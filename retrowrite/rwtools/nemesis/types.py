class BaseType:
    def __init__(self, type_str):
        self.type_str = type_str

    def is_register(self):
        return False

    def is_immediate(self):
        return False

    def is_memory(self):
        return False

    def __eq__(self, other):
        # two types are (weakly) equal if they are of the same type
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

class Register(BaseType):
    def __init__(self, type_str):
        super().__init__(type_str)

    def is_register(self):
        return True


class Immediate(BaseType):
    def __init__(self, type_str):
        super().__init__(type_str)

    def is_immediate(self):
        return True


class Memory(BaseType):
    def __init__(self, type_str):
        super().__init__(type_str)

    def is_memory(self):
        return True

class Label(BaseType):
    def __init__(self, type_str):
        super().__init__(type_str)

def construct_type(type_str):
    if '%' in type_str:
        return Register(type_str)
    elif '$' in type_str:
        return Immediate(type_str)
    elif "(" in type_str and ')' in type_str:
        return Memory(type_str)
    elif '.L' in type_str:
        return Label(type_str)
    elif 'r' in type_str:
        return Register(type_str)
    elif 'imm' in type_str:
        return Immediate(type_str)
    elif 'm' in type_str:
        return Memory(type_str)
    elif 'eax' in type_str:
        return Register(type_str)
    raise ValueError(f"unknown type string {type_str}")


if __name__ == '__main__':
    str_a = "r64"
    str_b = "r64"
    type_a = construct_type("r")
    type_b = construct_type("r64")
