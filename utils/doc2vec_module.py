from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from text_preprocessor import TextPreprocessor
from data_handler import FileHandler
from sklearn.metrics.pairwise import cosine_similarity

# # open specified files and get regulatory text cols.
file_handler = FileHandler()
ref1, text1, ref2, text2 = file_handler.get_reg_texts_cols()
file1_name, file2_name = file_handler.get_files_names()

preprocessor = TextPreprocessor()
preprocessed_text1 = [preprocessor.preprocess_text(text) for text in text1]
preprocessed_text2 = [preprocessor.preprocess_text(text) for text in text2]

documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(text1)]
model = Doc2Vec(documents, vector_size=50, window=3, min_count=1, workers=4, epochs=40)

model.build_vocab(documents)
model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)


# assessing the model.
ranks = []
second_ranks = []

breakpoint()

