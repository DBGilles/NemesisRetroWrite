#####################################
# Definition of a NemesisNode class #
#####################################
from rwtools.nemesis.LatencyMapper import construct_latency_mapper
import os

from rwtools.nemesis.graph.abstract_nemesis_node import AbstractNemesisNode

latency_mapper = construct_latency_mapper(os.path.abspath(
    "/home/gilles/git-repos/NemesisRetroWrite/retrowrite/rwtools/nemesis/utils"
    "/pickled_latency_map.p"))


class NemesisNode(AbstractNemesisNode):
    """
    Concrete node, actually contains a code sequence with instructions
    """

    def __init__(self, instruction):
        latencies = [latency_mapper.get_latency(instruction.mnemonic, instruction.op_str)]
        name = "%x" % instruction.address  # convert address to hex for consistency with RW
        super().__init__(latencies, name)
        self.instruction_wrappers = [instruction]

    def __repr__(self):
        # for each node, get a string with all of its instructions and
        out_strings = [f"{self.id}"]
        for instr, lats in zip(self.instruction_wrappers, self.latencies):
            instr_strings = [b for b in instr.before] + [str(instr)] + [a for a in instr.after]
            assert (len(lats) == len(instr_strings))

            for i, l in zip(instr_strings, lats):
                out_strings.append(f"{i} ~ {l} ")
        return ", \\n".join(out_strings)

    def insert(self, index, instruction, latency):
        # instr = get_nop_instruction(target_latency)
        c = 0
        out = None
        if index == 0:
            i, j = 0, 0
        else:
            for i in range(len(self.instruction_wrappers)):
                instr_wrap = self.instruction_wrappers[i]
                instr_wrap_len = len(instr_wrap.before) + 1 + len(instr_wrap.after)
                for j in range(instr_wrap_len):
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

        inst_wrapper = self.instruction_wrappers[i]

        # inside inst_wrapper, instert instruction at correct index
        if j <= len(inst_wrapper.before):
            inst_wrapper.before.insert(j, instruction)
        else:
            inst_wrapper.after.insert(j - len(inst_wrapper.before) - 1, instruction)
        self.latencies[i].insert(j, latency)

    def get_instr_mnemonic(self, index):
        """
        Return i'th latency, corresponding latency, in the code sequence
        taking into account that InstructionWrapper can have multiple instructions
        """
        orig_index = index
        if index < 0:
            total_latencies = sum(len(lats) for lats in self.instruction_wrappers)
            index = total_latencies + index

        # iterate over the latencies (nested lists) while incrementing a counter. when the
        # counter is equal to the target index, stop the iteration, get the iterator indices
        # values

        c = 0
        out = None
        for i in range(len(self.instruction_wrappers)):
            instr_wrap = self.instruction_wrappers[i]
            instr_wrap_len = len(instr_wrap.before) + 1 + len(instr_wrap.after)
            # for j in range(len(self.instruction_wrappers[i])):
            for j in range(instr_wrap_len):
                if c == index:
                    out = (i, j)
                if out is not None:
                    break
                c += 1
            if out is not None:
                break

        # if out is still none, index is out of range
        if out is None:
            total_latencies = sum(len(lats) for lats in self.instruction_wrappers)
            raise IndexError(
                f"Invalid index {orig_index} for node with {total_latencies} latencies")
        i, j = out

        inst_wrapper = self.instruction_wrappers[i]
        if j < len(inst_wrapper.before):
            return inst_wrapper.before[j]
        elif j == len(inst_wrapper.before):
            return str(inst_wrapper)
        else:
            return inst_wrapper.after[j - len(inst_wrapper.before) - 1]

    def append_node(self, node):
        self.latencies += node.latencies
        self.instruction_wrappers += node.instruction_wrappers
