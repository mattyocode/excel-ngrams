from functools import cached_property

import spacy
import nltk
import numpy as np
import pandas as pd

nlp = spacy.load("en_core_web_sm")


class FileToList:

    def __init__(self, path, column_name):
        self.path = path
        self.column_name = column_name
        self.term_list = self.set_terms(path, column_name)

    def set_terms(self, path, column_name):
        df = pd.read_excel(self.path)
        return df[self.column_name].tolist()

    def get_terms(self):
        return self.term_list

    def get_path(self):
        return self.path

class Grammer:

    def __init__(self, file_to_list):
        self.file_path = file_to_list.get_path()
        self.term_list = file_to_list.get_terms()

    def get_ngrams(self, n, top_n=100):
        word_list = []
        for doc in list(nlp.pipe(self.term_list)):
            for token in doc:
                word = token.text.lower()
                word_list.append(word)
        n_grams_series = (
            pd.Series(nltk.ngrams(word_list, n)).value_counts()
            )[:top_n]
        return list(zip(n_grams_series.index, n_grams_series))

    def terms_to_columns(self, tuple_list):
        term_col, value_col = zip(*tuple_list)
        term_col = [' '.join(term) for term in term_col]
        value_col = list(value_col)
        return term_col, value_col

    def df_from_tuple_list(self, tuple_list):
        term_col, value_col = self.terms_to_columns(tuple_list)
        ngram_val = len(term_col[0].split())
        terms_header = f'{ngram_val}-gram'
        freq_header = f'{ngram_val}-gram frequency'
        dict_ = {terms_header: term_col,
                freq_header: value_col}
        df = pd.DataFrame(dict_, columns=[terms_header, freq_header])
        return df

    def combine_dataframes(self, df_list):
        # existing_df = existing_df.reset_index()
        # new_df = new_df.reset_index()
        df = df_list
        print(pd.concat(df, axis=1))
        return pd.concat(df, axis=1)

    def ngram_range(self, max_n):
        df_list = []
        for i in range(2, max_n + 1):
            ngrams_list = self.get_ngrams(i)
            df = self.df_from_tuple_list(ngrams_list)
            df_list.append(df)
        if len(df_list) > 1:
            combined_dataframe = self.combine_dataframes(df_list)
            return combined_dataframe
        else:
            return df_list[0]


    #     ngrams_range = dict()
    #     for i in range(2, max_n+1):
    #         ngrams_i = self.get_ngrams(i)
    #         ngrams_range[i] = ngrams_i
    #     return ngrams_range