from collections import defaultdict

from rwtools.nemesis.graph.abstract_nemesis_node import flatten
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


def mapping(cfg_a, cfg_b):
    visited_nodes = []
    next_nodes = []

    assert nx.is_isomorphic(cfg_a.graph, cfg_b.graph)
    mapping = {}

    node_a = cfg_a.get_root()
    node_b = cfg_b.get_root()

    mapping[node_a] = node_b

    while True:
        visited_nodes.append(node_a)
        succ_a = list(cfg_a.graph.successors(node_a))
        succ_b = list(cfg_b.graph.successors(node_b))
        assert len(succ_a) == len(succ_b)

        if len(succ_a) == 1:
            # both nodes only have one successor -- these need to be mapped to each other
            mapping[succ_a[0]] = succ_b[0]
            if succ_a[0] not in visited_nodes and succ_a[0] not in next_nodes:
                next_nodes.append(succ_a[0])
        elif len(succ_a) == 2:
            instr_a = node_a.instruction_wrappers[-1]
            instr_b = node_b.instruction_wrappers[-1]
            assert instr_a.mnemonic == instr_b.mnemonic
            target_a = instr_a.op_str
            target_b = instr_b.op_str

            # map the nodes that corresopnd to the targets of the branch
            node_a = list(filter(lambda n: n.get_start_label() == target_a, succ_a))[0]
            node_b = list(filter(lambda n: n.get_start_label() == target_b, succ_b))[0]
            mapping[node_a] = node_b

            # map the other nodes
            node_a = list(filter(lambda n: n.get_start_label() != target_a, succ_a))[0]
            node_b = list(filter(lambda n: n.get_start_label() != target_b, succ_b))[0]
            mapping[node_a] = node_b

            for s in succ_a:
                if s not in visited_nodes and s not in next_nodes:
                    next_nodes.append(s)
        if len(next_nodes) == 0:
            break
        node_a = next_nodes[0]
        next_nodes.remove(node_a)
        node_b = mapping[node_a]
        # go to next node, do the same (TODO)
    return mapping


def evaluate_runtime(orig_func, mod_func, target_node=None):
    if target_node is None:
        graph = orig_func.cfg.graph
    else:
        graph = orig_func.cfg.subgraph(target_node)

    # get mapping between nodes of the graphs
    node_mapping = mapping(orig_func.cfg, mod_func.cfg)

    results = []

    root = [node for node in graph.nodes if graph.in_degree[node] == 0][0]
    leaves = [node for node in graph.nodes if graph.out_degree[node] == 0]
    for leaf in leaves:
        # get all paths to the leaf, use the mapping to get corresponding paths in modified
        # program calculated difference between the two
        for path in nx.all_simple_paths(graph, root, leaf):
            corresponding_path = [node_mapping[node] for node in path]
            # filter out any latencies that are smaller than 0 (jumps and calls)
            orig_latencies = filter(lambda x: x > 0,
                                    flatten([node.get_latencies() for node in path]))
            mod_latencies = filter(lambda x: x > 0,
                                   flatten([node.get_latencies() for node in corresponding_path]))
            results.append((path, sum(orig_latencies), sum(mod_latencies)))
    return results


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
        self.cfg.unwind_graph()

        for target_node in target_nodes:
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
