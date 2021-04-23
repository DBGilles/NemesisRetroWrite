import os
import pickle
import xml.etree.ElementTree as ET
from collections import defaultdict


class Instruction:
    def __init__(self, asm, operands, iaca_measurements, measurement, latencies):
        self.asm = asm
        self.operands = operands
        self.iaca_measurements = iaca_measurements
        self.measurement = measurement
        self.latencies = latencies

    def __str__(self):
        return f"{self.asm} {[str(op) for op in self.operands]}"

    def __repr__(self):
        return str(self)


class Operand:
    def __init__(self, type, values):
        self.type = type
        self.values = values


class RegisterOperand:
    def __init__(self, width, xtype, values):
        self.width = width
        self.xtype = xtype
        self.values = values

    def __str__(self):
        return "reg" + str(self.width)


class MemoryOperand:
    def __init__(self, width, xtype):
        self.width = width
        self.xtype = xtype

    def __str__(self):
        return "mem" + str(self.width)


class AgenOperand:
    "Address generator operand?"
    def __init__(self, address):
        self.address = address

    def __str__(self):
        return "agen"


class ImmOperand:
    def __init__(self, width):
        self.width = width

    def __str__(self):
        return "Imm" + self.width


class RelbrOperand:
    def __init__(self):
        return

    def __str__(self):
        return "RelBranch"


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
    tree = ET.parse('/home/gilles/Downloads/instructions.xml')
    root = tree.getroot()

    # instructions = defaultdict(list)
    instructions = []
    i = 0
    for instr_node in root.iter('instruction'):
        architecture_node = instr_node.find("./architecture[@name='SKL']")
        if architecture_node is None:
            continue
        else:
            # get instruction asm
            asm = instr_node.attrib['asm']

            # parse operands
            operands = parse_operand(instr_node)

            # architecture node has children
            # 1. IACA (1 or more)
            # 2. measurement (where measurement has (1 or more) children 'latency')
            iaca_measurements = []
            for iaca_node in architecture_node.iter("IACA"):
                iaca_measurements.append({key: value for key, value in iaca_node.attrib.items()})

            measurement_node = architecture_node.findall("measurement")
            measurement_attributes = None
            latencies = []
            if len(measurement_node) == 0:
                pass
            elif len(measurement_node) == 1:
                measurement_node = measurement_node[0]
                measurement_attributes = {key: value for key, value in
                                          measurement_node.attrib.items()}

                for latency_node in measurement_node.iter("latency"):
                    # latency_attributes = {key: value for key, value in
                    #                       measurement_node.attrib.items()}
                    latencies.append({key: value for key, value in
                                      latency_node.attrib.items()})
            else:
                raise RuntimeError(
                    f"Unexpected additional measurement node. Expected 1, got {len(measurement_node)}")
            instructions.append(
                Instruction(asm, operands, iaca_measurements, measurement_attributes, latencies))
    return instructions


def create_latency_map(instructions):
    # loop over the instructions, create latency map
    latency_map = defaultdict(list)
    for instruction in instructions:
        all_latencies = []
        for latency in instruction.latencies:
            if 'cycles' in latency.keys():
                all_latencies.append(latency['cycles'])
        if len(all_latencies) > 0:
            final_latency = max(all_latencies)
            latency_map[instruction.asm].append((instruction.operands, final_latency))
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

