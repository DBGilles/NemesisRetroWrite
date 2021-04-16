############################################
# Definition of Abstract NemesisNode class #
############################################

def flatten(nested_list):
    ret = []
    for sublist in nested_list:
        ret += sublist
    return ret


class AbstractNemesisNode:
    """
    abstract version of the nemesis node -- contains only a list of latencies
    A concrete node contains a list of instruction wrappers (each wrapper can contain multiple
    instructions after instrumentation).
    In this abstract version of  a node an instruction wrapper is simply a (nested)
    list of latencies
    """

    def __init__(self, instruction_latency, name):
        if isinstance(instruction_latency, int):
            self.latencies = [[instruction_latency]]
        elif isinstance(instruction_latency, list):
            self.latencies = [instruction_latency]
        self.instructions = [[]]
        self.frozen = False
        self.id = name
        self.mapped_nodes = None  # reference to original node - acts as a pointer of sorts

    def __repr__(self):
        out_str = ""
        out_str += f"#{self.id}#\n"
        for i, sublist in enumerate(self.latencies):
            strings = []
            for j, latency in enumerate(sublist):
                try:
                    instruction = self.instructions[i][j]
                except IndexError:
                    instruction = ""
                strings.append(f"{instruction} ~ {latency}")
            out_str += "\n".join(strings) + "\n"
        return out_str

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __gt__(self, other):
        """
        A node is 'larger' than another node if it takes a longer time to execute
        i.e. when the sum of all the latencies is larger than the other's
        """
        # return sum(flatten(self.latencies)) > sum(flatten(other.latencies))
        return sum(sum(lats) for lats in self.latencies) > sum(
            sum(lats) for lats in other.latencies)

    def get_instruction_sequence(self, i):
        return self.instructions[i]

    def get_latency_sequence(self, i):
        return self.latencies[i]

    def insert_into_instruction_sequence(self, i, j, val):
        self.instructions[i].insert(j, val)

    def insert_into_latency_sequence(self, i, j, val):
        self.latencies[i].insert(j, val)

    def get_instruction_sequence_length(self, index):
        # TODO: is dit ok? in `pr`incipe zouden die altijd gelijk moeten zijn (tenzij
        # abstract node enkel latencies  heeft
        return len(self.latencies[index])
        # return len(self.instructions[index])

    def get_nr_of_instruction_sequences(self):
        return len(self.instructions)

    def get_instr_mnemonic(self, index):
        return flatten(self.instructions)[index]

    def get_instr_latency(self, index):
        return flatten(self.latencies)[index]

    def append_node(self, node):
        self.instructions += node.instruction
        self.latencies += node.latencies

    def prepend_instructions(self, instructions, latencies):
        i = 0
        for instrs, lats in zip(instructions, latencies):
            for instr, lat in zip(instrs, lats):
                # add isntr, lat as last instruction, latenccy in the node
                self.insert(i, instr, lat)
                i += 1
                # self.instruction_wrappers[-1].instrument_after(instr)
                # self.latencies[-1].append(lat)

    def append_instructions(self, instructions, latencies):
        i = self.num_instructions()
        for instrs, lats in zip(instructions, latencies):
            for instr, lat in zip(instrs, lats):
                self.insert(i, instr, lat)
                i += 1

    def insert(self, index, instruction, latency):
        """
        Insert instruction at absolute index i
        Find where instruction at absolute index i-1 is locted, insert right after it
        """
        if index == 0:
            i, j = 0, 0
        elif index > self.num_instructions():
            raise ValueError(f"Cant insert instruction at index {index} into node with "
                             f"{self.num_instructions()} instructions")
        else:
            i, j = self.get_instruction_index(index - 1)
            j += 1

        self.insert_into_instruction_sequence(i, j, instruction)
        self.insert_into_latency_sequence(i, j, latency)

    def is_abstract(self):
        return True

    def get_instruction_index(self, index):
        orig_index = index
        if index < 0:
            # if index negative convert it by adding number instructions
            index = self.num_instructions() + index

        c = 0
        out = None
        for i in range(self.get_nr_of_instruction_sequences()):
            # instruction_sequence = self.instructions[i]
            # instruction_sequence_len = len(instruction_sequence)
            instr_sequence_len = self.get_instruction_sequence_length(i)
            # for j in range(len(self.instruction_wrappers[i])):
            for j in range(instr_sequence_len):
                if c == index:
                    out = (i, j)
                if out is not None:
                    break
                c += 1
            if out is not None:
                break

        # if out is still none, index is out of range
        if out is None:
            total_latencies = sum(len(lats) for lats in self.latencies)
            raise IndexError(
                f"Invalid index {orig_index} for node with {total_latencies} latencies")
        i, j = out

        # inst_wrapper = self.instruction_wrappers[i]
        return i, j

    def num_instructions(self):
        """
        Return the total number of instructions
        """
        return sum(len(lat) for lat in self.latencies)

    def get_instructions(self, flatten=True):
        if flatten:
            out = []
            for x in self.instructions:
                out += x
            return out
        else:
            return self.instructions

    def get_latencies(self, flatten=True):
        if flatten:
            out = []
            for lats in self.latencies:
                out += lats
                # out += [l for l in lats if l != 0]
            return out
        else:
            return self.latencies

    def get_instructions_with_latencies(self, flatten=True):
        all_instructions = []
        for instruction_list, latency_list in zip(self.instructions, self.latencies):
            instructions = list(zip(instruction_list, latency_list))
            if flatten:
                all_instructions += instructions
            else:
                all_instructions.append(instructions)
        return all_instructions

    def replace_instructions(self, new_sequence):
        # if len(flatten(self.instructions)) != len(flatten(self.latencies)):
        #     debug = True
        # else:
        #     debug = False

        debug=False
        if debug:
            # look only at latencies
            for i, (_, latency) in enumerate(new_sequence):
                if i < self.num_instructions() and latency == self.get_instr_latency(i):
                    continue
                else:
                    self.insert(i, "", latency)
        else:
            for i, (instr, latency) in enumerate(new_sequence):
                if i < self.num_instructions() and instr == self.get_instr_mnemonic(i):
                    continue
                else:
                    # insert the instruction at index i
                    self.insert(i, instr, latency)
