import copy
import os
import pickle

from rwtools.nemesis.types import Register


def split_operands(op_string):
    operands = list(filter(lambda x: len(x) > 0, map(lambda x: x.strip(), op_string.split(","))))
    return operands


def all_present(target_ops, candidate_ops):
    """
    Return true if all of the ops in target_ops are found in candidate_ops, otherwise return False
    """
    candidate_copy = copy.deepcopy(candidate_ops)

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
        operands = split_operands(args[1]) if len(args) > 1 else []

        # instruction contains the instruction as found in the assembly
        # operands contain the operands as found in assembly

        candidates = self.latency_map[instruction]  # dictionary mapping insruction + op_types to latency -- need to determine which is most suitable
        operand_types = list(map(construct_type, operands))  # to match candidates, convert the supplied operands to types

        # if all candidates have the same latency (meaning latency is same regardless of operand types), return that latency
        candidate_latencies = list(candidates.values())
        if len(set(candidate_latencies)) == 1:
            return candidate_latencies[0]

        # otherwise, loop over the candidates, get the best match (should be an identical match really)
        for candidate in candidates:
            candidate_op_types = candidate[1:]
            candidate_op_types = list(map(construct_type, candidate_op_types))

            if all_present(operand_types, candidate_op_types):
                return self.latency_map[instruction][candidate]

        print(f"Warning -- latency not found for instruction {instruction} with operands {operands}")
        print(candidates)
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
