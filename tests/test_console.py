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

@pytest.fixture
def fake_excel_file():
    with open('test.xlsx', 'w') as f:
        yield f
    os.remove('test.xlsx')
    

@pytest.mark.skip("end2end")
def test_main_succeeds_end_to_end(runner):
    result = runner.invoke(
        console.main, ["--file-path=input/test_search_listings.xlsx"]
        )
    assert result.exit_code == 0


def test_main_succeeds(runner, mock_file_handler, mock_grammer, fake_excel_file):
    result = runner.invoke(
        console.main, [f"--file-path=test.xlsx"]
        )
    assert result.exit_code == 0


def test_main_prints_status_updates(runner, mock_file_handler, mock_grammer, fake_excel_file):
    result = runner.invoke(
        console.main, [f"--file-path=test.xlsx"]
        )
    assert 'Reading file' in result.output
    assert 'Performing n-gram analysis' in result.output
    assert 'CSV file written to' in result.output


def test_main_calls_filehandler_specified_path(runner, mock_file_handler, mock_grammer, fake_excel_file):
    result = runner.invoke(
        console.main, [f"--file-path=test.xlsx"]
        )
    assert result.exit_code == 0
    mock_file_handler.assert_called_with(
        file_path=f'test.xlsx',
        sheet_name=0,
        column_name='Keyword')


def test_main_calls_grammer_with_file_handler_instance(runner, mock_file_handler, mock_grammer, fake_excel_file):
    result = runner.invoke(
        console.main, ["--file-path=test.xlsx"]
        )
    assert result.exit_code == 0
    mock_grammer.assert_called_with(mock_file_handler())

def test_main_calls_grammer_with_default_args(runner, mock_file_handler, mock_grammer, fake_excel_file):
    result = runner.invoke(
        console.main, ["--file-path=test.xlsx"]
        )
    assert result.exit_code == 0
    instance = mock_grammer.return_value
    assert instance.ngram_range.call_args == call(5, top_n_results=150)


def test_main_fails_on_non_existent_path(runner):
    # mock_file_handler.side_effect = Exception("Problemo!")
    result = runner.invoke(
        console.main, ["--file-path=doesnt_exist.xlsx"]
        )
    assert result.exit_code == 2


def test_main_fails_prints_error_on_non_existent_path(runner):
    # mock_file_handler.side_effect = Exception("Problemo!")
    result = runner.invoke(
        console.main, ["--file-path=doesnt_exist.xlsx"]
        )
    assert "Error: Invalid value" in result.output
