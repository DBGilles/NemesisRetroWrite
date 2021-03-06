#####################################
# Definition of a NemesisNode class #
#####################################
from rwtools.nemesis.LatencyMapper import construct_latency_mapper
import os
import itertools

from rwtools.nemesis.nop_insructions import get_nop_instruction

latency_mapper = construct_latency_mapper(os.path.abspath(
    "/home/gilles/git-repos/NemesisRetroWrite/retrowrite/rwtools/nemesis/utils"
    "/pickled_latency_map.p"))


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

    def __init__(self, instruction_latency, name, mapped_node=None):
        if isinstance(instruction_latency, int):
            self.latencies = [[instruction_latency]]
        elif isinstance(instruction_latency, list):
            self.latencies = [instruction_latency]
        self.frozen = False
        self.id = name
        self.mapped_nodes = mapped_node  # reference to original node - acts as a pointer of sorts

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        out_str = ""
        out_str += f"{self.id}\n"
        for sublist in self.latencies:
            out_str += "[" + "\n".join(str(x) for x in sublist) + "]\n"
        return out_str

    # def __repr__(self):
    #     return self.id

    def num_instructions(self):
        """
        Return the total number of instructions
        """
        return sum(len(lat) for lat in self.latencies)

    def __lt__(self, other):
        return sum(self.latencies) < sum(other.latencies)

    def __gt__(self, other):
        """
        A node is 'larger' than another node if it takes a longer time to execute
        i.e. when the sum of all the latencies is larger than the other's
        """
        return sum(flatten(self.latencies)) > sum(flatten(other.latencies))

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
            counter = 0
            out = None
            for i in range(len(self.latencies)):
                for j in range(len(self.latencies[i])):
                    if counter == index - 1:
                        out = (i, j)
                    if out is not None:
                        break
                    counter += 1
                if out is not None:
                    break

            # i, j are the indices of item with i = 'index'-1, to insert at 'index', insert at j+1
            i, j = out
            j += 1

        self.latencies[i].insert(j, latency)
        if self.mapped_nodes is not None:
            for mapped_node in self.mapped_nodes:
                if mapped_node == self:
                    continue
                else:
                    mapped_node.latencies[i].insert(j, latency)
        # self.latencies.insert(index, latency)

    def get(self, item):
        if item >= len(self.latencies):
            return_val = self[-1]
        else:
            return_val = self[item]
        assert (isinstance(return_val, int))
        return return_val

    def __getitem__(self, item):
        return self.latencies[item]

    def get_latency(self, i):
        """
        Return the latency with absolute position i
        """
        return flatten(self.latencies)[i]

    def append_node(self, node):
        self.latencies += node.latencies


class NemesisNode(AbstractNemesisNode):
    """
    Concrete node, actually contains a code sequence with instructions
    """

    def __init__(self, instruction):
        latencies = [[latency_mapper.get_latency(instruction.mnemonic, instruction.op_str)]]
        name = "%x" % instruction.address  # convert address to hex for consistency with RW
        super().__init__(latencies, name)
        self.instructions = [instruction]

    def __repr__(self):
        # for each node, get a string with all of its instructions and
        out_strings = [f"{self.id}"]
        for instr, lats in zip(self.instructions, self.instructions):
            instr_strings = [b for b in instr.before] + [str(instr)] + [a for a in instr.after]
            assert (len(lats) == len(instr_strings))

            for i, l in zip(instr_strings, lats):
                out_strings.append(f"{i} ~ {l} ")

        return ", \\n".join(out_strings)

    def __lt__(self, other):
        return sum(sum(lats) for lats in self.instructions) < sum(
            sum(lats) for lats in other.latencies)

    def __gt__(self, other):
        return sum(sum(lats) for lats in self.instructions) > sum(
            sum(lats) for lats in other.latencies)

    def __len__(self):
        # return the number of latencies stored (at the lowest level)
        return sum(len(lats) for lats in self.instructions)

    def __getitem__(self, index):
        """
        Return i'th latency, corresponding latency, in the code sequence
        taking into account that InstructionWrapper can have multiple instructions
        """
        orig_index = index
        if index < 0:
            total_latencies = sum(len(lats) for lats in self.instructions)
            index = total_latencies + index

        # iterate over the latencies (nested lists) while incrementing a counter. when the
        # counter is equal to the target index, stop the iteration, get the iterator indices
        # values

        c = 0
        out = None
        for i in range(len(self.instructions)):
            for j in range(len(self.instructions[i])):
                if c == index:
                    out = (i, j)
                if out is not None:
                    break
                c += 1
            if out is not None:
                break

        # if out is still none, index is out of range
        if out is None:
            total_latencies = sum(len(lats) for lats in self.instructions)
            raise IndexError(
                f"Invalid index {orig_index} for node with {total_latencies} latencies")

        # finally, return the instructionWrapper with the given index (the first one) and the
        # latency of the relevant instruction
        assert (isinstance(self.instructions[out[0]][out[1]], int))

        return self.instructions[out[0]][out[1]]

    def get_instruction_i(self, index):
        """
        Return i'th latency, corresponding latency, in the code sequence
        taking into account that InstructionWrapper can have multiple instructions
        """
        orig_index = index
        if index < 0:
            total_latencies = sum(len(lats) for lats in self.instructions)
            index = total_latencies + index

        # iterate over the latencies (nested lists) while incrementing a counter. when the
        # counter is equal to the target index, stop the iteration, get the iterator indices
        # values

        c = 0
        out = None
        for i in range(len(self.instructions)):
            for j in range(len(self.instructions[i])):
                if c == index:
                    out = (i, j)
                if out is not None:
                    break
                c += 1
            if out is not None:
                break

        # if out is still none, index is out of range
        if out is None:
            total_latencies = sum(len(lats) for lats in self.instructions)
            raise IndexError(
                f"Invalid index {orig_index} for node with {total_latencies} latencies")
        i, j = out

        inst_wrapper = self.instructions[i]
        if j < len(inst_wrapper.before):
            return inst_wrapper.before[j]
        elif j == len(inst_wrapper.before):
            return str(inst_wrapper)
        else:
            return inst_wrapper.after[j - len(inst_wrapper.before) - 1]

    def add_instructions(self, instructions):
        assert (isinstance(instructions, list))
        self.instructions += instructions
        for i in instructions:
            assert len(i.before) == 0 and len(i.after) == 0
            self.instructions.append([latency_mapper.get_latency(i.mnemonic, i.op_str)])

    def get_node_labels_set(self):
        # map each instruction wrapper to the label in its string
        labels = ["%x" % instr.address for instr in self.instructions]
        return set(labels)

    def insert(self, index, instruction, latency):
        # instr = get_nop_instruction(target_latency)

        c = 0
        out = None
        for i in range(len(self.instructions)):
            for j in range(len(self.instructions[i])):
                if c == index - 1:
                    out = (i, j)
                if out is not None:
                    break
                c += 1
            if out is not None:
                break

        # i, j are the indices of item with i = 'index'-1, to insert at 'index', insert at j+1
        i, j = out
        j += 1

        inst_wrapper = self.instructions[i]

        # inside inst_wrapper, instert instruction at correct index
        if j <= len(inst_wrapper.before):
            inst_wrapper.before.insert(j, instruction)
        else:
            inst_wrapper.after.insert(j - len(inst_wrapper.before) - 1, instruction)
        self.instructions[i].insert(j, latency)
