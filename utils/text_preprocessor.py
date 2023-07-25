import string

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


class TextPreprocessor:
    def __init__(self):
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.stemmer = PorterStemmer()

    def preprocess_text(self, text) -> str:

        # convert input text to lower.
        corpus = text.lower()
        # get stopwords and punctuation to remove them.
        stop_set = stopwords.words('english') + list(string.punctuation)
        # remove stop set and lemmatize the text.
        # corpus = " ".join(self.stemmer.stem(i) for i in self.tokenizer.tokenize(corpus) if i not in stop_set)
        corpus = " ".join(i for i in self.tokenizer.tokenize(corpus) if i not in stop_set)

        return corpus

    def tokenize_text(self, text) -> list:
        # tokenize the text.
        corpus = self.preprocess_text(text)
        tokenized_corpus = self.tokenizer.tokenize(corpus)
        return tokenized_corpus
