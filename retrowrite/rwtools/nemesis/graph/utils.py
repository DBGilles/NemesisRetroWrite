import os
import random
from collections import defaultdict

import matplotlib.image as mpimg
import networkx as nx
from networkx.algorithms.simple_paths import all_simple_paths

from rwtools.nemesis.graph.nemesis_node import NemesisNode

random.seed(10)


def to_img(graph, out_dir="image", name="temp"):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_file = os.path.abspath(f"./{out_dir}/{name}.dot")
    nx.drawing.nx_agraph.write_dot(graph, out_file)
    cmd = f"dot -Tpng {out_file} -o {name}.png"
    os.system(cmd)
    img = mpimg.imread(f"{name}.png")
    return img

def sort_edge(e1, e2):
    from1, to1 = e1
    from2, to2 = e2
    if from1 > from2:
        return True
    elif to1 >= to2:
        return True


def single_source_longest_dag_path_length(graph, s):
    # assert (graph.in_degree(s) == 0)
    dist = defaultdict(lambda: -1)
    dist[s] = 0
    topo_order = nx.topological_sort(graph)
    for n in topo_order:
        for s in graph.successors(n):
            if dist[s] < dist[n] + 1:
                dist[s] = dist[n] + 1
    return dist


def get_node_depth(graph, root, node):
    longest_pathlength = -1
    for path in all_simple_paths(graph, root, node):
        longest_pathlength = max(longest_pathlength, len(path))
    return longest_pathlength


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
