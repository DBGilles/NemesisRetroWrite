from collections import defaultdict

from rwtools.nemesis.graph.nemesis_node import NemesisNode
import networkx as nx

from rwtools.nemesis.utils.graph_utils import get_root

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


class ControlFlowGraph:
    def __init__(self):
        self.nodes = defaultdict(list)
        self.graph = nx.DiGraph()

    def initialize_cfg(self, rwcontainer):
        """
        Create an initial control flow graph based on the given RetroWrite container
        """
        # first, iterate over each function that is not a GCC function, creating initial code
        # sequences of length 1
        for _, fn in filter(lambda x: x[1].name not in GCC_FUNCTIONS,
                            rwcontainer.functions.items()):
            # the cache contains a number of InstructionWrappers. these contain an instruction
            # as well as some extra information (mnemonic, location ,etc. ) create the initial
            # list of length 1 sequences by iterating over these
            for instr in fn.cache:
                # instr is an instance of class librw.container.InstructionWrapper
                self.nodes[fn.name].append(NemesisNode(instr))
            self.graph.add_nodes_from(self.nodes[fn.name])

            # add branching information to the sequences
            for cache_i, next_is in fn.nexts.items():
                node = self.nodes[fn.name][cache_i]
                for i in next_is:
                    if isinstance(i, int):
                        next_node = self.nodes[fn.name][i]
                        self.graph.add_edge(node, next_node)

    def merge_consecutive_nodes(self):
        """
        Merge consecutive nodes that are do not have incoming or outoing edges
        """
        for fn_name, fn_nodes in self.nodes.items():
            # get in and out degrees for all nodes that belong to this function
            current_node = get_root(self.graph, fn_nodes)
            branches = []
            while True:
                # get out degree current nodes
                out_d = self.graph.out_degree[current_node]
                if out_d == 0:
                    # current node is leaf
                    if len(branches) == 0:
                        break
                    else:
                        current_node = branches[0]
                        branches.remove(current_node)
                if out_d == 1:
                    # we can merge this node into the next node
                    # iff the next node has in degree == 1
                    next_node = self.graph.neighbors(current_node).__next__()
                    if self.graph.in_degree[next_node] > 1:
                        branches.append(next_node)
                        current_node = branches[0]
                        branches.remove(current_node)
                    else:
                        # actually merge the two nodes
                        # 1) add instructions
                        current_node.add_instructions(next_node.instructions)

                        # 2) add edge from all neighbors of next_node
                        for neighbor in self.graph.neighbors(next_node):
                            self.graph.add_edge(current_node, neighbor)

                        # 3) remove node (also removes all edges)
                        self.graph.remove_node(next_node)
                elif out_d > 1:
                    branches += [n for n in self.graph.neighbors(current_node)]
                    current_node = branches[0]
                    branches.remove(current_node)
