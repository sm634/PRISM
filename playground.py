from utils.text_preprocessor import TextPreprocessor
from utils.data_handler import FileHandler
from utils.key_phrase_extractor import Extractor

# # open specified files and get regulatory text cols.
file_handler = FileHandler()
ref1, text1, ref2, text2 = file_handler.get_reg_texts_cols()
file1_name, file2_name = file_handler.get_files_names()

print("preprocessing regulation texts")
preprocessor = TextPreprocessor()
preprocessed_text1 = [preprocessor.preprocess_text(text) for text in text1]
preprocessed_text2 = [preprocessor.preprocess_text(text) for text in text2]

# key phrase extractor
# get key phrases from reg text 2.
print("Extracting key phrases from regulation text 2")
kp_extractor = Extractor()

# extract key phrases from corpus 1 and find matching documents in corpus 2.
matching_docs, num_of_matching_kp = kp_extractor.find_kw_matching_docs(preprocessed_text1, preprocessed_text2)

breakpoint()
