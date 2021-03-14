from collections import defaultdict

from rwtools.nemesis.graph.balance import balance_branching_point
from rwtools.nemesis.graph.nemesis_node import NemesisNode
import networkx as nx

from rwtools.nemesis.graph.utils import get_root

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
    def __init__(self, nodes, graph):
        self.nodes = nodes
        self.graph = graph

    def merge_consecutive_nodes(self):
        # get in and out degrees for all nodes that belong to this function
        current_node = get_root(self.graph)
        marked = []  # keep track of the ndoes we have already visited
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
                    marked.append(current_node)
            if out_d == 1:
                # we can merge this node into the next node
                # iff the next node has in degree == 1 and the node has not been visited yet(?)
                next_node = next(self.graph.neighbors(current_node))
                if next_node in marked:
                    if len(branches) == 0:
                        break
                    current_node = branches[0]
                    branches.remove(current_node)
                    marked.append(current_node)
                elif self.graph.in_degree[next_node] > 1:
                    branches.append(next_node)
                    current_node = branches[0]
                    branches.remove(current_node)
                    marked.append(current_node)
                else:
                    # actually merge the two nodes
                    # 1) add instructions
                    current_node.append_node(next_node)

                    # 2) add edge from all neighbors of next_node
                    for neighbor in self.graph.neighbors(next_node):
                        self.graph.add_edge(current_node, neighbor)

                    # 3) remove node from graph (also removes edges) and from list of nodes
                    self.graph.remove_node(next_node)
                    self.nodes.remove(next_node)
                    # marked.remove(next_node)
            elif out_d > 1:
                branches += [n for n in self.graph.neighbors(current_node) if n not in marked]
                if len(branches) == 0:
                    break
                current_node = branches[0]
                branches.remove(current_node)
                marked.append(current_node)

    def balance_branching_node(self, label):
        # iterate over all nodes, find the node with the given label
        target_node = None
        for node in self.graph.nodes:
            if node.id == label:
                target_node = node
                break
        balance_branching_point(self.graph, target_node)
