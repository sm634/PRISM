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


reg2_kp = []
for doc in preprocessed_text2:
    reg2_kp.append(kp_extractor.extract_keywords(doc))


print("Getting matching key phrases in regulation text 1")
kp_matched_docs = []
for i, kp_doc in enumerate(reg2_kp):
    matched_docs = []
    for j, doc in enumerate(preprocessed_text1):
        if any(string in doc for string in kp_doc):
            count = sum(el in doc for el in kp_doc)
            matched_docs.append((i, j, count))

    kp_matched_docs.append(matched_docs)
# # sorted key phrase matching docs.
kp_matched_docs = [sorted(kp_matched, key=lambda x: x[2], reverse=True) for kp_matched in kp_matched_docs]
num_kp_matches = sum(len(ls) for ls in kp_matched_docs)


print("key phrase matching complete")
breakpoint()
