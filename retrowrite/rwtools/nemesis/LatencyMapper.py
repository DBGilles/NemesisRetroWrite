import copy
import pickle
import re

from rwtools.nemesis.op_types import map_assembly_values, BaseType
from rwtools.nemesis.string_matching import REGISTER_REGEX_STR, IMM_VALUES_REGEX_STR, \
    LABELS_REGEX_STR, RELATIVE_FROM_REGISTER_REGEX_STR, \
    LABEL_RELATIVE_FROM_REGISTER_STR, COMPOUND_OP_STR, RELATIVE_FROM_COMPOUND_OP, \
    RELATIVE_FROM_COMPOUND_OP_STR, COMPOUND_OP, \
    JUMP_TARGET_STR

# def split_operands(op_string): operands = list(filter(lambda x: len(x) > 0, map(lambda x:
# x.strip(), op_string.split(",")))) return operands


operand_regex_str = f"({REGISTER_REGEX_STR})|" \
                    f"({IMM_VALUES_REGEX_STR})|" \
                    f"({LABELS_REGEX_STR})|" \
                    f"{RELATIVE_FROM_REGISTER_REGEX_STR}|" \
                    f"{LABEL_RELATIVE_FROM_REGISTER_STR}|" \
                    f"{RELATIVE_FROM_COMPOUND_OP_STR}|" \
                    f"{COMPOUND_OP_STR}|" \
                    f"{JUMP_TARGET_STR}"

# \([%a-zA-Z0-9]+,[%a-zA-Z0-9]+(, [[%a-zA-Z0-9]+)? \)
operand_regex = re.compile(operand_regex_str, re.VERBOSE)  # set verbose for spaces in pattern

one_op_regex_str = f"{operand_regex_str}"
two_ops_regex_str = f"({operand_regex_str}), ({operand_regex_str})"

one_op_regex = re.compile(operand_regex_str)
two_ops_regex = re.compile(two_ops_regex_str)

def _strip_operand(operand):
    # strip any non alphannumeric characters that may occur at start of operand and trailing
    # characters
    # TODO: should be able to use regex here
    if operand[:2] == ", ":
        operand = operand[2:]
    elif operand[0] == ",":
        operand = operand[1:]
    operand = operand.strip()
    return operand


def split_operands_v2(op_string):
    # first use the various regex to determine the structure of the operands (i.e. how many,
    # what form) given the form, split the string suitably. Ideally you could use the capture
    # groups, but because of the way the regexes are constructed this might be confusing
    op_string = op_string.strip()
    if len(op_string) == 0:
        return []
    if one_op_regex.fullmatch(op_string):
        if RELATIVE_FROM_COMPOUND_OP.match(op_string):
            closing_paren = op_string.find(")")
            operands = [op_string[:closing_paren+1]]
            return operands
        elif COMPOUND_OP.match(op_string):
            opening_paren = op_string.find("(")
            closing_paren = op_string.find(")")
            compound_ops = op_string[opening_paren + 1:closing_paren].split(", ")
            operands = [compound_ops]
            return operands
        else:
            return [op_string]
    elif two_ops_regex.fullmatch(op_string):
        # determine the index of the comma that seperates the two operands
        # if there is no compound op then this is simply the first comma. Otherwise, it
        # is the comma either before the compound op or after the compound op
        if (match := COMPOUND_OP.match(op_string)) or (
        match := RELATIVE_FROM_COMPOUND_OP.match(op_string)):
            # TODO: RELATIVE_FROM_COMPOUND_OP.match zou hier overbodig moeten zijn, toch?
            split_index = op_string.find(",", 0, match.start())
            if split_index == -1:
                split_index = op_string.find(",", match.end())
        else:
            split_index = op_string.find(",")
        assert split_index != -1
        first_op = op_string[:split_index]
        second_op = _strip_operand(op_string[split_index:])

        # first_ops = split_operands_v2(first_op)
        # second_ops = split_operands_v2(second_op)
        return [first_op,  second_op]
    else:
        print("unknown type:", op_string)
        raise ValueError(f"unkown type {op_string}")


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

        try:
            operands = split_operands_v2(args[1]) if len(args) > 1 else []
        except ValueError:
            raise ValueError(f"error on spliting operands for instruction {instruction}")
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

def construct_latency_mapper(latency_if):
    with open(latency_if, 'rb') as fp:
        latency_map = pickle.load(fp)

    mapper = LatencyMapper(latency_map)
    return mapper
