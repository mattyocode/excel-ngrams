"""Test cases for the console module."""
import builtins
from contextlib import contextmanager
import os
import tempfile
from unittest.mock import call, MagicMock, Mock, mock_open, patch

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


def test_main_prints_status_updates(runner, mock_file_handler, mock_grammer):
    with open('test.xlsx', 'w') as f:
        f.write('test data')
        result = runner.invoke(
            console.main, [f"--file-path=test.xlsx"]
            )
        assert 'Reading file' in result.output
        assert 'Performing n-gram analysis' in result.output
        assert 'CSV file written to' in result.output


def test_main_calls_filehandler_specified_path(runner, mock_file_handler, mock_grammer):
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


def test_main_calls_grammer_with_file_handler_instance(runner, mock_file_handler, mock_grammer):
    with open('test.xlsx', 'w') as f:
        f.write('test data')
        result = runner.invoke(
            console.main, ["--file-path=test.xlsx"]
            )
        assert result.exit_code == 0
        mock_grammer.assert_called_with(mock_file_handler())

def test_main_calls_grammer_with_default_args(runner, mock_file_handler, mock_grammer):
    with open('test.xlsx', 'w') as f:
        f.write('test data')
        result = runner.invoke(
            console.main, ["--file-path=test.xlsx"]
            )
        assert result.exit_code == 0
        instance = mock_grammer.return_value
        assert instance.ngram_range.call_args == call(5, top_n_results=150)
