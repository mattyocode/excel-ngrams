"""Return dataframe of ngrams from list of words."""
import re
from typing import Any, List, Sequence, Tuple

import nltk
from nltk.corpus import stopwords
import pandas as pd
import spacy


class Grammer:
    """Class that returns n-grams from text as a list of strings.

        Words are delineated by white space and punctuation.
        Using Spacy's NLP pipe and NLTK's ngrams function to generate
        ngrams within a given word length range and output them to a
        Pandas DataFrame for writing to an output file.

    Attributes:
        term_list: List of text as strings (one or more).

    _nlp and _stopwords are shared across all instances, but is loaded by the
    constructor to avoid loading is in cases where it isn't needed.

    """

    _nlp = None
    _stopwords = None

    def __init__(self, terms_list: List[str]) -> None:
        """Constructs attributes for Grammer object from FileHandler object."""
        self.term_list = terms_list

        if Grammer._nlp is None:
            try:
                Grammer._nlp = spacy.load("en")
            except OSError:
                from spacy.cli import download

                print(
                    "Downloading language model for the spaCy\n"
                    "(don't worry, this will only happen once)"
                )
                download("en")
                Grammer._nlp = spacy.load("en")

        if Grammer._stopwords is None:
            try:
                nltk.download("stopwords")
                Grammer._stopwords = set(stopwords.words("english"))
            except Exception as e:
                print(f"Error: {e}")

    def in_stop_words(self, spacy_token_text: str) -> bool:
        """Check if word appears in stopword set.

        Args:
            spacy_token_text(str): The text attribute of the Spacy
                token being passed to the method.

        Returns:
            bool: Whether text is present in stopwords.

        """
        return spacy_token_text.lower() in Grammer._stopwords

    def remove_escaped_chars(self, text: List[str]) -> List[str]:
        """Remove newline and tab chars from string list.

        Args:
            text(:obj:`List` of :obj:`str`): Terms list to be cleaned of
                specific chars.

        Returns:
            without_newlines(:obj:`List` of :obj:`str`): Terms list without
                specific chars.

        """
        without_newlines = []
        for item in text:
            item = re.sub(r"(\n*\t*)", "", item.strip())
            item = re.sub(r"’", "'", item)
            if item != "":
                without_newlines.append(item)
        return without_newlines

    def get_ngrams(
        self, n: int, top_n_results: int = 250, stopwords: bool = True
    ) -> Sequence[Tuple[Tuple[Any, ...], int]]:
        """Create tuple with terms and frequency from list.

        List of terms is tokenised using Spacy's NLP pipe, set to lowercase
        and ngrams are calculated with NLTK's ngrams function.

        Args:
            n(int): The length of phrases to analyse.
            top_n_results(int): The number of results to return.
                Default is 150.
            stopwords(bool): flag to indicate removal of stopwords.
                Default is True.

        Returns:
            :obj:`list` of :obj:`tuple`[:obj:`tuple`[str, ...], int]:
                List of tuples containing term(s) and values.

        """
        word_list = []
        term_list = self.remove_escaped_chars(self.term_list)
        for doc in list(Grammer._nlp.pipe(term_list)):
            for token in doc:
                word = token.text.lower().strip()
                if not token.is_punct:
                    if not stopwords or (stopwords and not self.in_stop_words(word)):
                        word_list.append(word)
        n_grams_series = pd.Series(nltk.ngrams(word_list, n)).value_counts()
        if top_n_results <= len(n_grams_series):
            n_grams_series = n_grams_series[:top_n_results]
        return list(zip(n_grams_series.index, n_grams_series))

    def terms_to_columns(
        self, ngram_tuples: Sequence[Tuple[Tuple[Any, ...], int]]
    ) -> Tuple[List[str], List[int]]:
        """Returns term/value tuples as two lists.

        Args:
            ngram_tuples(list): :obj:`list` of :obj:`tuple`[:obj:`tuple`
                [str], int]. Results from get_ngrams.

        Returns:
            term_col(:obj:`list` of :obj:`str`): Terms, concatinated into
                single string for multi-word terms, returned as list.
            value_col(:obj:`list` of :obj:`int`): Term frequencies as list.
            Lists are returned together as tuple containing both lists.

        """
        term_col: Tuple[str, ...]
        value_col: Tuple[Any, ...]
        term_col, value_col = zip(*ngram_tuples)
        term_col_list: List[str] = [" ".join(term) for term in term_col]
        value_col_list: List[int] = list(value_col)
        return term_col_list, value_col_list

    def df_from_terms(
        self, ngram_tuples: Sequence[Tuple[Tuple[Any, ...], int]]
    ) -> pd.DataFrame:
        """Creates DataFrame from lists of terms and values as tuple.

        Calls terms_to_columns on ngram_tuple to unpack them.

        Args:
            ngram_tuples(list): :obj:`list` of :obj:`tuple`[:obj:`tuple`
                [str], int]. Results from get_ngrams.

        Returns:
            df(pd.DataFrame): Pandas DataFrame comprising a column of
                terms and a column of frequency values for those terms.

        """
        term_col, value_col = self.terms_to_columns(ngram_tuples)
        ngram_val = len(term_col[0].split())
        terms_header = f"{ngram_val}-gram"
        freq_header = f"{ngram_val}-gram frequency"
        dict_ = {terms_header: term_col, freq_header: value_col}
        df = pd.DataFrame(dict_, columns=[terms_header, freq_header])
        return df

    def combine_dataframes(self, dataframes: List[pd.DataFrame]) -> pd.DataFrame:
        """Creates single multi-column dataframe.

        Takes the terms and frequency values for dataframes constructed
        from ngrams of various lengths and combines them into a single
        dataframe, e.g single term and values, bigrams and values, trigrams
        and values, etc.

        Args:
            dataframes(list): List of :obj:`pd.DataFrames` containing
                the dataframes to be merged, side by side.

        Returns:
            pd.DataFrame: Single combined dataframe from list of dataframes.

        """
        dfs = [df for df in dataframes]
        print(pd.concat(dfs, axis=1))
        return pd.concat(dfs, axis=1)

    def ngram_range(
        self, max_n: int, n: int = 1, top_n_results: int = 250, stopwords: bool = True
    ) -> pd.DataFrame:
        """Gets ngram terms and outputs for a range of phrase lengths.

        Gets ngrams from single terms as default up to desired maximum
        phrase length and creates Pandas DataFrame from results.

        Args:
            max_n(int): The longest phrase length desired in output.
            n(int): The minimum term length. Default is 1 (single term).
            top_n_results(int): The number of rows of results to return.
                Default set to 150.
            stopwords(bool): flag to indicate removal of stopwords.
                Default is True.

        Returns:
            pd.DataFrame: Combined dataframe of all results from various
                term lengths to desired maximum.

        """
        df_list = []
        for i in range(n, max_n + 1):
            ngrams_list = self.get_ngrams(i, top_n_results, stopwords)
            df = self.df_from_terms(ngrams_list)
            df_list.append(df)
        if len(df_list) > 1:
            combined_dataframe = self.combine_dataframes(df_list)
            return combined_dataframe
        else:
            return df_list[0]
