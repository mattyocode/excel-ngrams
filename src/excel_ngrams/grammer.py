from functools import cached_property

import spacy
import nltk
import pandas as pd

nlp = spacy.load("en_core_web_sm")

class Grammer:

    def __init__(self, path, column_name):
        self.path = path
        self.column_name = column_name

    @cached_property
    def term_list(self):
        df = pd.read_excel(self.path)
        return df[self.column_name].tolist()


    def get_ngrams(self, n, term_list=term_list, top_n=100):
        word_list = []
        for doc in list(nlp.pipe(term_list)):
            for token in doc:
                word = token.text.lower()
                word_list.append(word)

        n_grams_series = (
            pd.Series(nltk.ngrams(word_list, n)).value_counts()
            )[:top_n]
        return list(zip(n_grams_series.index, n_grams_series))

    def ngram_range(self, max_n, term_list=term_list):
        ngrams_range = dict()
        for i in range(2, max_n+1):
            ngrams_i = self.get_ngrams(i, term_list)
            ngrams_range[i] = ngrams_i
        print(ngrams_range)
        return ngrams_range

    