import os
from unittest.mock import Mock, mock_open, patch

import click
from freezegun import freeze_time
import pandas as pd
import pytest
import xlsxwriter

from excel_ngrams.grammer import FileHandler, Grammer


# ------- Instance fixtures -------


@pytest.fixture(scope="session")
def excel_test_file():
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
def file_handler(excel_test_file):
    excel_test_file = excel_test_file

    file_handler = FileHandler("test_doc.xlsx")
    return file_handler


@pytest.fixture
def file_handler_test_file():
    file_handler_test_file = FileHandler(
        "input_for_tests/test_search_listings.xlsx", column_name="Keyword"
    )
    return file_handler_test_file


@pytest.fixture
def grammer_instance():
    file_handler_mock = Mock()
    grammer_instance = Grammer(
        file_handler_mock,
    )
    return grammer_instance


# ------- Mock fixtures -------


@pytest.fixture
def mock_get_ngrams(mocker):
    return mocker.patch("excel_ngrams.grammer.Grammer.get_ngrams")


@pytest.fixture
def mock_terms_to_cols(mocker):
    return mocker.patch("excel_ngrams.grammer.Grammer.terms_to_columns")


@pytest.fixture
def mock_df_from_tuple_list(mocker):
    return mocker.patch("excel_ngrams.grammer.Grammer.df_from_tuple_list")


@pytest.fixture
def mock_file_handler(mocker):
    return mocker.patch("excel_ngrams.grammer.FileHandler")


# ------- File Handler tests -------


def test_gets_words_list_from_excel(file_handler):
    """It returns terms as list from constructed test Excel doc. """
    result = file_handler.get_terms()
    assert type(result) == list
    assert result == [
        "diet snacks",
        "keto snacks",
        "low carb snacks",
        "low calorie snacks",
    ]


def test_write_to_file_path_actual_doc(file_handler_test_file):
    """It returns expected file path from
    test Excel doc in input_for_tests."""
    with freeze_time("2020-11-22 01:02:03"):
        output = file_handler_test_file.get_destination_path()
        expected = "input_for_tests/test_search_listings_20201122010203_n-grams"
        assert output == expected


@patch.object(FileHandler, "get_file_path")
def test_write_to_file_path(mock_get_file_path, file_handler):
    """It returns expected file path from constructed test Excel doc."""
    mock_get_file_path.return_value = "test/test_path"
    with freeze_time("2020-11-22 01:02:03"):
        output = file_handler.get_destination_path()
        assert output == "test/test_path_20201122010203_n-grams"


@patch(
    "excel_ngrams.grammer.FileHandler.get_destination_path",
    return_value="test/destination/file_date_n-grams",
)
@patch("builtins.open", new_callable=mock_open)
def test_writes_df_to_correct_path(mock_open, mock_destination_path, file_handler):
    empty_df = pd.DataFrame()
    result = file_handler.write_df_to_file(empty_df)

    assert result == "test/destination/file_date_n-grams"
    args, kwargs = mock_open.call_args
    assert "test/destination/file_date_n-grams.csv" in args


# ------- Grammer tests -------


def test_get_single_word_frequency(grammer_instance):
    grammer_instance.term_list = [
        "best thing",
        "it's the best thing ever",
        "best day ever",
        "not the best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=1, top_n_results=1)
    assert result == [(("best",), 4)]


def test_get_bi_grams_mocked(grammer_instance):
    grammer_instance.term_list = [
        "best thing",
        "it's the best thing ever",
        "best day ever",
        "not the best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=2, top_n_results=1)
    assert result == [(("best", "thing"), 3)]


def test_get_tri_grams(grammer_instance):
    grammer_instance.term_list = [
        "best thing ever",
        "it's the best thing ever",
        "best day ever",
        "not the best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=3, top_n_results=1)
    assert result == [(("best", "thing", "ever"), 3)]


def test_get_bi_grams_from_file(file_handler):
    """It returns bigram from test file."""
    grammer_from_list = Grammer(file_handler)
    result = grammer_from_list.get_ngrams(n=2, top_n_results=1)
    assert result == [(("snacks", "low"), 2)]


def test_terms_to_columns(grammer_instance):
    tuple_list = [(("snacks", "low"), 2), (("low", "calorie"), 1)]
    output = grammer_instance.terms_to_columns(tuple_list)
    output_terms, output_values = output
    assert output_terms == ["snacks low", "low calorie"]
    assert output_values == [2, 1]


def test_tuple_list_to_dataframe(grammer_instance, mock_terms_to_cols):
    mock_terms_to_cols.return_value = ["snacks low", "low calorie"], [2, 1]
    test_tuple_list = [(("test", "thing"), 3)]
    df = grammer_instance.df_from_tuple_list(test_tuple_list)
    assert df.shape == (2, 2)
    assert df["2-gram"][0] == "snacks low"


def test_adds_to_existing_df(grammer_instance):
    existing_df = pd.DataFrame(
        {
            "2 gram": ["snacks low", "low cal"],
            "2 gram frequency": [2, 1],
        }
    )
    new_df = pd.DataFrame(
        {
            "3 gram": ["snacking more fine", "no calorie stuff"],
            "3 gram frequency": [5, 3],
        }
    )
    df = grammer_instance.combine_dataframes([existing_df, new_df])
    assert df.shape == (2, 4)


def test_adds_to_existing_df_with_unbalanced_dfs(grammer_instance):
    existing_df = pd.DataFrame(
        {
            "2 gram": ["snacks low", "low cal"],
            "2 gram frequency": [2, 1],
        }
    )
    new_df = pd.DataFrame(
        {
            "3 gram": ["snacking more fine", "no calorie stuff", "extra one added"],
            "3 gram frequency": [5, 3, 2],
        }
    )
    df = grammer_instance.combine_dataframes([existing_df, new_df])
    assert df.shape == (3, 4)


def test_ngram_range_single_word_only(
    grammer_instance, mock_get_ngrams, mock_df_from_tuple_list
):
    mock_df_from_tuple_list.return_value = pd.DataFrame(
        {
            "2 gram": ["snacks low", "low cal"],
            "2 gram frequency": [2, 1],
        }
    )
    output_df = grammer_instance.ngram_range(1)
    assert len(output_df.columns) == 2
    assert mock_get_ngrams.call_count == 1


def test_ngram_range_2_gram(grammer_instance, mock_get_ngrams, mock_df_from_tuple_list):
    mock_df_from_tuple_list.return_value = pd.DataFrame(
        {
            "2 gram": ["snacks low", "low cal"],
            "2 gram frequency": [2, 1],
        }
    )
    output_df = grammer_instance.ngram_range(2)
    assert len(output_df.columns) == 4
    assert mock_get_ngrams.call_count == 2


def test_ngram_range_3_gram(grammer_instance, mock_get_ngrams, mock_df_from_tuple_list):
    dataframe_return_values = [
        pd.DataFrame(
            {
                "1 gram": ["low", "snacks"],
                "1 gram frequency": [2, 1],
            }
        ),
        pd.DataFrame(
            {
                "2 gram": ["snacks low", "low cal"],
                "2 gram frequency": [2, 1],
            }
        ),
        pd.DataFrame(
            {
                "3 gram": ["big snacks low", "low cal time"],
                "3 gram frequency": [7, 3],
            }
        ),
    ]
    mock_df_from_tuple_list.side_effect = dataframe_return_values
    output_df = grammer_instance.ngram_range(3)
    assert len(output_df.columns) == 6
    assert mock_get_ngrams.call_count == 3


def test_grammer_returns_path_after_writing_file(mock_file_handler):
    """It returns path with no exception is raised."""
    mock_file_handler.write_df_to_file.return_value = "fake/path/file.csv"
    grammer_instance = Grammer(mock_file_handler)
    output = grammer_instance.output_csv_file("df")
    assert output == "fake/path/file.csv"


def test_grammer_handles_writing_file_errors(mock_file_handler):
    """It raises `ClickException` when writing file fails."""
    mock_file_handler.write_df_to_file.side_effect = Exception("boom!")
    grammer_instance = Grammer(mock_file_handler)
    with pytest.raises(click.ClickException):
        grammer_instance.output_csv_file("df")
