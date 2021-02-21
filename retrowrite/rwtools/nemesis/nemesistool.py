# class Tool:
#     def __init__(self):
import os
from collections import defaultdict

from archinfo import ArchX86

from rwtools.nemesis.balance import balance
from rwtools.nemesis.code_sequence import CodeSequence

GCC_FUNCTIONS = [
    "_start",
    "__libc_start_main",
    "__libc_csu_fini",
    "__libc_csu_init",
    "__lib_csu_fini",
    "_init",
    "__libc_init_first",
    "_fini",
    "_rtld_fini",
    "_exit",
    "__get_pc_think_bx",
    "__do_global_dtors_aux",
    "__gmon_start",
    "frame_dummy",
    "__do_global_ctors_aux",
    "__register_frame_info",
    "deregister_tm_clones",
    "register_tm_clones",
    "__do_global_dtors_aux",
    "__frame_dummy_init_array_entry",
    "__init_array_start",
    "__do_global_dtors_aux_fini_array_entry",
    "__init_array_end",
    "__stack_chk_fail",
    "__cxa_atexit",
    "__cxa_finalize",
]


class BranchAnalyzer:
    def __init__(self):
        self.op_length = defaultdict(lambda x: 0)
        # self.x86 = ArchX86()
        self.x86_register_dict = {reg.name: reg for reg in ArchX86.register_list}
        self.dotfiles = []  # one string for each function that can then later be joined
        self.code_sequences = defaultdict(list)  # dictionary that maps a function to a list of code sequences

    def op_type(self, operand):
        if operand[0] == "%":
            # operand is some register
            reg_name = operand[1:]
            reg = self.x86_register_dict[reg_name]
            print(reg)

    def count_instructions(self):
        # return a dictionary that contains the number of instructions for each function (for testing purposes)
        return {fn_name: sum(len(seq.instructions) for seq in self.code_sequences[fn_name]) for fn_name in self.code_sequences.keys()}

    def generate_dot_files(self, output_dir, prefix=""):
        """
        Analye the control flow inside each of the functions, determining where branches are present and which instructions belong to the relevant branches
        Store this information inside the Function objects? Or in a seperate object?
        """
        # loop over the function names and their generated code sequences
        prefix = prefix + "_" if len("prefix") > 0 else ""
        for fn_name, code_sequences in self.code_sequences.items():
            dot_lines = []
            seq_to_i = {}
            # first crate a new node for each code sequence
            # also need to keep track of indices of the code_sequences, so that dot file is consistent
            for i, seq in enumerate(code_sequences):
                dot_lines.append(f"{i} [label=\" {seq} \"]")
                seq_to_i[seq] = i

            # then add edges between the nodes
            for seq in code_sequences:
                for next_seq in seq.branches_out:
                    i = seq_to_i[seq]
                    next_i = seq_to_i[next_seq]
                    dot_lines.append(f"{i} -> {next_i}")

            # create a dotfile by joining all the individual lines together, write to output file
            dot_string = f"digraph {fn_name}" + "{ \n node [shape=record]; \n" + "\n".join(dot_lines) + "\n }"
            dot_of = os.path.join(output_dir, f"{prefix}{fn_name}.dot")
            png_of = os.path.join(output_dir, f"{prefix}{fn_name}.png")
            with open(dot_of, "w") as f:
                f.write(dot_string)

            # conver the dotfile to png
            sh_command = f"dot -Tpng {dot_of} > {png_of}"
            os.system(sh_command)

    def analyze_latencies(self, container):
        # iterate over each function in container
        for _, fn in container.functions.items():
            if fn.name in GCC_FUNCTIONS:
                continue
            print(f"### {fn.name} ###")
            # for each function, iterate over the instructions, and determine the instruction length
            for instr in fn.cache:
                # instr is an instance of InstructionWrapper
                mnemonic = instr.mnemonic  # name of the instruction
                operands = list(map(lambda x: x.strip(), instr.op_str.split(",")))
                for op in operands:
                    op_type = self.op_type(op)
                #     self.op_type(op)
        return

    def init_code_sequences(self, container):
        # first, iterate over each function that is not a GCC function, creating initial code
        # sequences of length 1
        for _, fn in filter(lambda x: x[1].name not in GCC_FUNCTIONS, container.functions.items()):
            # the cache contains a numver of InstructionWrappers. these contain an instruction
            # as well as some extra information (mnemonic, location ,etc. ) create the initial
            # list of length 1 sequences by iterating over these
            for instr in fn.cache:
                self.code_sequences[fn.name].append(CodeSequence([instr]))

            # add branching information to the sequences
            for cache_i, next_is in fn.nexts.items():
                seq = self.code_sequences[fn.name][cache_i]
                for i in next_is:
                    if isinstance(i, int):
                        next_seq = self.code_sequences[fn.name][i]
                        seq.add_branch_out(next_seq)
                        next_seq.add_branch_in(seq)

    def analyze_control_flow(self):
        for fn_name, fn_sequences in self.code_sequences.items():
            currentSeq = fn_sequences[0]
            branches = []
            while True:
                if (len(currentSeq.branches_out)) == 0:
                    if len(branches) == 0:
                        break
                    else:
                        currentSeq = branches[0]
                        branches.remove(branches[0])
                if len(currentSeq.branches_out) == 0:
                    break
                if len(currentSeq.branches_out) > 1:
                    # if more than 2 possible next instructions, add branches to list, continue with first branch in list (breadth first)
                    branches += currentSeq.branches_out
                    currentSeq = branches[0]
                    branches.remove(branches[0])
                    continue
                else:
                    # merge the next sequence into the current sequence
                    nextSeq = currentSeq.branches_out[0]
                    if len(nextSeq.branches_in) > 1:
                        branches.append(nextSeq)
                        currentSeq = branches[0]
                        branches.remove(branches[0])
                        continue
                    currentSeq.add_instructions(nextSeq.instructions)
                    currentSeq.branches_out = nextSeq.branches_out
                    fn_sequences.remove(nextSeq)
                    continue

    def balance_branches(self, branch_targets):
        print(branch_targets)
        for fn_name, fn_sequences in self.code_sequences.items():
            targets = branch_targets[fn_name]
            print(targets)
            exit()
            currentSeq = fn_sequences[0]
            branches = []
            while True:
                if len(currentSeq.branches_out) == 2:
                    balance(*currentSeq.branches_out)
                    branches += currentSeq.branches_out
                elif len(currentSeq.branches_out) == 1:
                    branches += currentSeq.branches_out
                if len(branches) == 0:
                    # no more branches to check -- balancing done
                    break
                else:
                    currentSeq = branches[0]
                    branches.remove(currentSeq)

    def generate_graph(self):
        """
        Create a graph of NemesisNodes (that contain the code sequences) that can be balanced
        using the balancing algorithm
        """

class NemesisInstrument:
    def __init__(self, rewriter):
        # Get the register map
        self.rewriter = rewriter
        self.x86 = ArchX86()
        self.regmap = defaultdict(lambda: defaultdict(dict))

    def do_instrument(self):
        # iterate over all functions
        for _, fn in self.rewriter.container.functions.items():
            # if one of the GCC functions, skip them for now I guess
            if fn.name in self.rewriter.GCC_FUNCTIONS:
                continue
            # fn.cache contains a number of InstructionWrapper
            # for c in fn.cache:
            # c.instrument_after(Instruction())
