import yake
from typing import List, Tuple, Iterable
from utils.text_preprocessor import TextPreprocessor


class Extractor:
    def __init__(self, extractor='key_word',
                 language="en",
                 max_word_size=2,
                 duplicate_limit=0.9,
                 num_keywords=10,
                 features=None):

        if extractor == 'key_word':
            self.kw_extractor = yake.KeywordExtractor(lan=language,
                                                      n=max_word_size,
                                                      dedupLim=duplicate_limit,
                                                      top=num_keywords,
                                                      features=features)

    def __extract_keywords(self, text: str) -> List:
        key_words_list_tuple = self.kw_extractor.extract_keywords(text)
        key_words = [i[0] for i in key_words_list_tuple]
        return key_words

    def __find_kw_matching_docs(self, corpus1: Iterable, corpus2: Iterable) -> Tuple:

        key_phrases = [self.__extract_keywords(doc) for doc in corpus2]

        kp_matched_docs = []
        for i, kp_doc in enumerate(key_phrases):
            matched_docs = []
            for j, doc in enumerate(corpus1):
                if any(string in doc for string in kp_doc):
                    count = sum(el in doc for el in kp_doc)
                    matched_docs.append((i, j, count))

            kp_matched_docs.append(matched_docs)
        # # sorted key phrase matching docs.
        kp_matched_docs = [sorted(kp_matched, key=lambda x: x[2], reverse=True) for kp_matched in kp_matched_docs]

        num_kp_matches = sum(len(ls) for ls in kp_matched_docs)

        return kp_matched_docs, num_kp_matches

    def get_matching_records(self, corpus1: List, corpus2: List, ref1: List, ref2: List, log=True):
        """A function that is used to get documents amongst two corpus to that contain relevant key words."""

        # calculation to understand numbers of docs.
        total_docs = len(corpus1) * len(corpus2)

        if log:
            print("preprocessing regulation texts")
        preprocessor = TextPreprocessor()
        preprocessed_corpus1 = [preprocessor.preprocess_text(text) for text in corpus1]
        preprocessed_corpus2 = [preprocessor.preprocess_text(text) for text in corpus2]

        # This returns a List[List[Tuple]], where the first list contains all comparisons between corpus 1 and 2
        # for key word searches. The list within the list contains all key word matches in a particular document
        # belonging to corpus 2 that is also found in corpus 1. The tuple consists of:
        # (document index of corpus 2, document index of corpus 1, count of kw matches).
        kp_matched_docs, num_kp_matches = self.__find_kw_matching_docs(preprocessed_corpus1, preprocessed_corpus2)

        if log:
            print(f"Number of documents with matching key phrases across corpus 1 and corpus 2: {num_kp_matches}"
                  f" out of a possible {total_docs} comparisons.\n")

        filtered_corpus1 = {}
        filtered_corpus2 = {}
        non_matched_refs = []

        for i, match in enumerate(kp_matched_docs):
            if len(match) < 1:
                non_matched_refs.append(ref2[i])
            for doc in match:
                """The second corpus exists in the 1st tuple position, while the first exists in the second."""
                filtered_corpus2[ref2[doc[0]]] = corpus2[doc[0]]
                filtered_corpus1[ref1[doc[1]]] = corpus1[doc[1]]
        if log:
            print("Corpus 1 and 2 filtered to extract matching documents based on key phrase extraction.\n")
        return filtered_corpus1, filtered_corpus2, non_matched_refs
