import spacy
import nltk
import pandas as pd

nlp = spacy.load("en_core_web_sm")

class Grammer:

    def word_list_from_excel_doc(self, path, column_name):
        df = pd.read_excel(path)
        return df[column_name].tolist()


    def get_n_grams(self, term_list, n, top_n=10, lemma=False):
        word_list = []
        for doc in list(nlp.pipe(term_list)):
            for token in doc:
                if lemma:
                    word = token.lemma_.lower()
                else:
                    word = token.text.lower()
                word_list.append(word)

        n_grams_series = (pd.Series(nltk.ngrams(word_list, n)).value_counts())[:top_n]
        return list(zip(n_grams_series.index, n_grams_series))