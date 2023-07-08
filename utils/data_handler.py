import pandas as pd
import re


class FileHandler:
    def __init__(self):
        self.ref_mapping_files_path = 'reference_docs/input_files.txt'

    def __get_files_to_map(self):
        """Return files to map in a list based on reference doc file script."""
        with open(self.ref_mapping_files_path, 'r') as f:
            files = f.read()
            files_list = files.split(',')
            f.close()

        file1, file2 = files_list[0], files_list[1]
        return file1, file2

    def __open_mapping_files(self):
        file1, file2 = self.__get_files_to_map()

        reg1_data = pd.read_excel(f'data/input/{file1}', sheet_name=0)
        reg2_data = pd.read_excel(f'data/input/{file2}', sheet_name=0)

        return reg1_data, reg2_data

    def get_files_names(self):
        file1, file2 = self.__get_files_to_map()
        file1_name = re.sub(r"\..+", "", file1)
        file2_name = re.sub(r"\..+", "", file2)

        return file1_name, file2_name

    def get_reg_texts_cols(self):
        """
        Return an array of reference numbers and regulatory texts for regulations 1 and 2.
        :return: 4-tuple[array] of ref1, text1, ref2, text2.
        """
        regulation1, regulation2 = self.__open_mapping_files()

        regulation_ref1_col = regulation1[regulation1.columns[0]]
        regulation_text1_col = regulation1.columns[1]
        regulation1_text = regulation1[
            regulation_text1_col].apply(lambda x: x.replace('\n', ''))
        # free up memory
        del regulation1

        regulation_ref2_col = regulation2[regulation2.columns[0]]
        regulation_text2_col = regulation2.columns[1]
        regulation2_text = regulation2[
            regulation_text2_col].apply(lambda x: x.replace('\n', ''))
        # free up memory.
        del regulation2

        return regulation_ref1_col, regulation1_text, regulation_ref2_col, regulation2_text
