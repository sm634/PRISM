import yake
from typing import List


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

    def extract_keywords(self, text: str) -> List:
        key_words_list_tuple = self.kw_extractor.extract_keywords(text)
        key_words = [i[0] for i in key_words_list_tuple]
        return key_words


