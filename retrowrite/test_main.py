import os

from librw.loader import Loader
from librw.rw import Rewriter
from rwtools.nemesis.control_flow_graph import ControlFlowGraph
from rwtools.nemesis.load_branching_targets import target_branches_from_json
from rwtools.nemesis.nemesistool import NemesisInstrument, BranchAnalyzer
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


def to_png(graph, out_dir="", name="temp"):
    dot_out = os.path.abspath(os.path.join(out_dir, f"./{name}.dot"))
    png_out = os.path.abspath(os.path.join(out_dir, f"./{name}.png"))
    if len(out_dir) > 0:
        os.makedirs(out_dir, exist_ok=True)
    nx.drawing.nx_agraph.write_dot(graph, dot_out)
    cmd = f"dot -Tpng {dot_out} -o {png_out}"
    os.system(cmd)


if __name__ == '__main__':
    binary = "/home/gilles/git-repos/NemesisRetroWrite/src/simple"
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
    # load all data sections into container (sections for which lamda func returns true)
    loader.load_data_sections(slist, lambda x: x in Rewriter.DATASECTIONS)

    reloc_list = loader.reloc_list_from_symtab()  # get a list of relocations
    loader.load_relocations(reloc_list)

    global_list = loader.global_data_list_from_symtab()
    loader.load_globals_from_glist(global_list)

    loader.container.attach_loader(loader)
    # container is a class that contains dictionaries mapping sections to their attributes and
    # a bunch of function create a Rewriter with access to this container (i.e. with access to
    # information about the various sections)
    rw = Rewriter(loader.container, outfile)
    rw.symbolize()

    control_flow_graph = ControlFlowGraph()
    control_flow_graph.initialize_cfg(loader.container)

    to_png(control_flow_graph.graph, out_dir="test_out", name="original")

    control_flow_graph.merge_consecutive_nodes()
    to_png(control_flow_graph.graph, out_dir="test_out", name="merged")

    branch_targets = {
        'main': ['1146']
    }

    control_flow_graph.balance_branches(branch_targets)
    to_png(control_flow_graph.graph, out_dir="test_out", name="balanced")

    instrumenter = NemesisInstrument(rw)
    instrumenter.do_instrument()

    rw.dump()
