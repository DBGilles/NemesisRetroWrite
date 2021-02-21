##########################################################
# Utility functions functions for modifying and querying #
# leafs and (sub)trees composed of NemesisNodes          #
##########################################################
from rwtools.nemesis.graph.nemesis_node import AbstractNemesisNode


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
        latencies.append(curr_node.latencies)
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
            s.latencies = latencies[0]
    else:
        # no sucessors, add new nodes with the given latency
        new_node = AbstractNemesisNode(latencies[0], f"{root.id}{1}")
        graph.add_node(new_node)
        graph.add_edge(root, new_node)
    for s in successors:
        replace_latencies_descendants(graph, s, latencies[1:])
    return


def get_root(graph, nodes):
    # return the first nodes that has in degree 0 (assuming that there is only one such node,
    # this is the root
    for node in nodes:
        if graph.in_degree[node] == 0:
            return node
