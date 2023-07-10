import yake
from typing import List, Tuple, Iterable


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

    def find_kw_matching_docs(self, corpus1: Iterable, corpus2: Iterable) -> Tuple:
        print("Extracting key words from corpus2")
        key_phrases = [self.__extract_keywords(doc) for doc in corpus2]

        print("Getting matching key phrases in corpus1")
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
        print("key phrase matching complete")
        num_kp_matches = sum(len(ls) for ls in kp_matched_docs)
        print(f"Number of documents with matching key phrases across corpus 1 and corpus 2: {num_kp_matches}")

        return kp_matched_docs, num_kp_matches

