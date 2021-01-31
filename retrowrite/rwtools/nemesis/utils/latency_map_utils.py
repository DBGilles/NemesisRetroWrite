import os
import pandas as pd
import opcodes
from opcodes.x86_64 import read_instruction_set

#############
# Constants #
#############

REG_NAMES = ["r"] + [f"r{x}" for x in [8, 16, 32, 64, 128, 256]] + [f"{x}mm" for x in ["", "x", "y", "z"]]
REG_NAMES += ["x", "y", "z"]
REG_NAMES += ["v", "sr"]
REG_NAMES += ['r8l', 'r8h']
REG_NAMES += ['AX', 'ax']

MEM_OPERANDS = [f"m{x}" for x in ['', 8, 16, 32, 64, 128, 256, 512]]

IMM_OPERANDS = ["i"]

ALL_TYPES = REG_NAMES + MEM_OPERANDS + IMM_OPERANDS


####################
# Helper functions #
####################

def convert_latency(lat):
    """
    Convert the given latency to a fixed type (float) -- ensure uniformity between rows
    """
    if isinstance(lat, int):
        return lat
    elif isinstance(lat, float):
        return int(lat)
    elif isinstance(lat, str):
        try:
            # try casting string to float and returning it
            return int(lat)
        except ValueError:
            # if it doesn succeed, continue with rest of the function z
            pass
            # several special cases, handle seperately
        if "-" in lat:
            # latency of type 'a-b' -- return float(b)
            return int(lat.split("-")[-1])
        if 'b' in lat:
            return -1
        if "~" in lat:
            return int(lat[1:])


def is_type(a):
    return a in ALL_TYPES


def is_reg(a):
    if isinstance(a, opcodes.x86_64.Operand):
        return a.is_register
    else:
        return a in REG_NAMES


def is_mem(a):
    if isinstance(a, opcodes.x86_64.Operand):
        return a.is_memory
    else:
        return a in MEM_OPERANDS


def is_imm(a):
    if isinstance(a, opcodes.x86_64.Operand):
        return a.is_immediate
    else:
        return a in IMM_OPERANDS


def type_match(a, b):
    if is_reg(a) and is_reg(b):
        return True
    elif is_mem(a) and is_mem(b):
        return True
    elif is_imm(a) and is_imm(b):
        return True
    else:
        return False


def cast_to_types(op_types):
    if not False in map(lambda x: is_type(x), op_types):
        return op_types
    # first, determine if this is some special case
    if '[' in op_types[0] and ']' in op_types[0]:
        # 'r+s*y' (represents some compound type maybe? IDK?)
        return []
    elif 'stack pointer' in op_types[0]:
        # TODO: check if stack pointer needs its own type
        return ['m']
    elif 'cl' in op_types[0]:
        # no clue what this could be
        return []
    elif 'short' in op_types[0] or 'near' in op_types[0]:
        # TODO check if distinction between short and near is important for latency
        return ['m']
    elif 'a' in op_types[0] or 'b' in op_types[0]:
        return ['i16']  # use only in enter (and somehwere else, idk) https://www.felixcloutier.com/x86/enter
    elif '0' in op_types[0] or '1' in op_types[0]:
        return ['i16']  # TODO nakijken
    elif len(op_types) == 2 and is_type(op_types[0]):
        # cast second op type to type of first --
        # at this point you can simply preprend first char to get crrect type
        return [op_types[0], op_types[0][0] + op_types[1]]


def extract_operand_types(op_string):
    """
    Return for each operand position (seperated by commas) a list of possible operand typess
    eg input 'r32/64,r32/64' return [r32, r64], [r32, r64]
    """

    if op_string == "nan" or op_string is None or isinstance(op_string, float):
        # nan is apparently of type float
        return []

    operand_positions = op_string.split(",")
    operand_types = []
    for ops in operand_positions:
        # now we are looking at individual operands -- ensure they are one of the types defined above, if not cast
        op_types = list(map(lambda x: x.strip(), ops.split("/")))
        operand_types.append(cast_to_types(op_types))
    return operand_types


def length_diff(a, b):
    return abs(len(a) - len(b))


def best_candidate(key, candidates):
    # get the candidate that is the best/closest match to key k (in terms of name, operands, etc)
    if len(candidates) == 1:
        return candidates.iloc[0]
    else:
        # sort candidates based on length similarity
        target_name, target_gas_name = key[:2]
        operands = key[2:] if len(key) > 2 else []
        candidates = candidates.values.tolist()
        candidates.sort(key=lambda x: length_diff(x[0], key[0]))

        candidate_match_counts = []
        for c in candidates:
            candidate_ops = c[1]
            candidate_op_types = extract_operand_types(candidate_ops)
            match_count = 0
            for op, candidate_types in zip(operands, candidate_op_types):
                op = opcodes.x86_64.Operand(op)
                for c in candidate_types:
                    if type_match(op, c):
                        match_count += 1
                        break
            candidate_match_counts.append(match_count)
        max_i = candidate_match_counts.index(max(candidate_match_counts))
        return candidates[max_i]