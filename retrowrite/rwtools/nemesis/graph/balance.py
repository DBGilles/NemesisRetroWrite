####################################################################
# Various functions related to (sub)trees composed of NemesisNodes #
####################################################################

import copy
from itertools import zip_longest

# algoritmes robust
from rwtools.nemesis.graph.nemesis_node import NemesisNode

# TODO: overal asserts toevoegen om na te gaan of aan alle voorwaarden wel bepaald wordt -- maak
from rwtools.nemesis.graph.utils import is_leaf, get_balanced_tree_latencies, \
    add_latencies_as_descendants, replace_latencies_descendants


def balance_node_latencies(graph, n1, n2):
    # balance the latencies contained in two nodes (leaves)

    n1_c = n1
    n2_c = n2
    i = 0
    while True:
        if i >= len(n1_c) and i >= len(n2_c):
            break

        if n1_c.get(i) == n2_c.get(i):
            # equal latencies -- skip
            i += 1
        else:
            # unequal latencies, add latency of the longer branche to the shorter one
            longer = max(n1_c, n2_c)
            shorter = n1_c if longer == n2_c else n2_c

            # get the latency from the longer one, add it to the shorter one
            target_latency = longer[i]
            shorter.insert(i, target_latency)

            i += 1


def balance_node_tree_latencies(graph, leaf, tree):
    # balance a subtree and a node
    balance_branching_point(graph, tree)  # recursively balance the tree

    # then balance the root of the tree and the leaf (luckily the tree is actually represented
    # by root)
    balance_node_latencies(graph, leaf, tree)
    # TODO: verify that tree was correctly balanced

    # Because the tree is balanced,you can take any path from the root to a leaf and simply
    # copy over the latencies
    target_latencies = get_balanced_tree_latencies(graph, tree)

    # now, insert the target latencies into new nodes that are descendants of the leaf
    add_latencies_as_descendants(graph, leaf, target_latencies)


def balance_branching_point(graph, node):
    successors = list(graph.successors(node))
    assert (len(successors) == 2)  # if not two, do someting special
    child1, child2 = successors

    # determine if the children are laeves or non-leaves (i.e. subtrees
    nodes_are_leaves = [is_leaf(graph, n) for n in successors]

    if False not in nodes_are_leaves:
        # both nodes are leaves if all values are true <=> no values are false
        balance_node_latencies(graph, child1, child2)
    elif True not in nodes_are_leaves:
        # both nodes are trees if all values are false <=> no value are true
        balance_tree_latencies(graph, child1, child2)
    else:
        if nodes_are_leaves[0] == True:
            leaf = child1
            tree = child2
        else:
            leaf = child2
            tree = child1
        balance_node_tree_latencies(graph, leaf, tree)


def balance_latency_lists(latencies1, latencies2):
    # create a deecopy of the two lists (we dont want to modify the originals)
    latencies1 = copy.deepcopy(latencies1)
    latencies2 = copy.deepcopy(latencies2)
    target_latencies = []
    for a, b, in zip_longest(latencies1, latencies2, fillvalue=[]):
        if len(a) == 0:
            target_latencies.append(b)
        elif len(b) == 0:
            target_latencies.append(a)
        else:
            # merge the two in the same way you would balance two nodes
            i = 0
            while True:
                if i >= len(a) and i >= len(b):
                    break

                if a[min(i, len(a) - 1)] == b[min(i, len(b) - 1)]:
                    # equal latencies -- skip
                    i += 1
                else:
                    # unequal latencies, add latency of the longer branche to the shorter one
                    longer = max(a, b, key=lambda x: sum(x))
                    shorter = a if longer == b else b

                    # get the latency from the longer one, add it to the shorter one
                    target_latency = longer[i]
                    shorter.insert(i, target_latency)

                    i += 1
            assert (a == b)
            target_latencies.append(a)
    return target_latencies


def balance_tree_latencies(graph, tree1, tree2):
    # balance two subtrees

    # first balance the two trees seperately
    balance_branching_point(graph, tree1)
    balance_branching_point(graph, tree2)

    # then balance the roots
    balance_node_latencies(graph, tree1, tree2)

    # then get the latencies from root to leaf for both subtrees
    latencies1 = get_balanced_tree_latencies(graph, tree1)
    latencies2 = get_balanced_tree_latencies(graph, tree2)

    # insert these latencies into BOTH trees, following a balancing approach similar to the one
    # when balancing nodes (except seperate by level)
    # first determine optimal interlacing of latencies, and then add these where neccessary? (
    # i.e. assign them)

    target_latencies = balance_latency_lists(latencies1, latencies2)

    # recursively asssign these latencies to each of the trees (not including the root)
    replace_latencies_descendants(graph, tree1, target_latencies)
    replace_latencies_descendants(graph, tree2, target_latencies)



