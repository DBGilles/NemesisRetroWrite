from archinfo.arch_x86 import ArchX86
import re

REGISTER_TYPES = ["r"] + [f"r{x}" for x in [8, 16, 32, 64, 128, 256]] + [f"{x}mm" for x in ["", "x", "y", "z"]]
REGISTER_TYPES += ["x", "y", "z"]
REGISTER_TYPES += ["v", "sr"]
REGISTER_TYPES += ['r8l', 'r8h']
REGISTER_TYPES += ['AX', 'ax']

MEM_TYPES = [f"m{x}" for x in ['', 8, 16, 32, 64, 128, 256, 512]]

IMM_TYPES = ["i"]

ALL_TYPES = REGISTER_TYPES + MEM_TYPES + IMM_TYPES

REGISTER_NAMES = []

for reg in ArchX86.register_list:
    REGISTER_NAMES.append(reg.name)
    for subreg in reg.subregisters:
        REGISTER_NAMES.append(subreg[0])  # subreg is a tuple, with the first value being the name

for reg in ArchX86.register_list[:8]:
    # doesn't contain 64 bit version of the (first 8) registers
    name = reg.name
    REGISTER_NAMES.append('r' + name[1:])


class BaseType:
    def __init__(self, type_str, size):
        self.type_str = type_str
        self.size = size

    def is_register(self):
        return False

    def is_immediate(self):
        return False

    def is_memory(self):
        return False

    def is_relative(self):
        return False

    def __eq__(self, other):
        # two types are (weakly) equal if they are of the same type
        # TODO make this more specific
        if self.is_memory() and other.is_memory():
            return True
        elif self.is_register() and other.is_register():
            return True
        elif self.is_immediate() and other.is_immediate():
            return True
        return False

    def __str__(self):
        return self.type_str

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash(self.type_str)


class Register(BaseType):
    def __init__(self, type_str, size=None):
        super().__init__(type_str, size)
        self.size = size

    def is_register(self):
        return True


class Immediate(BaseType):
    def __init__(self, type_str, size=None):
        super().__init__(type_str, size)

    def is_immediate(self):
        return True


class Memory(BaseType):
    def __init__(self, type_str, size=None):
        super().__init__(type_str, size)

    def is_memory(self):
        return True


class Label(BaseType):
    def __init__(self, type_str):
        super().__init__(type_str, None)


class Unknown(BaseType):
    def __init__(self, type_str):
        super().__init__(type_str, None)


class Relative(BaseType):
    # TODO: is Relative altijd memory address?
    def __init__(self, type_str, size=None):
        super().__init__(type_str, size)

    def is_relative(self):
        return True


# TODO: mapping to type, construction type, taking into account size
def map_opcode_types(type_name):
    """
    Map the type representation used by package opcodes to an instance of the correct type
    Examples of type representations - imm8, imm16, ..., r8, r16, ..., mm16, mm32, ... (i.e. not actual names of registers or actual immediate values or whatnot)
    """
    # first check if the name is a register name
    if type_name in REGISTER_NAMES or type_name in REGISTER_TYPES:
        return Register(type_name)

    # check if it is an immediate value -- represente by 'imm'
    if type_name[:3] == 'imm':
        size = int(type_name[3:]) if len(type_name) > 3 else None
        return Immediate(type_name, size)

    if type_name[:5] == "moffs":
        # memory offset, regard as memory
        size = int(type_name[5:]) if len(type_name) > 5 else None
        return Memory(type_name, size)

    # if first value is m, refers to memory type
    if type_name[0] == "m":
        try:
            size = int(type_name[1:]) if len(type_name) > 1 else None
            return Memory(type_name, size)
        except ValueError:
            # error while converting last part, unknown type
            return Unknown(type_name)

    if type_name[:3] == "rel":
        size = int(type_name[3:]) if len(type_name) > 1 else None
        return Relative(type_name, size)

    return Unknown(type_name)


def map_latencydata_types(type_name):
    """
    Map the type representation used by latency data document
    i = immediate data, r = register, mm = 64 bit mmx register, x = 128 bit mmx register, mm/x = mmx or xmm register, y = 256 ymm register, m = memory operand,
    m32 = 32-bit memory operands, etc.
    v = any vector register (mmx, xmm, ymm)
    """

    if type_name in ['0', '1']:
        return Unknown(type_name)

    # cl is  register that is used for certain instructions
    if type_name == 'cl':
        return Register(type_name)

    # TODO make this its own type?
    if type_name == "stack pointer":
        return Register(type_name)

    if type_name == "[r+s*x]" or type_name == "[r+s*y]":
        return Unknown(type_name)

    if type_name[:1] == 'r':
        if type_name[-1] == 'l' or type_name[-1] == 'h':
            # h, l refer to high, low? get rid of these and continnue as normally
            type_name = type_name[:-1]  # mistake in the document? get rid of the trailing l?
        size = int(type_name[1:]) if len(type_name) > 1 else None
        return Register(type_name, size)

    # vector registers (I think)
    if type_name in ["xmm", "mmx", "ymm", "mmy"]:
        return Register(type_name)

    if type_name == 'i':
        return Immediate(type_name)
    if type_name == "v":
        return Register(type_name)

    if type_name[:3] == "xmm":
        return Register(type_name)

    if type_name[:2] == 'mm':
        size = int(type_name[2:]) if len(type_name) > 2 else None
        return Memory(type_name, size)

    if type_name[0] == 'm':
        size = int(type_name[1:]) if len(type_name) > 1 else None
        return Memory(type_name, size)

    if type_name == "x":
        return Register(type_name)

    if type_name == "y":
        return Register(type_name)

    if type_name == "near" or type_name == "short":
        return Unknown(type_name)
    raise ValueError(f"uknown type {type_name}")

REGISTER_REGEX = re.compile("%[a-z]{3}")  # '%' followed by 3 chars in alphabet
RELATIVE_FROM_REGISTER_REGEX = re.compile("-([0-9]+|0[xX][0-9a-fA-F]+)\\(%[a-z]{3}\\)")  # '-', decimal or hex number, '(' register ')'
IMM_VALUES_REGEX = re.compile("\\$(0[xX][0-9a-fA-F]+|[0-9]+)")
LABELS_REGEX = re.compile(".L[a-zA-Z0-9]+")  # '.L' followed by nonempty string of alphanumeric values

def map_assembly_values(asm_value):

    if REGISTER_REGEX.match(asm_value):
        return Register(asm_value)

    if RELATIVE_FROM_REGISTER_REGEX.match(asm_value):
        # TODO: is dit correct? heb je in dit geval een memory address?
        return Memory(asm_value)

    if IMM_VALUES_REGEX.match(asm_value):
        return Immediate(asm_value)

    if LABELS_REGEX.match(asm_value):
        return Label(asm_value)

    raise ValueError(f"unable to map unknown value {asm_value} to typ")


if __name__ == '__main__':
    print("main")
