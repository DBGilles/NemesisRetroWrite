########################################################
# Various functions for balancing a Control Flow Graph #
########################################################

import copy
from rwtools.nemesis.latency_balancing import balance_node_latency_lists, \
    create_new_instruction_sequence


def balance_branching_point(cfg, node):
    successors = list(cfg.get_successors(node))
    if len(successors) == 0:
        return
    if len(successors) == 1:
        # don't need to do anything?
        # return
        balance_branching_point(cfg, successors[0])  # TODO: check of dit klopt ??
        return
    assert (len(successors) == 2)  # if not two, do someting special
    child1, child2 = successors

    # determine if the children are laeves or non-leaves (i.e. subtrees)
    nodes_are_leaves = [cfg.is_leaf(n) for n in successors]
    if False not in nodes_are_leaves:
        # both nodes are leaves if all values are true <=> no values are false
        balance_node_latencies(child1, child2)
    elif True not in nodes_are_leaves:
        # both nodes are trees if all values are false <=> no value are true
        balance_tree_latencies(cfg, child1, child2)
    else:
        if nodes_are_leaves[0]:
            leaf = child1
            tree = child2
        else:
            leaf = child2
            tree = child1
        balance_node_tree_latencies(cfg, leaf, tree)

def balance_node_latencies(n1, n2):
    n1_latencies = n1.get_latencies()
    n2_latencies = n2.get_latencies()

    # determine the set of latencies for a balanced node
    balanced_latencies = balance_node_latency_lists(n1_latencies, n2_latencies)

    # for both nodes, determine a new sequence of instructions and replace the current sequence
    new_instructions_n1 = create_new_instruction_sequence(instructions=n1.get_instructions_with_latencies(),
                                                          target_latencies=balanced_latencies)
    n1.replace_instructions(new_instructions_n1)

    new_instructions_n2 = create_new_instruction_sequence(instructions=n2.get_instructions_with_latencies(),
                                                          target_latencies=balanced_latencies)
    n2.replace_instructions(new_instructions_n2)

def balance_node_tree_latencies(cfg, leaf, tree):
    # balance a subtree and a node
    balance_branching_point(cfg, tree)  # recursively balance the tree

    # then balance the root of the tree and the leaf (luckily the tree is actually represented
    # by root)
    balance_node_latencies(leaf, tree)
    # TODO: verify that tree was correctly balanced

    # Because the tree is balanced,you can take any path from the root to a leaf and simply
    # copy over the latencies
    target_latencies = cfg.get_balanced_tree_latencies(tree)

    # now, insert the target latencies into new nodes that are descendants of the leaf
    cfg.add_latencies_as_descendants(leaf, target_latencies)

def balance_latency_lists(tree1_lats, tree2_lats):
    latencies_1 = copy.deepcopy(tree1_lats)
    latencies_2 = copy.deepcopy(tree2_lats)
    target_latencies = []
    for a, b in zip(latencies_1, latencies_2):
        print(a, b)
        balanced_latencies = balance_node_latency_lists(a, b)
        target_latencies.append(balanced_latencies)
    return target_latencies

def balance_tree_latencies(cfg, tree1, tree2):
    # balance two subtrees
    # 1) first balance the two trees independently
    balance_branching_point(cfg, tree1)
    balance_branching_point(cfg, tree2)

    # then balance the root nodes
    balance_node_latencies(tree1, tree2)

    # at this point the nodes are balanced, and the seperate trees.
    # balance the entire tree by balancing the left subtree and the right subtreee
    # because both subtrees are balanced we can simply treat them as a list of latencies
    # (for determining a balanced latency list)
    latencies1 = cfg.get_balanced_tree_latencies(tree1)
    latencies2 = cfg.get_balanced_tree_latencies(tree2)

    return
    if latencies1 == latencies2:
        # latencies are already equal, no need to balance
        return

    # insert these latencies into BOTH trees, following a balancing approach similar to the one
    # when balancing nodes (except seperate by level)
    # first determine optimal interlacing of latencies, and then add these where neccessary?
    # (i.e. assign them)
    target_latencies = balance_latency_lists(latencies1, latencies2)

    print(target_latencies)

    return
    # recursively asssign these latencies to each of the trees (not including the root)
    cfg.replace_latencies_descendants(tree1, target_latencies)
    cfg.replace_latencies_descendants(tree2, target_latencies)
#
# def balance_tree_latencies_v2(cfg, tree1, tree2):
#     # balance two subtrees
#     # 1) first balance the two trees independently
#     balance_branching_point(cfg, tree1)
#     balance_branching_point(cfg, tree2)
#
#     # then balance the root nodes
#     balance_node_latencies(tree1, tree2)
