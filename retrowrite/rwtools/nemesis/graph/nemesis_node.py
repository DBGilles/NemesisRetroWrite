#####################################
# Definition of a NemesisNode class #
#####################################
from rwtools.nemesis.LatencyMapper import construct_latency_mapper
import os

from rwtools.nemesis.nop_insructions import get_nop_instruction

latency_mapper = construct_latency_mapper(os.path.abspath(
    "/home/gilles/git-repos/NemesisRetroWrite/retrowrite/rwtools/nemesis/utils/pickled_latency_map.p"))


class AbstractNemesisNode:
    """
    abstract version of the nemesis node -- contains only a list of latencies
    """

    def __init__(self, latencies, name):
        self.latencies = latencies
        self.frozen = False
        self.id = name

    def __hash__(self):
        # self.frozen = True
        # self.latencies = tuple(self.latencies)
        return hash(self.id)

    def __repr__(self):
        return "\n".join(str(x) for x in [self.id] + self.latencies)
        # return str(self.id)

    def __len__(self):
        # return the sum of the latencies
        return len(self.latencies)

    def __lt__(self, other):
        return sum(self.latencies) < sum(other.latencies)

    def __gt__(self, other):
        return sum(self.latencies) > sum(other.latencies)

    def insert(self, index, instruction, latency):
        self.latencies.insert(index, latency)

    def get(self, item):
        if item >= len(self.latencies):
            return_val = self[-1]
        else:
            return_val = self[item]
        assert (isinstance(return_val, int))
        return return_val

    def __getitem__(self, item):
        return self.latencies[item]


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
        for instr, lats in zip(self.instructions, self.latencies):
            instr_strings = [b for b in instr.before] + [str(instr)] + [a for a in instr.after]
            assert (len(lats) == len(instr_strings))

            for i, l in zip(instr_strings, lats):
                out_strings.append(f"{i} ~ {l} ")

        return ", \\n".join(out_strings)

    def __lt__(self, other):
        return sum(sum(lats) for lats in self.latencies) < sum(
            sum(lats) for lats in other.latencies)

    def __gt__(self, other):
        return sum(sum(lats) for lats in self.latencies) > sum(
            sum(lats) for lats in other.latencies)

    def __len__(self):
        # return the number of latencies stored (at the lowest level)
        return sum(len(lats) for lats in self.latencies)

    def __getitem__(self, index):
        """
        Return i'th latency, corresponding latency, in the code sequence
        taking into account that InstructionWrapper can have multiple instructions
        """
        orig_index = index
        if index < 0:
            total_latencies = sum(len(lats) for lats in self.latencies)
            index = total_latencies + index

        # iterate over the latencies (nested lists) while incrementing a counter. when the
        # counter is equal to the target index, stop the iteration, get the iterator indices
        # values

        c = 0
        out = None
        for i in range(len(self.latencies)):
            for j in range(len(self.latencies[i])):
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

        # finally, return the instructionWrapper with the given index (the first one) and the
        # latency of the relevant instruction
        assert (isinstance(self.latencies[out[0]][out[1]], int))

        return self.latencies[out[0]][out[1]]

    def get_instruction_i(self, index):
        """
        Return i'th latency, corresponding latency, in the code sequence
        taking into account that InstructionWrapper can have multiple instructions
        """
        orig_index = index
        if index < 0:
            total_latencies = sum(len(lats) for lats in self.latencies)
            index = total_latencies + index

        # iterate over the latencies (nested lists) while incrementing a counter. when the
        # counter is equal to the target index, stop the iteration, get the iterator indices
        # values

        c = 0
        out = None
        for i in range(len(self.latencies)):
            for j in range(len(self.latencies[i])):
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
            self.latencies.append([latency_mapper.get_latency(i.mnemonic, i.op_str)])

    def get_node_labels_set(self):
        # map each instruction wrapper to the label in its string
        labels = ["%x" % instr.address for instr in self.instructions]
        return set(labels)

    def insert(self, index, instruction, latency):
        # instr = get_nop_instruction(target_latency)

        c = 0
        out = None
        for i in range(len(self.latencies)):
            for j in range(len(self.latencies[i])):
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
        self.latencies[i].insert(j, latency)
