"""Return list of words from column in spreadsheet."""
import datetime
import os
from typing import List, Union

import click
import pandas as pd


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
    ) -> List[str]:
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
        return df[column_name].tolist()

    def get_terms(self) -> List[str]:
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

    def write(self, df: pd.DataFrame) -> str:
        """Writes DataFrame to csv file.

        Gets path from get_destination_path method and use
        Pandas to_csv function to write DataFrame to csv file.

        Args:
            df(pd.DataFrame): Dataframe of terms and values columns
                for ngrams.

        Returns:
            str: Path to which csv file was written.

        Raises:
            ClickException: Writing to csv file failed.
        """
        try:
            path = self.get_destination_path()
            df.to_csv(f"{path}.csv")
            return path
        except Exception as error:
            err_message = str(error)
            raise click.ClickException(err_message) from None
