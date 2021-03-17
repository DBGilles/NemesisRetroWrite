import copy
from collections import defaultdict

from rwtools.nemesis.graph.abstract_nemesis_node import AbstractNemesisNode
from rwtools.nemesis.graph.balance import balance_branching_point
from rwtools.nemesis.graph.nemesis_node import NemesisNode
import networkx as nx
from networkx.algorithms.simple_paths import all_simple_paths, all_simple_edge_paths
from networkx.algorithms.cycles import simple_cycles
import random
random.seed(10)

from rwtools.nemesis.graph.utils import get_root, get_candidate_edges, \
    single_source_longest_dag_path_length, get_node_depth, to_img, is_leaf

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
    """
    Wrapper class for modifying and querying networkx graph
    """
    def __init__(self, nodes, graph):
        self.nodes = nodes
        self.graph = graph

    def to_img(self):
        return to_img(self.graph)

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
        balance_branching_point(self, target_node)

    def add_latencies_as_descendants(self, leaf, latencies):
        # TODO: moet ook werken voor concrete nodes
        parent_node = leaf
        i = 0
        for lat in latencies:
            # lat is a list of latencies that belong in a single node
            # create a new node, add it to the graph, add edge from prev node to this node
            new_node = AbstractNemesisNode(lat, f"{parent_node.id}{i}")
            self.graph.add_node(new_node)
            self.graph.add_edge(parent_node, new_node)

            parent_node = new_node
            i += 1

    def replace_latencies_descendants(self, root, latencies):
        # TODO: moet ook werken voor concrete nodes
        # get the successors of this node, add the first latency in the list of latencies to both
        # recursively add to both children

        if len(latencies) == 0:
            return

        successors = list(self.graph.successors(root))
        if len(successors) > 0:
            for s in successors:
                s.latencies[0] = latencies[0]  # TODD: deze lijn checken
        else:
            # no sucessors, add new nodes with the given latency
            new_node = AbstractNemesisNode(latencies[0], f"{root.id}{1}")
            self.graph.add_node(new_node)
            self.graph.add_edge(root, new_node)
        for s in successors:
            self.replace_latencies_descendants(s, latencies[1:])
        return

    def equalize_path_lengths(self, root, node):
        # TODO: Moet ook werken voor conrete nodes
        # equalize all path lenghts to the given node
        # path length is defined as the number of nodes from the root to the target node
        paths = list(all_simple_edge_paths(self.graph, root, node))

        if len(paths) == 0:
            # there are not paths from root to node
            return

        longest_path = max(paths, key=lambda x: len(x))
        max_len = len(longest_path)

        counter = 0
        for i in range(len(paths)):
            p = paths[i]
            diff = max_len - len(p)
            if diff == 0:
                continue
            candidates = sorted(get_candidate_edges(p, longest_path),
                                key=lambda x: str(x[0].id) + str(x[1].id))
            unique_edge = candidates[0]
            from_node = unique_edge[0]
            to_node = unique_edge[1]

            for _ in range(diff):
                # create a new node
                new_node = AbstractNemesisNode([], f"{from_node.id}{to_node.id}")
                counter += 1

                # add it to graph
                self.graph.add_node(new_node)
                self.nodes.append(new_node)

                # add edge from second to last node  new node, from new node to last in path
                self.graph.add_edge(from_node, new_node)
                self.graph.add_edge(new_node, to_node)

                # remove edge from first in path to second in path
                self.graph.remove_edge(from_node, to_node)

                # update second_to_last
                for j in range(i + 1, len(paths)):
                    following_path = paths[j]
                    # following_path.remove((from_node, to_node))
                    edge = (from_node, to_node)
                    if edge in following_path:
                        edge_index = following_path.index(edge)
                        # first insert new edges at edge_index, edge_index+1, then remove old edge
                        following_path.insert(edge_index, (from_node, new_node))
                        following_path.insert(edge_index + 1, (new_node, to_node))
                        following_path.remove((from_node, to_node))
                from_node = new_node

    def restore_cycles(self):
        mapped_nodes = []
        root = get_root(self.graph)
        for node in self.graph.nodes:
            # get the nodes children
            children = self.graph.successors(node)
            for child in children:
                if child.mapped_nodes is not None:
                    mapped_nodes.append((child, node))

        for mapped_node, parent in mapped_nodes:
            self.graph.remove_node(mapped_node)
            self.graph.add_edge(parent, mapped_node.mapped_nodes[0])

        remove_nodes = []
        for node in self.graph.nodes:
            if node == root:
                continue
            try:
                next(all_simple_paths(self.graph, root, node))
            except StopIteration:
                remove_nodes.append(node)

        for node in remove_nodes:
            self.graph.remove_node(node)

    def insert_nodes(self):
        root = get_root(self.graph)
        longest_path_lengths = single_source_longest_dag_path_length(self.graph, root)

        all_distances = sorted(list(set(longest_path_lengths.values())), reverse=True)
        largest_d = all_distances[0]
        largest_d_nodes = [n for n in self.graph.nodes if longest_path_lengths[n] == largest_d]

        for d in all_distances:
            if d == largest_d:
                continue
            d_smaller_nodes = [n for n in self.graph.nodes if longest_path_lengths[n] == d]

            for smaller_node in d_smaller_nodes:
                for larger_node in largest_d_nodes:
                    self.equalize_path_lengths(smaller_node, larger_node)

    def unwind_graph(self, root=None):
        # 1) first determine which edges to remove (keep track of tuples of node)
        # 2) remove the nodes

        cyclic_edges = []
        if root is None:
            root = get_root(self.graph)
        # step 1: determine which edges to remove by first finding cycles and then removing the
        # edge that goes from the deepest node to the most shallow node
        cycles = simple_cycles(self.graph)
        for cycle in cycles:
            depths = [get_node_depth(self.graph, root, node) for node in cycle]

            deepest_index = depths.index(max(depths))
            shallow_index = depths.index(min(depths))
            assert (deepest_index + 1) % len(depths) == shallow_index
            # assert abs(deepest_index - shallow_index) == 1 or abs(deepest_index - shallow_index)

            cyclic_edges.append((cycle[deepest_index], cycle[shallow_index]))

        # step 2: given the target edges this step is really straightforward
        cyclic_edges = set(cyclic_edges)

        node_copies = defaultdict(list)
        for last_node, first_node in cyclic_edges:
            # remove the edge from the last node to the first node
            self.graph.remove_edge(last_node, first_node)

            # add a copy of the first node as a child of the last node
            # new_node = copy.deepcopy(first_node)
            new_node = copy.copy(first_node)
            new_node.id = new_node.id + f"_{random.randint(0, 100)}"
            node_copies[first_node].append(new_node)
            # new_node.mapped_node = first_node
            self.graph.add_node(new_node)
            self.graph.add_edge(last_node, new_node)

        # add to each newly created node as as mapped node
        # 1) the original node it is a copy of
        # 2) all other copies of that original node
        for node, copies in node_copies.items():
            for c in copies:
                c.mapped_nodes = [node] + copies

    def get_balanced_tree_latencies(self, subtree_root):
        # get the latencies of a balanced subtree starting at the root down to a leaf do a depth
        # first traversal of the root, keeping track of the node latencies, until you reach a leaf
        curr_node = subtree_root
        latencies = []

        while True:
            # get the first child of the current node
            curr_node = list(self.graph.successors(curr_node))[0]
            latencies += curr_node.latencies
            if is_leaf(self.graph, curr_node):
                break
        return latencies

    def is_leaf(self, node):
        return is_leaf(self.graph, node)

    def get_successors(self, node):
        return list(self.graph.successors(node))