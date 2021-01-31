"""
The data directory contains .csv files that store the numver of cycles per instruction.
Preprocess this data, generate a dictionary
Read: https://stackoverflow.com/questions/692718/how-many-cpu-cycles-are-needed-for-each-assembly-instruction#:~:text=For%20example%2C%20on%20most%20recent,four%20add%2Dcapable%20units).
also https://www.agner.org/optimize/#manual_instr_tab
TODO: dit moet eigenlijk veel beter aangepast zijn aan hoe het gebruikt zal worden in RetroWrite
"""
import os
import re


# operand_parser = re.compile("r[]")
from rwtools.nemesis.utils.latency_map import OpType


def valid_line(line):
    # any line that actually contains information on instructions should have (at least) 5 ';'-seperated values
    items = list(filter(lambda x: len(x) > 0, line.split(";")))
    # table header will have the same numver of items as table entries except it's values will have special values (e.g. first value will be 'Instruction')
    return len(items) >= 5 and items[0] != "Instruction"


def process_latency_field(lat):
    if len(lat) == 0:
        return None
    else:
        lat = lat.split('-')
        return lat


def process_name_field(name_str):
    names = []
    if ' ' in name_str:
        names = list(map(lambda x: x.strip(), " ".split(name_str)))
        print(names)
    else:
        # assume only a single name present
        names = [name_str]

    return names

def preprocess_lines(lines):
    output = []

    for l in lines:
        fields = l.split(";")
        mnems = process_name_field(fields[0])
        print(mnems)
        # operands = fields[1].split(",")
        # operands = list(map(map_to_optype, operands))
        # latency = fields[2]
        # for mnem in mnems:
        #     output.append((mnem, operands, latency))
        # print(output)
    # return for each line a dictionary?

def map_to_optype(op_str):
    if op_str == "i":
        return OpType.Immediate
    if op_str == "r":
        return OpType.Register


def create_dictionary(input_file):
    with open(input_file, "r") as f:
        lines = f.readlines()

    lines = filter(valid_line, lines)

    preprocess_lines(lines)


if __name__ == '__main__':
    input_file = os.path.abspath("../_data/raw_skylake.csv")
    create_dictionary(input_file)
