
def is_branch(mnemonic):
    branch_insn = ["jmp", "je", "jne", "jge"]
    return True in [inst in mnemonic for inst in branch_insn]