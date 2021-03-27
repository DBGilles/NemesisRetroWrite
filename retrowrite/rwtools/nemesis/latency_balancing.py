# Collection of functions that are responsible for
# 1) balancing latency lists, taking into account how instructions are inserted
# 2) mapping balanced latency lists to a new sequence of instructions (given the old sequence of
#    sequence of instructions

import copy
import os

from rwtools.nemesis.nop_instructions import get_nop_instruction, get_nop_sequence, \
    map_latency_sequence_to_instructions


def num_inserted_instructions(target_latency):
    instr, registers = get_nop_instruction(target_latency)
    return 1 + 4 * len(registers)


def options_for_latency(target_latency):
    instr, registers = get_nop_instruction(target_latency)
    if len(registers) == 0:
        return [1]
    else:
        return [4 + len(registers), 4]


def head_length(list, value):
    eq = [elem == value for elem in list]
    if False not in eq:
        return len(list)
    if True not in eq:
        return 0
    else:
        return eq.index(False)

def reachable(current_head, candidate, options):
    diff = candidate - current_head
    if diff < 0:
        return False
    else:
        return True in [diff % option == 0 for option in options]

def determine_head_length(longer_head, shorter_head, options):
    # calculate how many instructions that need to be added to balance the two, given
    # that we can only insert a number of instructions if it is found in options
    # if the two values are equal we don't need to add anything
    if longer_head == shorter_head:
        return longer_head

    options = sorted(options)
    i = 1
    while True:
        for option in options:
            candidate = i*option
            if reachable(longer_head, candidate, options) and reachable(shorter_head, candidate, options):
                return candidate
        if i > 100:
            raise RuntimeError("Probably something wrong here")
        i += 1


def balance_node_latency_lists(latencies_a, latencies_b):
    output_latencies = []
    latencies_a = copy.deepcopy(latencies_a)
    latencies_b = copy.deepcopy(latencies_b)

    # determine which list is longer
    longer = latencies_a if len(latencies_a) > len(latencies_b) else latencies_b
    shorter = latencies_a if longer == latencies_b else latencies_b

    # look at the latency of the longer list, look at how many instructions possibly
    # will be inserted
    if len(longer) == 0:
        return output_latencies
    target_latency = longer[0]

    longer_head_length = head_length(longer, target_latency)
    shorter_head_length = head_length(shorter, target_latency)

    target_head_length = determine_head_length(longer_head_length,
                                               shorter_head_length,
                                               options_for_latency(target_latency))

    # insert however many you need to insert to get to this target
    shorter = (target_head_length - shorter_head_length) * [target_latency] + shorter
    longer = (target_head_length - longer_head_length) * [target_latency] + longer

    # add to output latencies
    output_latencies = longer[:target_head_length]
    output_latencies += balance_node_latency_lists(shorter[target_head_length:],
                                               longer[target_head_length:])

    return output_latencies


def flatten_sublists(input_list):
    out = []
    for elem in input_list:
        if isinstance(elem, list):
            out += elem
        else:
            out.append(elem)
    return out


def compute_missing_latencies(current_sequence, target_sequence):
    output = []

    if current_sequence == target_sequence:
        return []
    # cut off the common prefix
    common_prefix_length = len(os.path.commonprefix([current_sequence, target_sequence]))
    current_postfix = current_sequence[common_prefix_length:]
    target_postfix = target_sequence[common_prefix_length:]

    if len(current_postfix) == 0:
        if len(target_postfix) > 0:
            # determine how many times the value repeats in the target value
            # determine the length of the 'head' (values that are the same), add that to output
            n = head_length(target_postfix, target_postfix[0])
            new_section = target_postfix[:n]
            output.append((new_section, common_prefix_length))
        else:
            # should only occur when current_sequence == target-sequence
            return []
    else:
        # get the first value in current sequence
        first_val = current_postfix[0]
        # get the index of the first occurence of this value in the target sequence
        first_occurence = target_postfix.index(first_val)
        new_section = target_postfix[:first_occurence]
        output.append((new_section, common_prefix_length))

    # create the update sequence to recursively call the function
    updated_current_sequence = copy.deepcopy(current_sequence)
    updated_current_sequence.insert(common_prefix_length, new_section)
    updated_current_sequence = flatten_sublists(updated_current_sequence)

    x = compute_missing_latencies(updated_current_sequence, target_sequence)
    return output + x


def create_new_instruction_sequence(instructions, target_latencies):
    output = copy.deepcopy(instructions)
    # first determine what latencies are missing
    current_latencies = [instr[1] for instr in instructions]
    missing_latencies = compute_missing_latencies(current_latencies, target_latencies)
    for latency_sequence, index in missing_latencies:
        # map the latency sequence to a sequence of actual instructions
        instructions = map_latency_sequence_to_instructions(latency_sequence)
        instructions = list(zip(instructions, latency_sequence))

        # check what kind of instruction is currently at the index. If it is a
        # jmp or return, insert the instruction sequence right before the jump or return
        if index > 0:
            if 'ret' in output[index - 1][0] or 'jmp' in output[index - 1][0]:
                index -= 1
        output.insert(index, instructions)
        output = flatten_sublists(output)
    return output
