import copy

from rwtools.nemesis.latency_map.create_latency_map import RegisterOperand, ImmOperand, \
    MemoryOperand, AgenOperand
from rwtools.nemesis.op_types import Immediate, Memory, Register, Label, BaseType
from rwtools.nemesis.string_matching import one_op_regex, RELATIVE_FROM_COMPOUND_OP, COMPOUND_OP, \
    two_ops_regex, three_ops_regex, REGISTER_REGEX, RELATIVE_FROM_REGISTER_REGEX, \
    LABEL_RELATIVE_FROM_REGISTER, IMM_VALUES_REGEX, LABELS_REGEX

modifier_to_size = {'q': 64, 'l': 32, 'w': 16, 'b': 8}


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


def split_operands(op_string):
    # first use the various regex to determine the structure of the operands (i.e. how many,
    # what form) given the form, split the string suitably. Ideally you could use the capture
    # groups, but because of the way the regexes are constructed this might be confusing
    op_string = op_string.strip()
    if len(op_string) == 0:
        return []
    if one_op_regex.fullmatch(op_string):
        if RELATIVE_FROM_COMPOUND_OP.match(op_string):
            closing_paren = op_string.find(")")
            operands = [op_string[:closing_paren + 1]]
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
        return [first_op, second_op]
    elif three_ops_regex.fullmatch(op_string):
        # TODO: in the case of a compound op this will fail (we don't want to split on the
        # commas within this compound op e.g. op1, (op2_a, op2_b, op2_c), op3
        ops = [op.strip() for op in op_string.split(",")]
        return ops
    else:
        print("unknown type:", op_string)
        raise ValueError(f"unkown type {op_string}")


def map_assembly_values(asm_value):
    if isinstance(asm_value, list):
        raise ValueError("obsolete, should never occur anymore")
        # substring = ", ".join(asm_value)
        # asm_value = f"({substring})"
        # return Memory(asm_value)

    try:
        _ = int(asm_value)
        return Immediate(asm_value)
    except ValueError:
        pass
    except TypeError:
        pass

    if COMPOUND_OP.fullmatch(asm_value):
        return Memory(asm_value)

    if RELATIVE_FROM_COMPOUND_OP.fullmatch(asm_value):
        return Memory(asm_value)

    if REGISTER_REGEX.match(asm_value):
        return Register(asm_value)

    if RELATIVE_FROM_REGISTER_REGEX.match(asm_value) or LABEL_RELATIVE_FROM_REGISTER.match(
            asm_value):
        # TODO: is dit correct? heb je in dit geval een memory address?
        return Memory(asm_value)

    if IMM_VALUES_REGEX.match(asm_value):
        return Immediate(asm_value)

    if LABELS_REGEX.match(asm_value):
        return Label(asm_value)

    if "@PLT" in asm_value or "@plt" in asm_value:
        # @PLT: https://stackoverflow.com/questions/5469274/what-does-plt-mean-here
        # Use only for 'call' instruction
        return Memory(asm_value)

    raise ValueError(f"warning, unable to map unknown value {asm_value} to type")
    # print(f"warning, unable to map unknown value {asm_value} to type")
    # return Unknown(asm_value)


def count_matches(instruction_asm, candidate_types, asm_operands):
    candidates_copy = list(copy.deepcopy(candidate_types))
    matches = 0
    for asm_op in asm_operands:
        for candidate in candidates_copy:
            if is_match(instruction_asm, candidate, asm_op):
                matches += 1
                candidates_copy.remove(candidate)
                break
    return matches


def is_match(instruction_asm, c_type, asm):
    asm_type = map_assembly_values(asm)
    if isinstance(c_type, RegisterOperand):
        if isinstance(asm_type, Register):
            register_value = asm
            if register_value[0] == "%":
                register_value = register_value[1:]
            register_value = register_value.upper()
            if register_value in c_type.values:
                return True
        return False

    elif isinstance(c_type, ImmOperand):
        if isinstance(asm_type, Immediate):
            return True
        else:
            return False

    elif isinstance(c_type, MemoryOperand):
        if isinstance(asm_type, Memory):
            size_modifier = instruction_asm[-1]
            if size_modifier in ['q', 'l', 's', 'b']:
                size = modifier_to_size[size_modifier]
                if int(size) == int(c_type.width):
                    return True
            else:
                return True
        return False
    elif isinstance(c_type, AgenOperand):
        if isinstance(asm_type, Memory):
            return True
        return False
    else:
        raise NotImplementedError(f"haven't taken into account type for {type(c_type)}")


def is_branching_instruction(instruction):
    return True in [x in instruction for x in ["jmp", "je", "jne"]]


class LatencyMapV2:
    def __init__(self, latencies):
        self.latencies = latencies

    def get_candidates(self, instruction):
        # first look for the instruction itself, then if no results found look for the instruction
        # without size modifier
        instruction = instruction.upper()
        if instruction in self.latencies.keys():
            return self.latencies[instruction]
        elif instruction[:-1] in self.latencies.keys():
            return self.latencies[instruction[:-1]]
        else:
            return []

    def count_match(self):
        return

    def get_latency(self, *args):
        instruction = args[0]
        # size_modifier = instruction[-1] if instruction[-1] in ['q', 'l', 'w', 'b'] else None

        # in some cases syntax is not exactly the same -- specific
        # instructions need to be mapped to more general versions
        # TODO: use the size information stored in the mnemonic instead of simply converting to
        # general version
        if 'movs' in instruction:
            instruction = "movsx"
        if 'movz' in instruction:
            instruction = "movzq"

        if instruction == "enrbs64":
            return 0

        if is_branching_instruction(instruction):
            return -1

        try:
            operands = split_operands(args[1]) if len(args) > 1 else []
        except ValueError:
            raise ValueError(f"error on spliting operands for instruction {instruction}")

        candidates = self.get_candidates(instruction)
        if len(candidates) == 0:
            print(f"no latency information found for instruction: {instruction} ")
            return -1
        # if all latencies are the same, don't bother selecting best candidate
        latencies = [latency for _, latency in candidates]
        if len(set(latencies)) == 1:
            return latencies[0]
        # otherwise select the candidate that is the best match
        max_match = 0
        best_ops = None
        best_lat = None
        for candidate_ops, latency in candidates:
            match_count = count_matches(instruction, candidate_ops, operands)
            if match_count > max_match:
                max_match = match_count
                best_lat = latency
                best_ops = candidate_ops
        if best_lat is None:
            print("warning, no latency found for instruction")
        return best_lat
