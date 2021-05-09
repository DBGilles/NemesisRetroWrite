from collections import defaultdict

from rwtools.nemesis.graph.utils import single_source_longest_dag_path_length
from rwtools.nemesis.latency_map.latency_map import LatencyMapV2

import networkx as nx

from librw.loader import Loader
from librw.rw import Rewriter
from rwtools.nemesis.graph.control_flow_graph import ControlFlowGraph
from rwtools.nemesis.graph.nemesis_node import NemesisNode
from rwtools.nemesis.latency_map.latency_map import LatencyMapV2
from rwtools.nemesis.nemesistool import load_latency_map, GCC_FUNCTIONS
from networkx.algorithms.shortest_paths.generic import shortest_path_length


class NemesisEvaluateProgram:
    def __init__(self, binary, outputfile):
        self.binary = binary
        self.outputfile = outputfile
        self.loader = None
        self.functions = {}

        # setup
        self.loader = Loader(self.binary)
        assert (self.loader.is_pie() and not self.loader.is_stripped())

        # get a dictionary mapping function id's to a dictionary containing metadata  to
        flist = self.loader.flist_from_symtab()
        self.loader.load_functions(flist)  # load functions into the container

        slist = self.loader.slist_from_symtab()  # get a list of all sections (?)
        # load all data sections into container (sections for which lamda func returns true)
        self.loader.load_data_sections(slist, lambda x: x in Rewriter.DATASECTIONS)

        reloc_list = self.loader.reloc_list_from_symtab()  # get a list of relocations
        self.loader.load_relocations(reloc_list)

        global_list = self.loader.global_data_list_from_symtab()
        self.loader.load_globals_from_glist(global_list)

        self.loader.container.attach_loader(self.loader)
        # container is a class that contains dictionaries mapping sections to their attributes and
        # a bunch of function create a Rewriter with access to this container (i.e. with access to
        # information about the various sections)
        self.rw = Rewriter(self.loader.container, self.outputfile)
        self.rw.symbolize()
        flist = Loader(binary).flist_from_symtab()
        self.function_names = [value['name'] for key, value in flist.items() if
                               value['name'] not in GCC_FUNCTIONS]
        for fn in self.function_names:
            print(fn)
            self.functions[fn] = NemesisEvaluateFunction(self.loader, fn)

    def evaluate_program(self, target_instructions):
        for fn in self.function_names:
            evaluator = self.functions[fn]
            evaluator.run_evaluation(target_instructions)



class NemesisEvaluateFunction:
    def __init__(self, loader, target_function):
        self.loader = loader
        self.cfg = None
        # load the binary, create writer etc.
        self.free_registers = {}
        self.clobber_registers = []
        self.selected_clobber = None
        self.clobber_instrumented = False
        self.leaves = None
        self.latency_mapper = LatencyMapV2(load_latency_map(
            "/home/gilles/git-repos/NemesisRetroWrite/retrowrite/rwtools/nemesis/latency_map"
            "/latencies.p"))
        self.target_nodes = None
        self.target_function = target_function
        self.create_cfg()

    def render_cfg(self):
        return self.cfg.to_img()

    def traverse_region(self, region, root, start_depth):
        result = []
        depth = start_depth
        for instruction_wrapper, latencies in zip(root.instruction_wrappers, root.latencies):
            latency = latencies[0]
            result.append((str(instruction_wrapper), latency, depth))
            depth += 1
            # create a dictionary mapping each depth all the instructions present at that depth

        for succ in region.successors(root):
            result += self.traverse_region(region, succ, depth)

        return result

    def create_cfg(self):
        # TODO: duplicated from nemesisInstrument class (nemesistool.py)
        """
        Create an initial control flow graph based on the given RetroWrite container
        """
        nodes = []
        graph = nx.DiGraph()

        target_fn = None
        for _, fn in self.loader.container.functions.items():
            if fn.name == self.target_function:
                target_fn = fn

        if target_fn is None:
            raise ValueError(f"Funtion with name {self.target_function} not found")

        # the cache contains a number of InstructionWrappers. these contain an instruction
        # as well as some extra information (mnemonic, location ,etc. ) create the initial
        # list of length 1 sequences by iterating over these
        for instr in target_fn.cache:
            # instr is an instance of class librw.container.InstructionWrapper
            instr_latency = self.latency_mapper.get_latency(instr.mnemonic, instr.op_str)
            nodes.append(NemesisNode(instr, instr_latency))
            # nodes[fn.name].append(NemesisNode(instr))
        graph.add_nodes_from(nodes)

        # add branching information to the sequences
        for cache_i, next_is in target_fn.nexts.items():
            node = nodes[cache_i]
            for i in next_is:
                if isinstance(i, int):
                    next_node = nodes[i]
                    graph.add_edge(node, next_node)

        self.cfg = ControlFlowGraph(graph=graph)
        self.cfg.merge_consecutive_nodes()
        self.leaves = self.cfg.get_leaves()

    def depth_mapping(self, region, root):
        instructions = defaultdict(list)
        for (instr, latency, depth) in self.traverse_region(region, root, 0):
            instructions[depth].append((instr, latency))
        return instructions

    def run_evaluation(self, target_instructions):
        target_nodes = []
        ok = True
        for instr in target_instructions:
            node = self.cfg.get_instruction_node(str(instr))
            if node is not None:
                target_nodes.append(node)
        if len(target_nodes) == 0:
            return
        elif len(target_nodes) > 1:
            raise NotImplementedError("not sure what to do here")
        target_node = target_nodes[0]

        self.cfg.unwind_graph()

        subgraph = self.cfg.subgraph(target_node)
        successors = list(subgraph.successors(target_node))
        path_lengths = shortest_path_length(subgraph, target_node)

        then_region = sorted(
            list(nx.descendants(subgraph, successors[0]) | {successors[0]}),
            key=lambda x: path_lengths[x],
            reverse=True)

        else_region = sorted(
            list(nx.descendants(subgraph, successors[1]) | {successors[1]}),
            key=lambda x: path_lengths[x],
            reverse=True)

        then_region_depth = max(
            single_source_longest_dag_path_length(subgraph.subgraph(then_region),
                                                  successors[0]).values())
        else_region_depth = max(
            single_source_longest_dag_path_length(subgraph.subgraph(else_region),
                                                  successors[1]).values())

        if then_region_depth != else_region_depth:
            ok = False
            print("WARNING -- not valanced bla bla bla")

        then_instruction = self.depth_mapping(subgraph.subgraph(then_region), successors[0])
        else_instruction = self.depth_mapping(subgraph.subgraph(else_region), successors[1])
        for i in range(max(then_instruction.keys() | else_instruction.keys())):
            if len(then_instruction[i]) == 0 or len(else_instruction[i]) == 0:
                print(f"not balanced at f{i}")
                ok = False

            else:
                instructions = then_instruction[i] + else_instruction[i]
                latencies = [lat for _, lat in instructions]
                if len(set(latencies)) > 1:
                    print("not balanced ")
                    print(instructions)
                    ok = False

        self.cfg.restore_cycles()
        if ok:
            print("no issues found")
