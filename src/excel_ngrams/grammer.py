"""Client to get ngram values from Excel document."""
import datetime
import os
from typing import Tuple, Union

import click
import nltk
import pandas as pd
import spacy


nlp = spacy.load("en_core_web_sm")


class FileHandler:
    """Class to handle reading, data extraction, and writing to files.

    Attributes:
        file_path(str): The path to Excel file to be read.
        sheet_name(int or str): The name or number of the sheet to read from.
        column_name(str): The name of the column to be read from.
            Defaults to 'Keyword'.
        term_list(list): A list of terms (read from from Excel column).

    """

    def __init__(
        self,
        file_path: str,
        sheet_name: Union[int, str] = 0,
        column_name: str = "Keyword",
    ) -> None:
        """Constructs attributes for FileHandler object."""
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.column_name = column_name
        self.term_list = self.set_terms(file_path, sheet_name, column_name)

    def set_terms(
        self, file_path: str, sheet_name: Union[int, str], column_name: str
    ) -> pd.DataFrame:
        """Sets term_list attribute from Excel doc.

        Uses Pandas DataFrame as an intermediate to generate list.

        Args:
            file_path(str): The path to Excel file to read terms from.
            sheet_name(int or str): The name or number of the sheet containing terms.
                Defaults to 0 (first sheet when sheets are unnamed).
            column_name(str): The name of the column header containing terms.
                Defaults to `Keyword`.

        Returns:
            list: Terms from Excel as Python array.

        """
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df[self.column_name].tolist()

    def get_terms(self) -> list:
        """:obj:`list` of :obj:`str`: Getter method returns terms_list."""
        return self.term_list

    def get_file_path(self) -> str:
        """str: Getter method returns Excel doc file path."""
        return self.file_path

    def get_destination_path(self) -> str:
        """Creates path to write output csv file to.

        Uses the path of the input Excel file to create an
        output path that mimics the input file name but is
        appended with the datetime and `n-grams`.

        Returns:
            str: Path to write output file to.

        """
        file_path = self.get_file_path()
        file_name = os.path.splitext(file_path)[0]
        now = datetime.datetime.now()
        date_time = now.strftime("%Y%m%d%H%M%S")
        return f"{file_name}_{date_time}_n-grams"

    def write_df_to_file(self, df: pd.DataFrame) -> str:
        """Writes DataFrame to csv file.

        Gets path from get_destination_path method and uses
        Pandas to_csv function to write DataFrame to csv file.

        Args:
            df(pd.DataFrame): Dataframe of terms and values columns
                for ngrams.

        Returns:
            str: Path to which csv file was written.
        """
        path = self.get_destination_path()
        df.to_csv(f"{path}.csv")
        return path


class Grammer:
    """Class to get n-grams from list of terms.

    Using Spacy's NLP pipe and NLTK's ngrams function to generate
    ngrams within a given range and output them to a Pandas DataFrame
    for writing to an output file.

    Attributes:
        file_handler(:obj:`FileHandler`): FileHandler obj with input file path.
        term_list: Term list from FileHandler attribute.

    """

    def __init__(self, file_handler: FileHandler) -> None:
        """Constructs attributes for Grammer object from FileHandler object."""
        self.file_handler = file_handler
        self.term_list = file_handler.get_terms()

    def get_ngrams(self, n: int, top_n_results: int = 150) -> list:
        """Create tuple with terms and frequency from list.

        List of terms is tokenised using Spacy's NLP pipe, set to lowercase
        and ngrams are calculated with NLTK's ngrams function.

        Args:
            n(int): The length of phrases to analyse.
            top_n_results(int): The number of results to return.
                Default is set to 150.

        Returns:
            :obj:`list` of :obj:`tuple`[`list` of str, int]: List of tuples
                containing term(s) and values.

        """
        word_list = []
        for doc in list(nlp.pipe(self.term_list)):
            for token in doc:
                word = token.text.lower()
                word_list.append(word)
        n_grams_series = (pd.Series(nltk.ngrams(word_list, n)).value_counts())[
            :top_n_results
        ]
        return list(zip(n_grams_series.index, n_grams_series))

    def terms_to_columns(self, tuple_list: list) -> Tuple[str, int]:
        """Returns term/value tuples as two lists.

        Args:
            tuple_list(list): List comprising :obj:`list` of
                :obj:`tuple`[:obj:`list` of :obj:`str`, int]
                Results from get_ngrams.

        Returns:
            term_col(:obj:`list` of :obj:`str`): Terms, concatinated into single string
                for multi-word terms, returned as list.
            value_col(:obj:`list` of :obj:`int`): Term frequencies as list.
            Lists are returned together as tuple containing both lists.

        """
        term_col, value_col = zip(*tuple_list)
        term_col = [" ".join(term) for term in term_col]
        value_col = list(value_col)
        return term_col, value_col

    def df_from_terms(self, tuple_list: list) -> pd.DataFrame:
        """Creates DataFrame from lists of terms and values as tuple.

        Args:
            tuple_list(list): List comprised of [:obj:`list` of :obj:`str`,
                :obj:`list` of :obj:`int`]. Results of terms_to_colums: two
                lists to comprise terms and value columns in DataFrame.

        Returns:
            df(pd.DataFrame): Pandas DataFrame comprising a column of
                terms and a column of frequency values for those terms.

        """
        term_col, value_col = self.terms_to_columns(tuple_list)
        ngram_val = len(term_col[0].split())
        terms_header = f"{ngram_val}-gram"
        freq_header = f"{ngram_val}-gram frequency"
        dict_ = {terms_header: term_col, freq_header: value_col}
        df = pd.DataFrame(dict_, columns=[terms_header, freq_header])
        return df

    def combine_dataframes(self, df_list: list) -> pd.DataFrame:
        """Creates single multi-column dataframe.

        Takes the terms and frequency values for dataframes constructed
        from ngrams of various lengths and combines them into a single
        dataframe, e.g single term and values, bigrams and values, trigrams
        and values, etc.

        Args:
            df_list(list): List of :obj:`pd.DataFrames` containing
                the dataframes to be merged, side by side.

        Returns:
            pd.DataFrame: Single combined dataframe from list of dataframes.

        """
        dfs = [df for df in df_list]
        print(pd.concat(dfs, axis=1))
        return pd.concat(dfs, axis=1)

    def ngram_range(
        self, max_n: int, n: int = 1, top_n_results: int = 150
    ) -> pd.DataFrame:
        """Gets ngram terms and outputs for a range of phrase lengths.

        Gets ngrams from single terms as default up to desired maximum
        phrase length and creates Pandas DataFrame from results.

        Args:
            max_n(int): The longest phrase length desired in output.
            n(int): The minimum term length. Default is 1 (single term).
            top_n_results(int): The number of rows of results to return.
                Default set to 150.

        Returns:
            pd.DataFrame: Combined dataframe of all results from various
                term lengths to desired maximum.

        """
        df_list = []
        for i in range(n, max_n + 1):
            ngrams_list = self.get_ngrams(i, top_n_results)
            df = self.df_from_terms(ngrams_list)
            df_list.append(df)
        if len(df_list) > 1:
            combined_dataframe = self.combine_dataframes(df_list)
            return combined_dataframe
        else:
            return df_list[0]

    def output_csv_file(self, df: pd.DataFrame) -> str:
        """Write dataframe to csv file.

        Args:
            df(pd.DataFrame): Dataframe with columns of terms
                and values.

        Returns:
            path(str): The path the csv file was written to.

        Raises:
            ClickException: Writing to csv file failed.

        """
        try:
            path = self.file_handler.write_df_to_file(df)
            return path
        except Exception as error:
            err_message = str(error)
            raise click.ClickException(err_message)
