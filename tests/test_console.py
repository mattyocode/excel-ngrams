"""Test cases for the console module."""
import os
from typing import Generator, TextIO
from unittest.mock import call, Mock

import click
import click.testing
from click.testing import CliRunner
from freezegun import freeze_time
import pytest
from pytest_mock import MockFixture

from excel_ngrams import console


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return click.testing.CliRunner()


@pytest.fixture
def mock_file_handler(mocker: MockFixture) -> Mock:
    """Fixture for mocking FileHandler."""
    return mocker.patch("excel_ngrams.console.FileHandler")


@pytest.fixture
def mock_grammer(mocker: MockFixture) -> Mock:
    """Fixture for mocking Grammer."""
    return mocker.patch("excel_ngrams.console.Grammer")


@pytest.fixture(scope="session")
def fake_excel_file() -> Generator[TextIO, None, None]:
    """It returns an empty TextIO file with xlsx extension."""
    with open("test.xlsx", "w") as f:
        yield f
    os.remove("test.xlsx")


def test_main_succeeds(
    runner: CliRunner,
    mock_file_handler: Mock,
    mock_grammer: Mock,
    fake_excel_file: TextIO,
) -> None:
    """It exits with status code of zero."""
    result = runner.invoke(console.main, ["--file-path=test.xlsx"])
    assert result.exit_code == 0


def test_main_prints_status_updates(
    runner: CliRunner,
    mock_file_handler: Mock,
    mock_grammer: Mock,
    fake_excel_file: TextIO,
) -> None:
    """It prints update messages."""
    result = runner.invoke(console.main, ["--file-path=test.xlsx"])
    assert "Reading file" in result.output
    assert "Performing n-gram analysis" in result.output
    assert "CSV file written to" in result.output


def test_main_calls_filehandler_specified_path(
    runner: CliRunner,
    mock_file_handler: Mock,
    mock_grammer: Mock,
    fake_excel_file: TextIO,
) -> None:
    """It passes CLI args and defaults to FileHandler instance."""
    result = runner.invoke(console.main, ["--file-path=test.xlsx"])
    assert result.exit_code == 0
    mock_file_handler.assert_called_with(
        file_path="test.xlsx", sheet_name=0, column_name="Keyword"
    )


def test_main_calls_grammer(
    runner: CliRunner,
    mock_file_handler: Mock,
    mock_grammer: Mock,
    fake_excel_file: TextIO,
) -> None:
    """It passes FileHandler instance to Grammer."""
    result = runner.invoke(console.main, ["--file-path=test.xlsx"])
    assert result.exit_code == 0
    mock_grammer.assert_called_once()


def test_main_calls_grammer_with_default_args(
    runner: CliRunner,
    mock_file_handler: Mock,
    mock_grammer: Mock,
    fake_excel_file: TextIO,
) -> None:
    """It passes default args to Grammer instance."""
    result = runner.invoke(console.main, ["--file-path=test.xlsx"])
    assert result.exit_code == 0
    instance = mock_grammer.return_value
    assert instance.ngram_range.call_args == call(5, top_n_results=250, stopwords=True)


def test_main_fails_on_non_existent_path(runner: CliRunner) -> None:
    """It exits with status code of zero if file path doesn't exist."""
    result = runner.invoke(console.main, ["--file-path=doesnt_exist.xlsx"])
    assert result.exit_code == 2


def test_main_fails_prints_error_on_non_existent_path(runner: CliRunner) -> None:
    """It prints error when file path doesn't exist."""
    result = runner.invoke(console.main, ["--file-path=doesnt_exist.xlsx"])
    assert "Error: Invalid value" in result.output


def test_main_fails_on_grammer_error(
    runner: CliRunner,
    mock_file_handler: Mock,
    mock_grammer: Mock,
    fake_excel_file: TextIO,
) -> None:
    """It fails on error from Grammer instance."""
    mock_grammer.side_effect = Exception("Problemo!")
    result = runner.invoke(console.main, ["--file-path=test.xlsx"])
    assert result.exit_code == 1


@pytest.mark.skip("e2e test creates and deletes output file - doesn't run by default")
@pytest.mark.e2e
def test_main_succeeds_end_to_end(runner: CliRunner) -> None:
    """It exits with a status code of zero (end-to-end)."""
    with freeze_time("2020-11-22 01:02:03"):
        result = runner.invoke(
            console.main, ["--file-path=input_for_tests/test_input.xlsx"]
        )
    print(result.__dict__)
    assert result.exit_code == 0
    assert "file written to input_for_tests/test_input_20201122010203_n-grams" in str(
        result.stdout_bytes
    )
    os.remove("input_for_tests/test_input_20201122010203_n-grams.csv")
