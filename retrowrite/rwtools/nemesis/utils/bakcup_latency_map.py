from collections import defaultdict

from enum import Enum


class OpType(Enum):
    Immediate = 1
    Register = 2
    Reg8 = 3
    Reg16 = 4
    Reg32 = 5
    Memory = 6
    Mem7 = 7


# Map instruction names to a list of InstructionTypes
# InstructionTypes contains information on name of instruction, operands, latency
class InstructionType:
    def __init__(self, name, operands, latency):
        self.name = str.lower(name)
        self.operands = operands
        self.latency = latency

    def __str__(self):
        op_str = ",".join(self.operands)
        return f"{self.name} {op_str}:{self.latency}"

    def __repr__(self):
        return self.__str__()


class LatencyMap:
    def __init__(self, instructions):
        self.latency_map = dict()
        for i in instructions:
            if i.name in self.latency_map.keys():
                self.latency_map[i.name].append(i)
            else:
                self.latency_map[i.name] = [i]

    def __repr__(self):
        return self.latency_map.__repr__()

    def __getitem__(self, inst_name):
        inst_name = inst_name[0]
        operands = inst_name[1:] if len(inst_name) > 1 else None
        if inst_name in self.latency_map.keys():
            candidates = self.latency_map[inst_name]
            if operands is None:
                return candidates[0].latency
            else:
                return candidates[0].latency
        else:
            return 99

def get_latency_map():
    instructions = [
        InstructionType("ADC", ["reg", "reg"], 1),
        InstructionType("ADC", ["reg", "imm"], 1),
        InstructionType("SBB", ["reg", "reg"], 1),
        InstructionType("SBB", ["reg", "imm"], 1),
        InstructionType("ADD", [], 1),
        InstructionType("SUB", [], 1),
        InstructionType("AND", [], 1),
        InstructionType("OR", [], 1),
        InstructionType("XOR", [], 1),
        InstructionType("BSF", [], 3),
        InstructionType("BSR", [], 3),
        InstructionType("BSWAP", [], 2),
        InstructionType("BT", [], 1),
        InstructionType("BTC", [], 1),
        InstructionType("BTR", [], 1),
        InstructionType("BTS", [], 1),
        InstructionType("CBW", [], 1),
        InstructionType("CWDE", [], 1),
        InstructionType("CDQE", [], 1),

        InstructionType("CDQ", [], 1),

        InstructionType("CQO", [], 1),
        InstructionType("CMOVE", [], 1),
        InstructionType("PUSHQ", [], 2),  # TODO: not confirmed
        InstructionType("MOVQ", [], 1),  # TODO: not confirmed
        InstructionType("MOVL", [], 1),  # TODO: not confirmed
        InstructionType("IMULL", [], 2),  # TODO: not confirmed
        InstructionType("ADDL", [], 1),  # TODO: not confirmed
        InstructionType("JLE", [], 1),  # TODO: not confirmed
        InstructionType("JMP", [], 1),  # TODO: not confirmed
        InstructionType("POPQ", [], 1),  # TODO: not confirmed
        InstructionType("RETQ", [], 1),  # TODO: not confirmed
        InstructionType("CMPL", [], 2),  # TODO: not confirmed
    ]

    latency_map = LatencyMap(instructions)
    return latency_map


if __name__ == '__main__':
    latency_map = get_latency_map()
    print(latency_map)
