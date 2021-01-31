import os
import pandas as pd

if __name__ == '__main__':


        ods_file = os.path.abspath("../_data/skylave_extracted.ods")
        data = pd.read_excel(ods_file, engine="odf")
        print(data.column)

        # TODO: use tabula to import data from intel files
        # TODO: generate a dictionary from this data 