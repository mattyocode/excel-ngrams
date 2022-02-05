"""Tests cases for the file_handler module."""
import os
from unittest.mock import Mock, mock_open, patch

import click
from freezegun import freeze_time
import pandas as pd
import pytest
import xlsxwriter

from excel_ngrams.file_handler import FileHandler


# ------- Instance fixtures -------


@pytest.fixture(scope="session")
def excel_test_file() -> xlsxwriter.Workbook:
    """Helper function to create simple xlsx file for testing."""
    excel_test_file = xlsxwriter.Workbook("test_doc.xlsx")
    worksheet = excel_test_file.add_worksheet()
    terms_column = (
        "Keyword",
        "diet snacks",
        "keto snacks",
        "low carb snacks",
        "low calorie snacks",
    )
    row = 0
    col = 0

    for term in terms_column:
        worksheet.write(row, col, term)
        row += 1
    excel_test_file.close()

    yield excel_test_file

    os.remove("test_doc.xlsx")


@pytest.fixture
def file_handler(excel_test_file: xlsxwriter.Workbook) -> FileHandler:
    """Fixture returns FileHandler instance."""
    file_handler = FileHandler("test_doc.xlsx")
    return file_handler


@pytest.fixture
def file_handler_test_file() -> FileHandler:
    """Fixture returns FileHandler instance.

    FileHandler is constructed from test xlsx file
    in input_for_tests directory.

    Returns:
        :obj:`FileHandler`: Instantiated with actual Excel doc.
    """
    file_handler_test_file = FileHandler(
        "input_for_tests/test_search_listings.xlsx", column_name="Keyword"
    )
    return file_handler_test_file


# ------- File Handler tests -------


def test_gets_words_list_from_excel(file_handler: FileHandler) -> None:
    """It returns terms as list from constructed test Excel doc."""
    result = file_handler.get_terms()
    assert type(result) == list
    assert result == [
        "diet snacks",
        "keto snacks",
        "low carb snacks",
        "low calorie snacks",
    ]


def test_get_file_path(file_handler: FileHandler) -> None:
    """It gets file path from class attribute."""
    result = file_handler.get_file_path()
    assert result == "test_doc.xlsx"


@patch.object(FileHandler, "get_file_path")
def test_write_to_file_path(
    mock_get_file_path: Mock, file_handler: FileHandler
) -> None:
    """It returns expected file path from constructed test Excel doc."""
    mock_get_file_path.return_value = "test/test_path"
    with freeze_time("2020-11-22 01:02:03"):
        output = file_handler.get_destination_path()
        assert output == "test/test_path_20201122010203_n-grams"


@patch(
    "excel_ngrams.file_handler.FileHandler.get_destination_path",
    return_value="test/destination/file_date_n-grams",
)
@patch("builtins.open", new_callable=mock_open)
def test_writes_df_to_correct_path(
    mock_open: Mock, mock_destination_path: Mock, file_handler: FileHandler
) -> None:
    """It returns expected path for writing csv to."""
    empty_df = pd.DataFrame()
    result = file_handler.write(empty_df)

    assert result == "test/destination/file_date_n-grams"
    args, kwargs = mock_open.call_args
    assert "test/destination/file_date_n-grams.csv" in args


@patch("excel_ngrams.file_handler.pd")
def test_handles_errors_when_writing_file(
    mock_pandas: Mock, file_handler: FileHandler
) -> None:
    """It raises `ClickException` when writing file fails."""
    mock_pandas.side_effect = Exception("boom!")
    with pytest.raises(click.ClickException):
        file_handler.write({})


@pytest.mark.e2e
def test_write_to_file_path_actual_doc(file_handler_test_file: FileHandler) -> None:
    """It returns expected file path from test Excel doc in input_for_tests."""
    with freeze_time("2020-11-22 01:02:03"):
        output = file_handler_test_file.get_destination_path()
        expected = "input_for_tests/test_search_listings_20201122010203_n-grams"
        assert output == expected
