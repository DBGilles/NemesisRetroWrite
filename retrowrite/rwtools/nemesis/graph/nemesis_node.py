#####################################
# Definition of a NemesisNode class #
#####################################
from rwtools.nemesis.LatencyMapper import construct_latency_mapper
import os

from rwtools.nemesis.graph.abstract_nemesis_node import AbstractNemesisNode, flatten
from rwtools.nemesis.nop_instructions import get_nop_instruction

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

    def is_abstract(self):
        return False

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
            total_latencies = sum(len(lats) for lats in self.latencies)
            raise IndexError(
                f"Invalid index {orig_index} for node with {total_latencies} latencies")
        i, j = out

        inst_wrapper = self.instruction_wrappers[i]
        if j < len(inst_wrapper.before):
            return inst_wrapper.before[j]
        elif j == len(inst_wrapper.before):
            return f"{inst_wrapper.mnemonic} {inst_wrapper.op_str}"
            # return str(inst_wrapper)
        else:
            return inst_wrapper.after[j - len(inst_wrapper.before) - 1]

    def append_node(self, node):
        self.latencies += node.latencies
        self.instruction_wrappers += node.instruction_wrappers

    def append_instructions(self, instructions, latencies):
        for instrs, lats in zip(instructions, latencies):
            for instr, lat in zip(instrs, lats):
                # add isntr, lat as last instruction, latenccy in the node
                self.instruction_wrappers[-1].instrument_after(instr)
                self.latencies[-1].append(lat)

    def replace_latencies(self, target_latencies):
        current_latencies = []
        for l in self.latencies:
            current_latencies += l

        missing_latencies = self.compute_missing_latencies(current_latencies, target_latencies)
        for (index, latencies) in missing_latencies:
            instructions = self.map_to_instruction_sequence(latencies)
            if "jmp" in self.get_instr_mnemonic(index-1):
                index = index - 1
            for i, instr in enumerate(instructions):
                self.insert(index + i, instructions[i], latencies[i])
            # insert for each latency in latencies some instructions
            continue

    def map_to_instruction_sequence(self, latency_sequence):
        # TODO: doe dit (minder) hardcoded - hoe?
        latency = latency_sequence[0]
        nop_instruction, registers = get_nop_instruction(latency)
        if len(registers) == 0:
            # simply return the same nop instruction a number of times
            return len(latency_sequence) * [nop_instruction]
        elif latency == 3 and len(latency_sequence) == 4:
            reg = registers[0]
            instructions = [
                f"sub $0x8, %rsp",
                f"pushq {reg}",
                f"popq {reg}",
                f"add $0x8, %rsp"
            ]
            return instructions
        else:
            raise NotImplementedError

    def compute_missing_latencies(self, current_latencies, target_latencies):
        # determine which seqeuences I need to insert where to go from current_latencies
        # to target_latencies
        missing_latencies = []
        if current_latencies == target_latencies:
            return missing_latencies
        while True:
            if current_latencies == target_latencies:
                return missing_latencies

            # find length of longest common prefix, this is the index where we will need to insert
            # some sequence
            common_prefix_length = len(
                os.path.commonprefix([current_latencies, target_latencies]))
            # find longest sequence of identical latencies starting at this index
            lat = target_latencies[common_prefix_length]
            end_index = len(target_latencies)
            for j in range(len(target_latencies) - common_prefix_length):
                if target_latencies[common_prefix_length + j] != lat:
                    end_index = j
                    break

            start_index = common_prefix_length
            sequence = target_latencies[start_index:end_index]

            # add the sequence and its index to the output list
            missing_latencies.append((common_prefix_length, sequence))

            # add it to the current latency list to get the next sequence
            current_latencies = current_latencies[
                                :common_prefix_length] + sequence + current_latencies[
                                                                    common_prefix_length:]

        return missing_latencies

    def get_instructions_with_latencies(self, flatten=True):
        all_instructions = []
        for wrapper, wrapper_latencies in zip(self.instruction_wrappers, self.latencies):
            instructions = wrapper.before + [f"{wrapper.mnemonic} {wrapper.op_str}"] + wrapper.after
            instructions = list(zip(instructions, wrapper_latencies))
            if flatten:
                all_instructions += instructions
            else:
                all_instructions.append(instructions)
        return all_instructions

