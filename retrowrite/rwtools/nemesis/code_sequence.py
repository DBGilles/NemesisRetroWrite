import os

from rwtools.nemesis.LatencyMapper import construct_latency_mapper
from rwtools.nemesis.utils.latency_map import load_latency_map

latency_mapper = construct_latency_mapper(os.path.abspath("/home/gilles/git-repos/NemesisRetroWrite/retrowrite/rwtools/nemesis/utils/pickled_latency_map.p"))


class CodeSequence:
    """
    This class represents a sequence of 1 or more instructions
    This class also keeps track of control flow information, keeping track of jumps out of the section and jumps into the code section
    """

    def __init__(self, instructions):
        self.instructions = instructions
        self.branches_out = []
        self.branches_in = []
        self.latencies = []
        for i in self.instructions:
            self.latencies.append([latency_mapper.get_latency(i.mnemonic, i.op_str)])

    def add_branch_out(self, code_seq):
        self.branches_out.append(code_seq)

    def add_branch_in(self, code_seq):
        self.branches_in.append(code_seq)

    def add_instructions(self, instructions):
        assert (isinstance(instructions, list))
        self.instructions += instructions
        for i in instructions:
            assert len(i.before) == 0 and len(i.after) == 0
            self.latencies.append([latency_mapper.get_latency(i.mnemonic, i.op_str)])

    def __str__(self):
        out_strings = []
        # loop over the instruction wrappers and their latencies
        for inst, lat in zip(self.instructions, self.latencies):
            # for each instruction wrapper, collect all the instruction strings (i.e. before +
            # instruction itself + after)
            instr_strings = [b for b in inst.before] + [str(inst)] + [a for a in inst.after]
            assert (len(lat) == len(instr_strings))
            # zip the instructions with their latencies, create output string, add to list
            for instr, l in zip(instr_strings, lat):
                out_strings.append(f"{instr} ~ {l} ")

        # join the list together, return
        return ", \\n".join(out_strings)

    def __repr__(self):
        return f"[{self}]"

    def __getitem__(self, item):
        return self.get(item)

    def __len__(self):
        # return the sum of the latencies
        return sum(map(lambda x: len(x), self.latencies))

    def __lt__(self, other):
        return len(self) < len(other)

    def __gt__(self, other):
        return len(self) > len(other)

    # TODO: test get, insert methodes
    def get(self, target_i):
        """
        Return i'th instruction, corresponding latency, in the code sequence
        taking into account that InstructionWrapper can have multiple instructions
        """

        # iterate over the latencies (nested lists) while incrementing a counter. when the
        # counter is equal to the target index, stop the iteration, get the iterator indices
        # values
        c = 0
        out = None
        for i in range(len(self.latencies)):
            for j in range(len(self.latencies[i])):
                if c == target_i:
                    out = (i, j)
                if out is not None:
                    break
                c += 1
            if out is not None:
                break

        # if out is still none, index is out of range
        if out is None:
            raise IndexError

        # finally, return the instructionWrapper with the given index (the first one) and the
        # latency of the relevant instruction
        return self.instructions[out[0]], self.latencies[out[0]][out[1]]

    def insert(self, target_i, instr, lat):
        c = 0
        out = None
        for i in range(len(self.latencies)):
            for j in range(len(self.latencies[i])):
                if c == target_i:
                    out = (i, j)
                if out is not None:
                    break
                c += 1
            if out is not None:
                break

        i, j = out
        inst_wrapper = self.instructions[i]

        # inside inst_wrapper, instert instruction at correct index
        if j <= len(inst_wrapper.before):
            inst_wrapper.before.insert(j, instr)
        else:
            inst_wrapper.after.insert(j - len(inst_wrapper.before) - 1, instr)
        self.latencies[i].insert(j, lat)
