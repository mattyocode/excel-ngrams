"""Test cases for the console module."""
import builtins
from contextlib import contextmanager
import os
import tempfile
from unittest.mock import MagicMock, Mock, mock_open, patch

import click
import click.testing
from click.testing import CliRunner
import pytest
from pytest_mock import MockFixture
import xlsxwriter

from excel_ngrams import console


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return click.testing.CliRunner()


@pytest.fixture
def mock_file_handler(mocker):
    """Fixture for mocking FileHandler."""
    return mocker.patch("excel_ngrams.console.FileHandler")


@pytest.fixture
def mock_grammer(mocker):
    """Fixture for mocking Grammer."""
    return mocker.patch("excel_ngrams.console.Grammer")


# @pytest.fixture
# def fake_excel_file():
#     """Fixture for creating fake excel file."""
#     tmp = tempfile.NamedTemporaryFile('w+t')
#     tmp.name = 'file.xlsx'
#     yield tmp
#     tmp.close()


def test_file_mocking(runner):
    """It exits with a status code of zero."""
    with patch('builtins.open', mock_open(read_data="test")) as mock_file:
        assert open("path/to/open").read() == "test"
        mock_file.assert_called_with("path/to/open")

@pytest.mark.skip("end2end")
def test_main_succeeds_end_to_end(runner):
    result = runner.invoke(
        console.main, ["--file-path=input/test_search_listings.xlsx"]
        )
    assert result.exit_code == 0


def test_main_succeeds(runner, mock_file_handler, mock_grammer):
    with open('test.xlsx', 'w') as f:
        f.write('test data')
        result = runner.invoke(
            console.main, [f"--file-path=test.xlsx"]
            )
        assert result.exit_code == 0
        mock_file_handler.assert_called_with(
            file_path=f'test.xlsx',
            sheet_name=0,
            column_name='Keyword')


def test_main_prints_status_updates(runner, mock_file_handler, mock_grammer):
    with open('test.xlsx', 'w') as f:
        f.write('test data')
        result = runner.invoke(
            console.main, [f"--file-path=test.xlsx"]
            )
        assert 'Reading file' in result.output
        assert 'Performing n-gram analysis' in result.output
        assert 'CSV file written to' in result.output


# @patch('os.path.isfile')
# def test_main_succeeds(mock_os_is_file, runner, mock_file_handler, mock_grammer):
#     """It exits with a status code of zero."""
#     mock_os_is_file.return_value = True
#     with patch('builtins.open', mock_open(read_data="test")) as mock_file:
#         result = runner.invoke(
#             console.main, ["--file-path=input/test_search_listings.xlsx"]
#             )
#         print(result.exception)
#         mock_file_handler.assert_called_with(file_path='path/fake.xlsx')
#         assert result.exit_code == 0


            # mock_grammer.ngram_range.return_value = "dataframe"
            # mock_grammer.output_csv_file.return_value = "fake.xlsx"
            # result = runner.invoke(console.main, ["--file-path=fake.xlsx"])
            # print(result.exception)
            # assert result.exit_code == 0
