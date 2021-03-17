####################################################################
# Various functions related to (sub)trees composed of NemesisNodes #
####################################################################

import copy
from itertools import zip_longest

# algoritmes robust
from rwtools.nemesis.graph.nemesis_node import AbstractNemesisNode

# TODO: overal asserts toevoegen om na te gaan of aan alle voorwaarden wel bepaald wordt -- maak
from rwtools.nemesis.graph.utils import is_leaf, get_balanced_tree_latencies, \
    add_latencies_as_descendants, replace_latencies_descendants
from rwtools.nemesis.nop_insructions import get_nop_instruction


def balance_branching_point(graph, node):
    successors = list(graph.successors(node))
    print(f"balancing node {node.id}, with {len(successors)} children")
    if len(successors) == 0:
        return
    if len(successors) == 1:
        # don't need to do anything?
        # return
        balance_branching_point(graph, successors[0])  # TODO: check of dit klopt ??
        return
    assert (len(successors) == 2)  # if not two, do someting special
    child1, child2 = successors

    # determine if the children are laeves or non-leaves (i.e. subtrees)
    nodes_are_leaves = [is_leaf(graph, n) for n in successors]
    if False not in nodes_are_leaves:
        # both nodes are leaves if all values are true <=> no values are false
        balance_node_latencies(graph, child1, child2)
    elif True not in nodes_are_leaves:
        # both nodes are trees if all values are false <=> no value are true
        balance_tree_latencies(graph, child1, child2)
    else:
        if nodes_are_leaves[0]:
            leaf = child1
            tree = child2
        else:
            leaf = child2
            tree = child1
        balance_node_tree_latencies(graph, leaf, tree)


def copy_latencies_between_nodes(source, target):
    i = 0
    for sublist in source.latencies:
        for latency in sublist:
            target.insert(index=i, instruction="placeholder", latency=latency)
            i += 1


def balance_node_latencies(graph, n1, n2):
    # If either of the two nodes is empty, do something special
    if n1.num_instructions() == 0 and n2.num_instructions() == 0:
        raise RuntimeError("Not sure what to do here quite yet")
    elif n1.num_instructions() == 0:
        copy_latencies_between_nodes(n2, n1)
        return
    elif n2.num_instructions() == 0:
        copy_latencies_between_nodes(n1, n2)
        return

    # balance the latencies contained in two nodes (leaves)
    i = 0
    while True:
        if i >= n1.num_instructions() and i >= n2.num_instructions():
            break
        n1_lat = n1.get_latency(i) if i < n1.num_instructions() else n1.get_latency(-1)
        n2_lat = n2.get_latency(i) if i < n2.num_instructions() else n2.get_latency(-1)
        if n1_lat == n2_lat:
            # equal latencies -- skip
            i += 1
        else:
            # unequal latencies, add latency of the longer brancher to the shorter one
            longer = max(n1, n2)
            shorter = n1 if longer == n2 else n2

            # get the latency from the longer one, add it to the shorter one
            target_latency = longer.get_latency(i)

            # determine what instruction to use
            nop_instruction, mod_registers = get_nop_instruction(target_latency)
            if len(mod_registers) == 0:
                # simply insert the instruction at index i
                try:
                    shorter.insert(i, nop_instruction, target_latency)
                    i += 1
                except ValueError:
                    return
            elif len(mod_registers) == 1:
                # , the nop instruction to the shorter one,
                # and a pop instruction to both nodes
                reg = mod_registers[0]
                push_instr = f"pushq {reg}"
                pop_instr = f"popq {reg}"

                sp_dec_instr = f"sub $0x8, %rsp"
                sp_inc_instr = f"add $0x8, %rsp"
                longer.insert(i, sp_dec_instr, 3)
                shorter.insert(i, sp_dec_instr, 3)
                i += 1

                # add a push instruction to both nodes
                longer.insert(i, push_instr, 3)
                shorter.insert(i, push_instr, 3)

                # add the nop to the shorter one
                shorter.insert(i + 1, nop_instruction, target_latency)

                # identical) add the pop instruction to both nodes
                # problem and (hacky) solution. If the instruction we want to balance is a
                # jump, the pop wont be executed. in that case add the pop before the jump
                # (fortunately jump and pop are both 3 so to an attacker these cases are
                # identical)
                shorter.insert(i + 2, pop_instr, 3)
                shorter.insert(i + 3, sp_inc_instr, 3)

                instr = longer.get_instr_mnemonic(i + 1)
                if "jmp" in instr:
                    longer.insert(i + 1, pop_instr, 3)
                    longer.insert(i + 2, sp_inc_instr, 3)
                else:
                    longer.insert(i + 2, pop_instr, 3)
                    longer.insert(i + 3, sp_inc_instr, 3)
                i += 4
            else:
                raise NotImplementedError


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
                    # nop_instruction, mod_registers = get_nop_instruction(target_latency)

                    # return
                    shorter.insert(i, target_latency)

                    i += 1
            assert (a == b)
            target_latencies.append(a)
    return target_latencies


def balance_tree_latencies(graph, tree1, tree2):
    # balance two subtrees
    print(f"balancing trees {tree1.id}, {tree2.id}")

    # 1) first balance the two trees independently
    balance_branching_point(graph, tree1)
    balance_branching_point(graph, tree2)

    # then balance the root nodes
    balance_node_latencies(graph, tree1, tree2)

    # at this point the nodes are balanced, and the seperate trees.
    # balance the entire tree by balancing the left subtree and the right subtreee
    # because both subtrees are balanced we can simply treat them as a list of latencies
    # (for determining a balanced latency list)
    latencies1 = get_balanced_tree_latencies(graph, tree1)
    latencies2 = get_balanced_tree_latencies(graph, tree2)

    if latencies1 == latencies2:
        # latencies are already equal, no need to balance
        return

    # insert these latencies into BOTH trees, following a balancing approach similar to the one
    # when balancing nodes (except seperate by level)
    # first determine optimal interlacing of latencies, and then add these where neccessary?
    # (i.e. assign them)
    target_latencies = balance_latency_lists(latencies1, latencies2)

    # recursively asssign these latencies to each of the trees (not including the root)
    replace_latencies_descendants(graph, tree1, target_latencies)
    replace_latencies_descendants(graph, tree2, target_latencies)
