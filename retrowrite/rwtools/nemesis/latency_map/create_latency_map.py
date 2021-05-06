import os
import pickle
import xml.etree.ElementTree as ET
from collections import defaultdict


class Instruction:
    def __init__(self, asm, operands, latencies):
        self.asm = asm
        self.operands = operands
        self.latencies = latencies

    def __str__(self):
        return f"{self.asm} {[str(op) for op in self.operands]}"

    def __repr__(self):
        return str(self)


class Operand:
    def __init__(self, type, values):
        self.type = type
        self.values = values

    def __eq__(self, other):
        raise NotImplementedError


class RegisterOperand:
    def __init__(self, width, xtype, values):
        self.width = width
        self.xtype = xtype
        self.values = values

    def __str__(self):
        return "reg" + str(self.width)

    def __eq__(self, other):
        if isinstance(other, RegisterOperand) and self.width == other.width:
            return True
        return False


class MemoryOperand:
    def __init__(self, width, xtype):
        self.width = width
        self.xtype = xtype

    def __str__(self):
        return "mem" + str(self.width)

    def __eq__(self, other):
        if isinstance(other, MemoryOperand) and self.width == other.width:
            return True
        return False


class AgenOperand:
    """Address generator operand?"""

    def __init__(self, address):
        self.address = address

    def __str__(self):
        return "agen"

    def __eq__(self, other):
        return isinstance(other, AgenOperand)


class ImmOperand:
    def __init__(self, width):
        self.width = width

    def __str__(self):
        return "Imm" + self.width

    def __eq__(self, other):
        return isinstance(other, ImmOperand)


class RelbrOperand:
    def __init__(self):
        return

    def __str__(self):
        return "RelBranch"

    def __eq__(self, other):
        return isinstance(other, ImmOperand)
        return True


class Measurement:
    def __init__(self, tp_loop, tp_ports, tp_unrolled):
        self.tp_loop = tp_loop
        self.tp_ports = tp_ports
        self.tp_unrolled = tp_unrolled
        self.latencies = []

    def add_latency_measurement(self, attributes):
        self.latencies.append(attributes)

    def get_latency(self):
        if len(self.latencies) > 0:
            return self.latencies[0]['latency']

        return -1


def get_attribute(node, attr_key):
    try:
        attr = node.attrib[attr_key]
    except KeyError:
        attr = ""
    return attr


def parse_operand(instr_node):
    # parse operands
    operands = []
    for operand_node in instr_node.iter('operand'):
        if operand_node.attrib.get('suppressed', '0') == '1':
            # not sure what this means
            continue
        operand_type = operand_node.attrib['type']

        operand_id = operand_node.attrib['idx']
        if operand_type == 'reg':
            reg_width = get_attribute(operand_node, "width")
            reg_xtype = get_attribute(operand_node, "xtype")
            reg_values = operand_node.text.split(",")
            operands.append(RegisterOperand(reg_width, reg_xtype, reg_values))
        elif operand_type == 'mem':
            mem_width = get_attribute(operand_node, "width")
            mem_xtype = get_attribute(operand_node, "xtype")
            operands.append(MemoryOperand(mem_width, mem_xtype))
        elif operand_type == "agen":
            agen = get_attribute(instr_node, 'agen')
            address = []
            # copied from uops.info script (not sure what this does)
            if 'R' in agen:
                address.append('RIP')
            if 'B' in agen:
                address.append('RAX')
            if 'IS' in agen:
                address.append('2*RBX')
            elif 'I' in agen:
                address.append('1*RBX')
            if 'D8' in agen:
                address.append('8')
            if 'D32' in agen:
                address.append('128')
            operands.append(AgenOperand(address))
        elif operand_type == 'imm':
            imm_width = get_attribute(operand_node, 'width')
            operands.append(ImmOperand(imm_width))
        elif operand_type == 'relbr':
            operands.append(RelbrOperand())
        else:
            raise ValueError(f"Unknown memory type: {operand_node.attrib['type']}")
    return operands


def read_uops_xml():
    tree = ET.parse(
        '/home/gilles/git-repos/NemesisRetroWrite/retrowrite/rwtools/nemesis/data/instructions.xml')
    root = tree.getroot()

    instructions = []
    for instr_node in root.iter('instruction'):
        architecture_node = instr_node.find("./architecture[@name='SKL']")
        if architecture_node is None:
            continue
        else:
            # get instruction asm
            asm = instr_node.attrib['asm']
            # parse operands
            operands = parse_operand(instr_node)

            measurement_node = architecture_node.findall("measurement")
            latencies = []

            if len(measurement_node) == 0:
                pass
            elif len(measurement_node) == 1:
                measurement_node = measurement_node[0]
                for latency_node in measurement_node.iter("latency"):
                    latency_keys = [key for key in latency_node.attrib.keys() if
                                    'cycles' in key and "is_upper_bound" not in key]
                    for key in latency_keys:
                        latency = int(latency_node.attrib[key])
                        if f"{key}_is_upper_bound" in latency_node.attrib:
                            is_upper_bound = (latency_node.attrib[f"{key}_is_upper_bound"] == "1")
                        else:
                            is_upper_bound = False
                        latencies.append((key, latency, is_upper_bound))
            else:
                raise RuntimeError(
                    f"Unexpected additional measurement node. Expected 1, got {len(measurement_node)}")
            instructions.append(
                Instruction(asm, operands, latencies))
    return instructions


def same_ops(ops_a, ops_b):
    if len(ops_a) != len(ops_b):
        return False

    matched = []
    for a in ops_a:
        for b in ops_b:
            if b not in matched and a == b:
                matched.append(b)
                continue
    # same ops if all elems in ops_b are matched with some elem in ops_a
    return len(matched) == len(ops_b)


def create_latency_map(instructions):
    # loop over the instructions, create latency map
    latency_map = defaultdict(list)
    existing_operands = defaultdict(list)
    count = 0
    total_count = 0
    for instruction in instructions:
        total_count += 1
        # check existing operands, if duplicate then skip
        matched = False
        for ops in existing_operands[instruction.asm]:
            if same_ops(instruction.operands, ops):
                matched = True
                count += 1
                break
        if matched:
            continue
        all_latencies = []
        for latency_type, value, is_upper_bound in instruction.latencies:
            # strategy, add all latencies regardless of whether or not they are upper bounds
            if not is_upper_bound:
                all_latencies.append(value)
        if len(all_latencies) > 0:
            final_latency = max(all_latencies)
            latency_map[instruction.asm].append((instruction.operands, final_latency))
            existing_operands[instruction.asm].append(instruction.operands)
    latency_map["PUSH"].append(([], 3))       # source: Agner Fog
    latency_map["PUSHQ"].append(([], 3))      # source: Agner Fog
    return latency_map


def load_latency_map(input_file):
    with open(input_file, 'rb') as handle:
        latency_map = pickle.load(handle)
    return latency_map


if __name__ == '__main__':
    # read all of the information from the uops xml, parse into list of Instructions
    instructions = read_uops_xml()

    # create latency map
    latency_map = create_latency_map(instructions)

    with open("./latencies.p", 'wb') as handle:
        pickle.dump(latency_map, handle, protocol=pickle.HIGHEST_PROTOCOL)
