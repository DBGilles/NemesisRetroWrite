import os

from librw.loader import Loader
from librw.rw import Rewriter
from rwtools.nemesis.nemesistool import NemesisInstrument, BranchAnalyzer

if __name__ == '__main__':
    binary = "/home/gilles/git-repos/thesis_v2/src/print"
    bin_name = binary.split("/")[-1]
    output_dir = f"output/{bin_name}"
    os.makedirs(name=output_dir, exist_ok=True)
    outfile = f"./{bin_name}.s"

    loader = Loader(binary)
    assert (loader.is_pie() and not loader.is_stripped())

    # get a dictionary mapping function id's to a dictionary containing metadata  to
    flist = loader.flist_from_symtab()
    loader.load_functions(flist)  # load functions into the container

    slist = loader.slist_from_symtab()  # get a list of all sections (?)
    loader.load_data_sections(slist, lambda x: x in Rewriter.DATASECTIONS)  # load all data sections into container (sections for which lamda func returns true)

    reloc_list = loader.reloc_list_from_symtab()  # get a list of relocations
    loader.load_relocations(reloc_list)  # prints 'warning' (?) -- [*] Relocations for a section that's not loaded: .rela.dyn

    global_list = loader.global_data_list_from_symtab()
    loader.load_globals_from_glist(global_list)

    loader.container.attach_loader(loader)
    # container is a class that contains dictionaries mapping sections to their attributes and a bunch of function
    # create a Rewriter with access to this container (i.e. with access to information about the various sections)
    rw = Rewriter(loader.container, outfile)
    rw.symbolize()

    branch_analyzer = BranchAnalyzer()

    # create initial (atomic) code sequences
    branch_analyzer.init_code_sequences(loader.container)
    branch_analyzer.generate_dot_files(output_dir=f"output/{bin_name}", prefix="orig")

    # # analyze the control flow, merging code sequences
    # branch_analyzer.analyze_control_flow()
    # branch_analyzer.generate_dot_files(output_dir=f"output/{bin_name}", prefix="merged")
    #
    # branch_analyzer.balance_branches()
    # branch_analyzer.generate_dot_files(output_dir=f"output/{bin_name}", prefix="balanced")

    # analyze the latency in each code sequence
    # branch_analyzer.analyze_branch_latencies()

    # instrumenter = NemesisInstrument(rw)
    # instrumenter.do_instrument()

    # rw.dump()
