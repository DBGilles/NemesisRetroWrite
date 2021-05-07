import pickle
from enum import Enum

import networkx as nx

from librw.analysis.register import RegisterAnalysis
from librw.container import InstructionWrapper
from librw.loader import Loader
from librw.rw import Rewriter
from rwtools.nemesis.graph.control_flow_graph import ControlFlowGraph
from rwtools.nemesis.graph.nemesis_node import NemesisNode
from rwtools.nemesis.latency_map.latency_map import LatencyMapV2

GCC_FUNCTIONS = [
    "_start",
    "__libc_start_main",
    "__libc_csu_fini",
    "__libc_csu_init",
    "__lib_csu_fini",
    "_init",
    "__libc_init_first",
    "_fini",
    "_rtld_fini",
    "_exit",
    "__get_pc_think_bx",
    "__do_global_dtors_aux",
    "__gmon_start",
    "frame_dummy",
    "__do_global_ctors_aux",
    "__register_frame_info",
    "deregister_tm_clones",
    "register_tm_clones",
    "__do_global_dtors_aux",
    "__frame_dummy_init_array_entry",
    "__init_array_start",
    "__do_global_dtors_aux_fini_array_entry",
    "__init_array_end",
    "__stack_chk_fail",
    "__cxa_atexit",
    "__cxa_finalize",
]


class RegType(Enum):
    FREE = 1
    CLOBBER = 2


def get_nop_v2(target_lat):
    if target_lat == -2:
        return "", 0
    if target_lat == -1:
        return "jmp {}", 1
    if target_lat == 1:
        return "add $0, %rax", 0
    elif target_lat == 2:
        return "xadd {}, {}", 2
    elif target_lat == 3:
        return "imul {}, {}", 2
    elif target_lat == 4:
        return "mul {}, {}", 2
    elif target_lat == 5:
        return "movq -0x4(%rbp), {}", 1
    elif target_lat == 6:
        return "or -0x4(%rbp), {}", 1
    elif target_lat == 7:
        return "adc -0x4(%rbp), {}", 1
    else:
        raise RuntimeError

def register_filter(reg):
    if reg in ["rsp", "rbp", "rflags", "rsp"]:
        return False
    else:
        return True

def is_branch(mnemonic):
    branch_insn = ["jmp", "je", "jne", "jge"]
    return True in [inst in mnemonic for inst in branch_insn]


def load_latency_map(latency_file):
    with open(latency_file, 'rb') as fp:
        l_map = pickle.load(fp)
    return l_map


class NemesisInstrument:
    def __init__(self, binary, outputfile, target_function="main"):
        self.binary = binary
        self.outputfile = outputfile
        self.loader = None
        self.rw = None
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
        self.target_function = target_function
        self._setup()

    def _setup(self):
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

        # create control flow graph
        self.create_cfg()

        # do analysis
        self.do_analysis()

    def create_cfg(self):
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

    def do_analysis(self):
        # do analysis
        RegisterAnalysis.analyze(self.loader.container)

        # get analysis for current function only
        main_function = None
        for addr, function in self.loader.container.functions.items():
            if function.name == "main":
                main_function = function

        if main_function is None:
            raise RuntimeError("Can't find function 'main'")

        self.clobber_registers = list(main_function.analysis['clobber_registers'])

        self.free_registers = {}
        for idx, wrapper in enumerate(main_function.cache):
            self.free_registers[main_function.cache[idx]] = \
                main_function.analysis['free_registers'][idx]

    def render_cfg(self):
        return self.cfg.to_img()

    def dump(self):
        self.rw.dump()

    def _get_clobber_register(self):
        # If no register is selected yet, select one and insert push and pop instructions into
        # root, leaves
        if self.selected_clobber is None:
            self.selected_clobber = self.clobber_registers[0]

            # insert instruction at the start of the function that push the clobber
            # register
            root = self.cfg.get_root()
            push_instruction = f"pushq %{self.selected_clobber}"
            latency = self.latency_mapper.get_latency("pushq",
                                                      f"%{self.selected_clobber}")
            root.insert(0, push_instruction, latency)

            # insert instructions at function end that pop it
            # TODO: this won't work if cycles are removed (?)
            for leaf in self.leaves:
                n = leaf.num_instructions()
                pop_instruction = f"popq %{self.selected_clobber}"
                latency = self.latency_mapper.get_latency("popq",
                                                          f"%{self.selected_clobber}")
                leaf.insert(n - 1, pop_instruction, latency)

            self.clobber_instrumented = True

        return self.selected_clobber

    def _select_register(self, node, instruction_index):
        if instruction_index < node.num_instructions():
            instr_seq = node.get_sequence_of_instruction(instruction_index)
            if isinstance(instr_seq, InstructionWrapper):
                free_regs = list(filter(register_filter, self.free_registers[instr_seq]))
                if len(free_regs) > 0:
                    return free_regs[0], RegType.FREE
        return self._get_clobber_register(), RegType.CLOBBER

    def _select_candidate(self, candidates, it):
        reference_node = None
        if len(candidates) == 1:
            reference_node = candidates[0]
        else:
            for c in candidates:
                if c.get_instr_latency(it) != -1:
                    reference_node = c
                    break
        if reference_node is None:
            reference_node = candidates[0]
        return reference_node

    def _align_nodes(self, nodes):
        it = 0

        # keep track of the number of instructions in each node, update as the nodes are modified
        while True:
            node_lengths = {node: node.num_instructions() for node in nodes}

            if it >= max(node_lengths.values()):
                break

            # get all candidates nodes, select reference node from them
            candidates = [node for node in nodes if
                          node_lengths[node] == max(node_lengths.values())]
            reference_node = self._select_candidate(candidates, it)

            # get target latency from reference node
            target_lat = reference_node.get_instr_latency(it)
            dummy_instruction, n_args = get_nop_v2(target_lat)
            for node in [n for n in nodes if n != reference_node]:
                # if the current instruction in the node has the same latency,
                # no need to do anything
                if it < node_lengths[node] and node.get_instr_latency(it) == target_lat:
                    continue

                if target_lat == -1:
                    # instruction is a jump -- balance with another jump
                    node_successors = list(self.cfg.graph.successors(node))
                    # shouldn't be 0 , and if len(successors) > 2 there should already be a
                    # brancing instruction
                    if len(node_successors) != 1:
                        print(node.id)
                    assert len(node_successors) == 1
                    jump_target = node_successors[0].get_start_label()
                    node.insert(it, dummy_instruction.format(jump_target), target_lat)
                elif target_lat == -2:
                    # instruction is a call -- simply copy over (i.e. call same function)
                    instr = reference_node.get_instr_mnemonic(it)
                    node.insert(it, instr, -2)
                else:
                    # otherwise determine what to do
                    selected_register, reg_type = self._select_register(node, it)

                    reg = n_args * [f"%{selected_register}"]

                    # insert instruction into node
                    node.insert(it, dummy_instruction.format(*reg), target_lat)
            it += 1

    def align(self, node):
        subgraph = self.cfg.subgraph(node)
        # root = get_root(subraph)
        # tree_depths = nx.shortest_path_length(subraph, root)
        tree_depths = nx.shortest_path_length(subgraph, node)
        for i in range(max(tree_depths.values()) + 1):
            level_nodes = [node for node in subgraph.nodes if tree_depths[node] == i]
            self._align_nodes(level_nodes)

    def instrument(self, target_node):
        # 1. get rid of any cycles in the graph
        self.cfg.unwind_graph()

        # 2. insert nodes and equalize branches so that all
        #   paths to all leaves are same length -- stratified
        self.cfg.insert_nodes(target_node)
        self.cfg.equalize_branches(target_node)

        # 4. align the nodes
        self.align(target_node)

        # insert labels into newly created nodes that are branching targets
        self.cfg.insert_labels()

        # 5. merge inserted nodes
        self.cfg.merge_inserted_nodes()

        self.cfg.restore_cycles()
