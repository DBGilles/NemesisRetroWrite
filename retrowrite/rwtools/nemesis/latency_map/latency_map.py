import os
import pickle
import xml.etree.ElementTree as ET
from collections import defaultdict


class Instruction:
    def __init__(self, asm, operands, measurement):
        self.asm = asm
        self.operands = operands
        self.measurement = measurement

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
        return "reg"+str(self.width)


class MemoryOperand:
    def __init__(self, width, xtype):
        self.width = width
        self.xtype = xtype

    def __str__(self):
        return "mem"+str(self.width)



class AgenOperand:
    def __init__(self, address):
        self.address = address


class ImmOperand:
    def __init__(self, width):
        self.width = width

    def __str__(self):
        return "Imm" + self.width


class RelbrOperand:
    def __init__(self):
        return


class Measurement:
    def __init__(self, tp_loop, tp_ports, tp_unrolled):
        self.tp_loop = tp_loop
        self.tp_ports = tp_ports
        self.tp_unrolled = tp_unrolled
        self.latencies = []

    def add_latency_measurement(self, start_op, target_op, latency):
        self.latencies.append({
            'start_op': start_op,
            'target_op': target_op,
            'latency': latency,
        })

    def get_latency(self):
        if len(self.latencies) > 0:
            return self.latencies[0]['latency']

        return -1

class LatencyMap:
    def __init__(self, latency_dict):
        self.latency_dict = latency_dict



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


def main():
    tree = ET.parse('/home/gilles/Downloads/instructions.xml')
    root = tree.getroot()

    instructions = defaultdict(list)
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

            # parse latency information
            measurement = None
            for measurement_node in architecture_node.iter("measurement"):
                try:
                    tp_loop = float(architecture_node.attrib['tp_loop'])
                except KeyError:
                    tp_loop = None
                try:
                    tp_ports = float(architecture_node.attrib['tp_ports'])
                except KeyError:
                    tp_ports = None
                try:
                    tp_unrolled = float(architecture_node.attrib['tp_ports'])
                except KeyError:
                    tp_unrolled = None
                measurement = Measurement(tp_loop, tp_ports, tp_unrolled)
                for latency_node in measurement_node.iter("latency"):
                    try:
                        cycles = int(latency_node.attrib['cycles'])
                    except KeyError:
                        cycles = None
                    try:
                        start_op = int(latency_node.attrib['start_op'])
                    except KeyError:
                        start_op = None
                    try:
                        target_op = int(latency_node.attrib['target_op'])
                    except KeyError:
                        target_op = None
                    if cycles is None:
                        print(f"{ET.tostring(latency_node)}")
                    measurement.add_latency_measurement(start_op, target_op, cycles)

                # create instruction
                instruction = Instruction(asm, operands, measurement)
                instructions[asm].append(instruction)

    latency_of = os.path.abspath("./latency_dict.p")
    with open(latency_of, 'wb') as fp:
        pickle.dump(instructions, fp, protocol=pickle.HIGHEST_PROTOCOL)

def create_latency_map(dict_file):
    with open(dict_file, "rb") as f:
        latency_dict = pickle.load(f)
    latency_map = LatencyMap(latency_dict)
    return latency_map

if __name__ == '__main__':
    main()
