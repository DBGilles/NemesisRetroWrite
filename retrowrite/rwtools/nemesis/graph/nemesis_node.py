from rwtools.nemesis.graph.abstract_nemesis_node import AbstractNemesisNode

class NemesisNode(AbstractNemesisNode):
    """
    Concrete node, actually contains a code sequence with instructions
    """

    def __init__(self, instruction, latency=-99):
        latencies = [latency]
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

    def get_instruction_sequence(self, i):
        return self.instruction_wrappers[i]

    def get_latency_sequence(self, i):
        return self.latencies[i]

    def insert_into_instruction_sequence(self, i, j, val):
        inst_wrapper = self.instruction_wrappers[i]

        # inside inst_wrapper, instert instruction at correct index
        if j <= len(inst_wrapper.before):
            inst_wrapper.before.insert(j, val)
        else:
            inst_wrapper.after.insert(j - len(inst_wrapper.before) - 1, val)

    def insert_into_latency_sequence(self, i, j, val):
        self.latencies[i].insert(j, val)

    def is_abstract(self):
        return False

    def get_instruction_sequence_length(self, index):
        instr_wrapper = self.instruction_wrappers[index]
        return len(instr_wrapper.before) + 1 + len(instr_wrapper.after)

    def get_nr_of_instruction_sequences(self):
        return len(self.instruction_wrappers)

    def get_instr_mnemonic(self, index):
        i, j = self.get_instruction_index(index)
        inst_wrapper = self.instruction_wrappers[i]

        if j < len(inst_wrapper.before):
            return inst_wrapper.before[j]
        elif j == len(inst_wrapper.before):
            return f"{inst_wrapper.mnemonic} {inst_wrapper.op_str}"
        else:
            return inst_wrapper.after[j - len(inst_wrapper.before) - 1]

    def get_start_label(self):
        first_instruction = self.instruction_wrappers[0]
        label = f".L{hex(first_instruction.address)[2:]}"
        return label

    def append_node(self, node):
        self.latencies += node.latencies
        self.instruction_wrappers += node.instruction_wrappers

    def prepend_instruction(self, instructions, latencies):
        for instrs, lats in zip(instructions, latencies):
            for instr, lat in zip(instrs, lats):
                # add isntr, lat as last instruction, latenccy in the node
                self.instruction_wrappers[0].instrument_before(instr)
                self.latencies[0].insert(0, lat)

    def get_instructions_with_latencies(self, flatten=True):
        all_instructions = []
        for wrapper, wrapper_latencies in zip(self.instruction_wrappers, self.latencies):
            instructions = wrapper.before + [
                f"{wrapper.mnemonic} {wrapper.op_str}"] + wrapper.after
            instructions = list(zip(instructions, wrapper_latencies))
            if flatten:
                all_instructions += instructions
            else:
                all_instructions.append(instructions)
        return all_instructions

    def set_instruction_i(self, i, instruction, latency):
        # replace the i'th instruction with this new instruction
        raise NotImplementedError

    def set_branching_target(self, target):
        branching_instruction = self.instruction_wrappers[-1]
        if len(branching_instruction.after) == 0:
            # instruction has not been instrumented
            branching_instruction.op_str = target
        else:
            raise NotImplementedError
