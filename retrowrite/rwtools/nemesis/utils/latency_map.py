import pickle
from rwtools.nemesis.op_types import map_opcode_types
from rwtools.nemesis.utils.latency_map_utils import convert_latency, best_candidate
import os
import pandas as pd
from opcodes.x86_64 import read_instruction_set

def initialize_latency_map():
    """
    Create an initial latency map with default values based on the opcodes stored in the opcodes library
    """
    init_latency_map = dict()
    instruction_set = read_instruction_set()  # set of Instruction instances
    for instr in instruction_set:
        for form in instr.forms:
            # instances of InstructionForm -- forms mainly differen by operands
            name = form.name  # base mnemonic (i think)
            gas_name = form.gas_name  # name with possible modifiers (I think)
            operands = [map_opcode_types(op.type) for op in form.operands]
            entry_key = (name, gas_name) + tuple(operands)
            init_latency_map[entry_key] = 1

    return init_latency_map


def load_latency_data(ods_file):
    """
    Load latency data from and .osd file, apply some preprocessing to make it easier to use
    """
    raw_data = pd.read_excel(ods_file, engine="odf")
    latency_data = raw_data[['instruction', 'operands', 'latency']]
    latency_data = latency_data.drop(latency_data[latency_data.instruction.isnull()].index)

    ### Step 1 : Ensure every row has a valid latency value ###
    latency = None
    for index, row in latency_data.iterrows():
        if row.isnull().latency == False:
            converted_latency = convert_latency(row.latency)  # convert latency to a float
            assert isinstance(converted_latency, int)
            row.latency = converted_latency  # store this converted value
            latency = converted_latency  # store locally as wel
        else:
            row.latency = latency

    assert not latency_data.latency.isnull().any()

    ### Step 2 : Split up rows that contain multiple instructions seperated by spaces ###
    latency_data_cpy = latency_data.copy(deep=True)

    multi_instructions = latency_data_cpy['instruction'].str.contains(" ")

    target_rows_index = latency_data_cpy[multi_instructions].index

    new_rows = []

    for i in target_rows_index:
        row = latency_data_cpy.loc[i]
        operands = row['operands']
        latency = row['latency']
        names = list(filter(lambda x: len(x) > 0, row['instruction'].split(" ")))

        # create new rows, one for each seperate name
        new_rows += [[n, operands, latency] for n in names]

        # create a dataframe that contains the new rows
    new_data = pd.DataFrame(new_rows, columns=latency_data_cpy.columns)

    # delete the rows that have just been split up from the original dataframe
    latency_data_cpy.drop(target_rows_index, inplace=True)

    # finally, append/concatenate the dataframe containing the newly created rows
    processed_latency = pd.concat([latency_data_cpy, new_data])
    processed_latency.reset_index(drop=True)

    return processed_latency


def populate_latency_map(latency_map, latency_data):
    """
    Populate the latency map using the given latency data (extracted from some file)
    """
    for key, value in latency_map.items():
        name = key[0]  # get the instruction name
        candidates = latency_data[latency_data['instruction'].str.contains(name, case=False)] #  find all rows that potentially contain this instruction
        if len(candidates) == 0:
            continue
        # find the best match among these candidates
        best = best_candidate(key, candidates)
        best_latency = best[-1]
        latency_map[key] = best_latency
    return latency_map


def construct_latency_map():
    # create an initial latency mapping with default values
    latency_map = initialize_latency_map()

    # load the (processed) latency data from file into a pandas dataframe,
    data_file = os.path.abspath("../data1/skylave_extracted.ods")
    latency_data = load_latency_data(data_file)

    # populate the latency map using the data in the pandas dataframe
    latency_map = populate_latency_map(latency_map, latency_data)
    return latency_map


def load_latency_map():
    latency_file = os.path.abspath("../data1/pickled_latency_map.p")
    with open(latency_file, 'rb') as fp:
        l_map = pickle.load(fp)
    return l_map


if __name__ == '__main__':
    latency_map = construct_latency_map()
    latency_of = os.path.abspath("../data1/pickled_latency_map.p")
    with open(latency_of, 'wb') as fp:
        pickle.dump(latency_map, fp, protocol=pickle.HIGHEST_PROTOCOL)
