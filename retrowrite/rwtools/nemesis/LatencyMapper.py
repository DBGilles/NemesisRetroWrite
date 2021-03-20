import copy
import os
import pickle
import re

from rwtools.nemesis.op_types import map_assembly_values, BaseType
from rwtools.nemesis.string_matching import REGISTER_REGEX_STR, IMM_VALUES_REGEX_STR, \
    LABELS_REGEX, LABELS_REGEX_STR, RELATIVE_FROM_REGISTER_REGEX_STR, \
    LABEL_RELATIVE_FROM_REGISTER_STR, COMPOUND_OP_STR, RELATIVE_FROM_COMPOUND_OP, \
    RELATIVE_FROM_COMPOUND_OP_STR, COMPOUND_OP


# def split_operands(op_string): operands = list(filter(lambda x: len(x) > 0, map(lambda x:
# x.strip(), op_string.split(",")))) return operands


operand_regex_str = f"({REGISTER_REGEX_STR})|" \
                    f"({IMM_VALUES_REGEX_STR})|" \
                    f"({LABELS_REGEX_STR})|" \
                    f"{RELATIVE_FROM_REGISTER_REGEX_STR}|" \
                    f"{LABEL_RELATIVE_FROM_REGISTER_STR}|" \
                    f"{RELATIVE_FROM_COMPOUND_OP_STR}|" \
                    f"{COMPOUND_OP_STR}"

# \([%a-zA-Z0-9]+,[%a-zA-Z0-9]+(, [[%a-zA-Z0-9]+)? \)
operand_regex = re.compile(operand_regex_str, re.VERBOSE)  # set verbose for spaces in pattern

one_op_regex_str = f"{operand_regex_str}"
two_ops_regex_str = f"({operand_regex_str}), ({operand_regex_str})"

one_op_regex = re.compile(operand_regex_str)
two_ops_regex = re.compile(two_ops_regex_str)


def split_operands_v2(op_string):
    # first use the various regex to determine the structure of the operands (i.e. how many,
    # what form) given the form, split the string suitably. Ideally you could use the capture
    # groups, but because of the way the regexes are constructed this might be confusing
    op_string = op_string.strip()
    if len(op_string) == 0:
        return []
    if one_op_regex.fullmatch(op_string):
        return [op_string]
    elif two_ops_regex.fullmatch(op_string):
        if RELATIVE_FROM_COMPOUND_OP.search(op_string):
            # contains compound operation, take into account opening and closing parentheses
            # note: return a flat list with all ops or nested list?
            opening_paren = op_string.find("(")
            closing_paren = op_string.find(")")
            first_op = op_string[:opening_paren]
            compound_ops = op_string[opening_paren + 1:closing_paren].split(", ")
            last_op = op_string[closing_paren + 1:]
            if last_op[:2] == ', ':
                last_op = last_op[2:]
            operands = [first_op, compound_ops, last_op]
            return operands
        elif COMPOUND_OP.search(op_string):
            opening_paren = op_string.find("(")
            closing_paren = op_string.find(")")
            first_op = op_string[:opening_paren]
            compound_ops = op_string[opening_paren + 1:closing_paren].split(", ")
            last_op = op_string[closing_paren + 1:]
            if last_op[:2] == ', ':
                last_op = last_op[2:]
            if first_op[:2] == ', ':
                first_op = first_op[2:]
            operands = []
            if len(first_op) > 0:
                operands.append(first_op)
            operands.append(compound_ops)
            if len(last_op) > 0:
                operands.append(last_op)
            return operands
        else:
            return op_string.split(', ')
    elif "@" in op_string:
        return [op_string]
    else:
        print("unknown type:", op_string)
        raise ValueError


def all_present(target_ops, candidate_ops):
    """
    Return true if all of the ops in target_ops are found in candidate_ops, otherwise return False
    """
    candidate_copy = list(copy.deepcopy(candidate_ops))

    for target in target_ops:
        matched = False
        for candidate in candidate_copy:
            if target == candidate:
                candidate_copy.remove(candidate)
                matched = True
                break
        if not matched:
            return False
    return True


class LatencyMapper:
    """
    Wrapper for latency map
    """

    def __init__(self, latency_map):
        self.base_map = latency_map
        self.latency_map = {}
        for key, value in self.base_map.items():
            category = key[0]  # eg PUSH
            instruction = key[1]  # eg pushq
            operands = key[1:]
            if instruction not in self.latency_map.keys():
                self.latency_map[instruction] = {}

            k = key[1:]
            self.latency_map[instruction][k] = value

        # some special cases
        # (1) retq, equal to ret
        self.latency_map['retq'] = self.latency_map['ret']

    def get_latency(self, *args):
        instruction = args[0]

        # Some special cases
        if instruction == 'endbr64':
            # endbr64 signifies end of branch, but is essentially a NOP instruction
            return 0

        operands = split_operands_v2(args[1]) if len(args) > 1 else []
        # instruction contains the instruction as found in the assembly
        # operands contain the operands as found in assembly

        # dictionary mapping insruction + op_types to latency --
        # need to determine which is most suitable
        candidates = self.latency_map[instruction]

        # to match candidates, convert the supplied operands to types
        try:
            operand_types = [map_assembly_values(op) for op in operands]
        except ValueError as e:
            print(args[1])
            print(operands)
            raise e
        for x in operand_types:
            assert isinstance(x, BaseType)

        # if all candidates have the same latency (meaning latency is same regardless of
        # operand types), return that latency
        candidate_latencies = list(candidates.values())
        if len(set(candidate_latencies)) == 1:
            return candidate_latencies[0]

        # otherwise, loop over the candidates, get the best match (should be an identical match
        # really)
        for candidate in candidates:
            candidate_op_types = candidate[1:]
            # candidate_op_types = list(map(construct_type, candidate_op_types))

            if all_present(operand_types, candidate_op_types):
                return self.latency_map[instruction][candidate]

        print(f"Warning -- latency not found for instruction `{instruction}` "
              f"with operands {operands}")
        return 1

    def _map_to_type(self, op):
        if "(" in op and ")" in op:
            # operand is a location at an offset from some value -- return memory
            return "m"
        elif '%' in op:
            # register operand
            return "r"
        elif "$" in op:
            # immediate value
            return "i"
        elif ".L" in op:
            # label
            return "label"
        raise ValueError


def construct_latency_mapper(latency_if):
    with open(latency_if, 'rb') as fp:
        latency_map = pickle.load(fp)

    mapper = LatencyMapper(latency_map)
    return mapper
