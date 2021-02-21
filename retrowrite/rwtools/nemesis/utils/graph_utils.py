
def get_root(graph, nodes):
    # return the first nodes that has in degree 0 (assuming that there is only one such node,
    # this is the root
    for node in nodes:
        if graph.in_degree[node] == 0:
            return node
