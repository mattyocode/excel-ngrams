import os
import datetime
import re

import spacy
import nltk
import numpy as np
import pandas as pd

nlp = spacy.load("en_core_web_sm")


class FileHandler:

    def __init__(self, file_path, sheet_name=0, column_name="Keyword"):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.column_name = column_name
        self.term_list = self.set_terms(
            file_path, sheet_name, column_name)

    def set_terms(self, file_path, sheet_name, column_name):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df[self.column_name].tolist()

    def get_terms(self):
        return self.term_list

    def get_file_path(self):
        return self.file_path

    def get_destination_path(self):
        file_name = os.path.splitext(self.file_path)[0]
        now = datetime.datetime.now()
        date_time = now.strftime("%Y%m%d%H%M%S")
        return f"{file_name}_{date_time}_n-grams"

    def write_df_to_file(self, df):
        path = self.get_destination_path()
        df.to_csv(f"{path}.csv")
        return path


class Grammer:

    def __init__(self, file_handler):
        self.file_handler = file_handler
        self.file_path = file_handler.get_file_path()
        self.term_list = file_handler.get_terms()

    def get_ngrams(self, n, top_n_results=150):
        word_list = []
        for doc in list(nlp.pipe(self.term_list)):
            for token in doc:
                word = token.text.lower()
                word_list.append(word)
        n_grams_series = (
            pd.Series(nltk.ngrams(word_list, n)).value_counts()
            )[:top_n_results]
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
        dfs = [df for df in df_list]
        print(pd.concat(dfs, axis=1))
        return pd.concat(dfs, axis=1)

    def ngram_range(self, max_n, top_n_results=150):
        df_list = []
        for i in range(2, max_n + 1):
            ngrams_list = self.get_ngrams(i, top_n_results)
            df = self.df_from_tuple_list(ngrams_list)
            df_list.append(df)
        if len(df_list) > 1:
            combined_dataframe = self.combine_dataframes(df_list)
            return combined_dataframe
        else:
            return df_list[0]

    def output_csv_file(self, df):
        try:
            path = self.file_handler.write_df_to_file(df)
            return path
        except Exception as e:
            return f'Error: {e}'