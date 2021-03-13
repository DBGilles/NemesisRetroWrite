# class Tool:
#     def __init__(self):
import os
from collections import defaultdict

from archinfo import ArchX86

from rwtools.nemesis.balance import balance

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
