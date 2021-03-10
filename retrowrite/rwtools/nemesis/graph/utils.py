##########################################################
# Utility functions functions for modifying and querying #
# leafs and (sub)trees composed of NemesisNodes          #
##########################################################
import copy
import os
from collections import defaultdict
import networkx as nx
import matplotlib.image as mpimg
from networkx.algorithms.cycles import simple_cycles
from rwtools.nemesis.graph.nemesis_node import AbstractNemesisNode, NemesisNode
from networkx.algorithms.simple_paths import all_simple_paths, all_simple_edge_paths
import random

from rwtools.nemesis.nemesistool import GCC_FUNCTIONS

random.seed(10)


def to_img(graph, out_dir= "image", name="temp"):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_file = os.path.abspath(f"./{out_dir}/{name}.dot")
    nx.drawing.nx_agraph.write_dot(graph, out_file)
    cmd = f"dot -Tpng {out_file} -o {name}.png"
    os.system(cmd)
    img = mpimg.imread(f"{name}.png")
    return img


def is_leaf(graph, node):
    return graph.out_degree(node) == 0


def get_balanced_tree_latencies(graph, root):
    # get the latencies of a balanced subtree starting at the root down to a leaf do a depth
    # first traversal of the root, keeping track of the node latencies, until you reach a leaf
    curr_node = root
    latencies = []

    while True:
        # get the first child of the current node
        curr_node = list(graph.successors(curr_node))[0]
        latencies += curr_node.latencies
        if is_leaf(graph, curr_node):
            break
    return latencies


def add_latencies_as_descendants(graph, leaf, latencies):
    parent_node = leaf
    i = 0
    for lat in latencies:
        # lat is a list of latencies that belong in a single node
        # create a new node, add it to the graph, add edge from prev node to this node
        new_node = AbstractNemesisNode(lat, f"{parent_node.id}{i}")
        graph.add_node(new_node)
        graph.add_edge(parent_node, new_node)

        parent_node = new_node
        i += 1


def replace_latencies_descendants(graph, root, latencies):
    # get the successors of this node, add the first latency in the list of latencies to both
    # recursively add to both children

    if len(latencies) == 0:
        return

    successors = list(graph.successors(root))
    if len(successors) > 0:
        for s in successors:
            s.latencies[0] = latencies[0]  # TODD: deze lijn checken
    else:
        # no sucessors, add new nodes with the given latency
        new_node = AbstractNemesisNode(latencies[0], f"{root.id}{1}")
        graph.add_node(new_node)
        graph.add_edge(root, new_node)
    for s in successors:
        replace_latencies_descendants(graph, s, latencies[1:])
    return


def get_root(graph):
    # return the first nodes that has in degree 0 (assuming that there is only one such node,
    # this is the root
    for node in graph.nodes:
        if graph.in_degree[node] == 0:
            return node


def get_candidate_edges(path, longest_path):
    return set(path).difference(longest_path)


def sort_edge(e1, e2):
    from1, to1 = e1
    from2, to2 = e2
    if from1 > from2:
        return True
    elif to1 >= to2:
        return True


def equalize_path_lengths(graph, root, node):
    # equalize all path lenghts to the given node
    # path length is defined as the number of nodes from the root to the target node
    paths = list(all_simple_edge_paths(graph, root, node))

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
            graph.add_node(new_node)
            # add edge from second to last node  new node, from new node to last in path
            graph.add_edge(from_node, new_node)
            graph.add_edge(new_node, to_node)

            # remove edge from first in path to second in path
            graph.remove_edge(from_node, to_node)

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


def single_source_longest_dag_path_length(graph, s):
    assert (graph.in_degree(s) == 0)
    dist = defaultdict(lambda: -1)
    dist[s] = 0
    topo_order = nx.topological_sort(graph)
    for n in topo_order:
        for s in graph.successors(n):
            if dist[s] < dist[n] + 1:
                dist[s] = dist[n] + 1
    return dist


def insert_nodes(graph):
    root = get_root(graph)
    longest_path_lengths = single_source_longest_dag_path_length(graph, root)

    all_distances = sorted(list(set(longest_path_lengths.values())), reverse=True)
    largest_d = all_distances[0]
    largest_d_nodes = [n for n in graph.nodes if longest_path_lengths[n] == largest_d]

    for d in all_distances:
        if d == largest_d:
            continue
        d_smaller_nodes = [n for n in graph.nodes if longest_path_lengths[n] == d]

        for smaller_node in d_smaller_nodes:
            for larger_node in largest_d_nodes:
                equalize_path_lengths(graph, smaller_node, larger_node)


def get_node_depth(graph, root, node):
    longest_pathlength = -1
    for path in all_simple_paths(graph, root, node):
        longest_pathlength = max(longest_pathlength, len(path))
    return longest_pathlength


def unwind_graph(graph, root = None):
    # 1) first determine which edges to remove (keep track of tuples of node)
    # 2) remove the nodes

    cyclic_edges = []
    if root is None:
        root = get_root(graph)
    # step 1: determine which edges to remove by first finding cycles and then removing the edge
    # that goes from the deepest node to the most shallow node
    cycles = simple_cycles(graph)
    for cycle in cycles:
        depths = [get_node_depth(graph, root, node) for node in cycle]

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
        graph.remove_edge(last_node, first_node)

        # add a copy of the first node as a child of the last node
        new_node = copy.deepcopy(first_node)
        new_node.id = new_node.id + f"_{random.randint(0, 100)}"
        node_copies[first_node].append(new_node)
        # new_node.mapped_node = first_node
        graph.add_node(new_node)
        graph.add_edge(last_node, new_node)

    # add to each newly created node as as mapped node
    # 1) the original node it is a copy of
    # 2) all other copies of that original node
    for node, copies in node_copies.items():
        for c in copies:
            c.mapped_nodes = [node] + copies


def restore_cycles(graph):
    mapped_nodes = []
    root = get_root(graph)
    for node in graph.nodes:
        # get the nodes children
        children = graph.successors(node)
        for child in children:
            if child.mapped_nodes is not None:
                mapped_nodes.append((child, node))

    for mapped_node, parent in mapped_nodes:
        graph.remove_node(mapped_node)
        graph.add_edge(parent, mapped_node.mapped_nodes[0])

    remove_nodes = []
    for node in graph.nodes:
        if node == root:
            continue
        try:
            next(all_simple_paths(graph, root, node))
        except StopIteration:
            remove_nodes.append(node)

    for node in remove_nodes:
        graph.remove_node(node)

def create_graph_structure(rwcontainer, func_name):
    """
    Create an initial control flow graph based on the given RetroWrite container
    """
    nodes = []
    graph = nx.DiGraph()

    target_fn = None
    for _, fn in rwcontainer.functions.items():
        if fn.name == func_name:
            target_fn = fn

    if target_fn is None:
        raise ValueError(f"Funtion with name {func_name} not found")

    # the cache contains a number of InstructionWrappers. these contain an instruction
    # as well as some extra information (mnemonic, location ,etc. ) create the initial
    # list of length 1 sequences by iterating over these
    for instr in target_fn.cache:
        # instr is an instance of class librw.container.InstructionWrapper
        nodes.append(NemesisNode(instr))
        # nodes[fn.name].append(NemesisNode(instr))
    graph.add_nodes_from(nodes)

    # add branching information to the sequences
    for cache_i, next_is in target_fn.nexts.items():
        node = nodes[cache_i]
        for i in next_is:
            if isinstance(i, int):
                next_node = nodes[i]
                graph.add_edge(node, next_node)

    return nodes, graph