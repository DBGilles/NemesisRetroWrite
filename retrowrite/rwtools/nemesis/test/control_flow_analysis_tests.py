import os
import unittest

from librw.loader import Loader
from librw.rw import Rewriter
from rwtools.nemesis.nemesistool import BranchAnalyzer


class TestPrint(unittest.TestCase):
    def setUp(self):
        binary = "/home/gilles/git-repos/thesis_v2/src/print"

        loader = Loader(binary)
        assert (loader.is_pie() and not loader.is_stripped())

        # get a dictionary mapping function id's to a dictionary containing metadata  to
        flist = loader.flist_from_symtab()
        loader.load_functions(flist)  # load functions into the container

        slist = loader.slist_from_symtab()  # get a list of all sections (?)
        loader.load_data_sections(slist,
                                  lambda x: x in Rewriter.DATASECTIONS)  # load all data sections into container (sections for which lamda func returns true)

        reloc_list = loader.reloc_list_from_symtab()  # get a list of relocations
        loader.load_relocations(reloc_list)  # prints 'warning' (?) -- [*] Relocations for a section that's not loaded: .rela.dyn

        global_list = loader.global_data_list_from_symtab()
        loader.load_globals_from_glist(global_list)

        loader.container.attach_loader(loader)
        # container is a class that contains dictionaries mapping sections to their attributes and a bunch of function
        # create a Rewriter with access to this container (i.e. with access to information about the various sections)
        rw = Rewriter(loader.container, outfile="")
        rw.symbolize()

        self.branch_analyzer = BranchAnalyzer()
        self.container = loader.container

    def extract_control_flow(self):
        control_flow = {}
        for fn_name, code_seqs in self.branch_analyzer.code_sequences.items():
            next_seq = {}
            for seq in code_seqs:
                next_seq[seq] = seq.branches_out
            control_flow[fn_name] = next_seq
        return control_flow

    # def test_merge(self):
    #     self.branch_analyzer.init_code_sequences(self.container)
    #     counts_before = self.branch_analyzer.count_instructions()
    #     control_flow_before = self.extract_control_flow()
    #
    #     self.branch_analyzer.analyze_control_flow(self.container)
    #
    #     counts_after = self.branch_analyzer.count_instructions()
    #     control_flow_after = self.extract_control_flow()
    #
    #     # verify no functions have been removed
    #     self.assertEqual(counts_before.keys(), counts_after.keys())
    #
    #     # verify no instructions have been added/deleted
    #     for fn_name in counts_before.keys():
    #         self.assertEqual(counts_before[fn_name], counts_after[fn_name])
    #
