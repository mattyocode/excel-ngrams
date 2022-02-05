"""Tests cases for the grammer module."""
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from pytest_mock import MockFixture

from excel_ngrams.grammer import Grammer

TEST_DATA = [
    "diet snacks",
    "keto snacks",
    "low carb snacks",
    "low calorie snacks",
]


# ------- Instance fixture -------


@pytest.fixture
def grammer_instance() -> Grammer:
    """Fixture returns Grammer instance."""
    terms_list = ["test"]
    grammer_instance = Grammer(terms_list)
    return grammer_instance


# ------- Mock fixtures -------


@pytest.fixture
def mock_get_ngrams(mocker: MockFixture) -> Mock:
    """Fixture to patch Grammer.get_ngrams."""
    return mocker.patch("excel_ngrams.grammer.Grammer.get_ngrams")


@pytest.fixture
def mock_terms_to_cols(mocker: MockFixture) -> Mock:
    """Fixture to patch Grammer.terms_to_columns."""
    return mocker.patch("excel_ngrams.grammer.Grammer.terms_to_columns")


@pytest.fixture
def mock_df_from_terms(mocker: MockFixture) -> Mock:
    """Fixture to patch Grammer.df_from_terms."""
    return mocker.patch("excel_ngrams.grammer.Grammer.df_from_terms")


@pytest.fixture
def mock_file_handler(mocker: MockFixture) -> Mock:
    """Fixture to patch FileHandler passed to Grammer constructor."""
    return mocker.patch("excel_ngrams.grammer.FileHandler")


@pytest.fixture
def mock_spacy_load(mocker: MockFixture) -> Mock:
    """Fixture to patch Spacy.load."""
    return mocker.patch("spacy.load", side_effect=OSError)


@pytest.fixture
def mock_spacy_download(mocker: MockFixture) -> Mock:
    """Fixture to patch Spacy.download."""
    return mocker.patch("spacy.cli.download")


@pytest.fixture
def mock_nltk_download(mocker: MockFixture) -> Mock:
    """Fixture to patch nltk.download."""
    return mocker.patch("nltk.download")


@pytest.fixture
def mock_nltk_stopwords(mocker: MockFixture) -> Mock:
    """Fixture to patch nltk.stopwords.words."""
    return mocker.patch("nltk.corpus.stopwords.words")


# ------- Grammer tests -------


def test_loads_spacy_model_if_present(
    mock_spacy_load: Mock, mock_spacy_download: Mock
) -> None:
    """It calls spacy.load without calling download."""
    with patch("excel_ngrams.grammer.Grammer._nlp", new=None):
        mock_spacy_load.side_effect = Mock()
        grammer = Grammer(mock_file_handler)
        mock_spacy_load.assert_called_once_with("en")
        mock_spacy_download.assert_not_called
        assert grammer._nlp is not None


def test_downloads_spacy_model_if_not_present(
    mock_spacy_load: Mock, mock_spacy_download: Mock
) -> None:
    """It calls spacy.download with correct command."""
    with patch("excel_ngrams.grammer.Grammer._nlp", new=None):
        mock_spacy_load.side_effect = [OSError, Mock()]
        grammer = Grammer(TEST_DATA)
        mock_spacy_download.assert_called_with("en")
        assert grammer._nlp is not None


def test_downloads_nltk_stopwords_if_not_present(
    mock_nltk_download: Mock, mock_nltk_stopwords: Mock
) -> None:
    """It calls os.system with correct command."""
    with patch("excel_ngrams.grammer.Grammer._stopwords", new=None):
        mock_nltk_stopwords.return_value = "fake_stopwords"
        grammer = Grammer(TEST_DATA)
        mock_nltk_stopwords.assert_called_with("english")
        assert grammer._stopwords is not None


def test_displays_exception_if_nltk_stopwords_fails(
    capsys: MockFixture,
    mock_nltk_download: Mock,
) -> None:
    """It raises exception with message if nltk download fails."""
    with patch("excel_ngrams.grammer.Grammer._stopwords", new=None):
        mock_nltk_download.side_effect = Exception
        grammer = Grammer(TEST_DATA)
        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert grammer._stopwords is None


@pytest.mark.parametrize(
    "test_word,expected",
    [("to", True), ("of", True), ("by", True), ("unicorn", False), (",", False)],
)
def test_if_in_nltk_stopwords(
    test_word: str, expected: bool, grammer_instance: Grammer
) -> None:
    """It returns bool according to presence in NLTK stopwords."""
    actual = grammer_instance.in_stop_words(test_word)
    assert actual == expected


def test_get_single_word_frequency(grammer_instance: Grammer) -> None:
    """It returns most frequent term with value."""
    grammer_instance.term_list = [
        "the best the thing",
        "it's the best thing ever",
        "the best day ever",
        "not the best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=1, top_n_results=1)
    assert result == [(("best",), 4)]


def test_get_single_word_frequency_stopwords_false(grammer_instance: Grammer) -> None:
    """It returns most frequent term with value including stopwords."""
    grammer_instance.term_list = [
        "the best the thing",
        "it's the best thing ever",
        "the best day ever",
        "not the best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=1, top_n_results=1, stopwords=False)
    assert result == [(("the",), 5)]


def test_get_ngrams_excludes_puncuation(grammer_instance: Grammer) -> None:
    """It returns most frequent term with value."""
    grammer_instance.term_list = [
        "best, thing",
        "it's 'the' best, thing, ever",
        "best ! day ! ever!",
        "not, the? best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=1, top_n_results=100)
    punctuation = [",", "'", "!", "?"]
    unpacked_tuple_results = [k[0] for k, v in result]
    assert [i for i in punctuation if i in unpacked_tuple_results] == []


def test_remove_escaped_chars(grammer_instance: Grammer) -> None:
    """It returns text list with newline chars removed."""
    input_list = [
        "String with \n newline chars \n",
        "\n",
        "string with \t tab \t chars",
        "\t",
        "without any",
    ]
    output = grammer_instance.remove_escaped_chars(input_list)
    assert output == [
        "String with  newline chars",
        "string with  tab  chars",
        "without any",
    ]


def test_top_results_exceeds_results_available(grammer_instance: Grammer) -> None:
    """It returns all results when top_n_results exceeds results available."""
    grammer_instance.term_list = [
        "best thing",
        "it's the best thing ever",
        "best day ever",
        "not the best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=1, top_n_results=100)
    assert len(result) == 5


def test_get_bi_grams_mocked(grammer_instance: Grammer) -> None:
    """It returns most frequent bigram with value."""
    grammer_instance.term_list = [
        "best thing",
        "it's the best thing ever",
        "best day ever",
        "not the best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=2, top_n_results=1)
    assert result == [(("best", "thing"), 3)]


def test_get_tri_grams(grammer_instance: Grammer) -> None:
    """It returns most frequent trigram with value."""
    grammer_instance.term_list = [
        "best thing ever",
        "it's the best thing ever",
        "best day ever",
        "not the best thing ever",
    ]
    result = grammer_instance.get_ngrams(n=3, top_n_results=1)
    assert result == [(("best", "thing", "ever"), 3)]


@pytest.mark.e2e
def test_get_bi_grams_from_file() -> None:
    """It returns most frequent bigram and value from test file in directory."""
    test_terms = [
        "diet snacks",
        "keto snacks",
        "low carb snacks",
        "low calorie snacks",
    ]
    grammer = Grammer(test_terms)
    result = grammer.get_ngrams(n=2, top_n_results=1)
    assert result == [(("snacks", "low"), 2)]


def test_terms_to_columns(grammer_instance: Grammer) -> None:
    """It outputs a list of concatinated terms and a list of values."""
    tuple_list = [(("snacks", "low"), 2), (("low", "calorie"), 1)]
    output = grammer_instance.terms_to_columns(tuple_list)
    output_terms, output_values = output
    assert output_terms == ["snacks low", "low calorie"]
    assert output_values == [2, 1]


def test_tuple_list_to_dataframe(
    grammer_instance: Grammer, mock_terms_to_cols: Mock
) -> None:
    """It returns Pandas dataframe from tuple list."""
    mock_terms_to_cols.return_value = ["snacks low", "low calorie"], [2, 1]
    test_tuple_list = [(("test", "thing"), 3)]
    df = grammer_instance.df_from_terms(test_tuple_list)
    assert df.shape == (2, 2)
    assert df["2-gram"][0] == "snacks low"


def test_adds_to_existing_df(grammer_instance: Grammer) -> None:
    """It combines two dataframes into one."""
    existing_df = pd.DataFrame(
        {"2 gram": ["snacks low", "low cal"], "2 gram frequency": [2, 1]}
    )
    new_df = pd.DataFrame(
        {
            "3 gram": ["snacking more fine", "no calorie stuff"],
            "3 gram frequency": [5, 3],
        }
    )
    df = grammer_instance.combine_dataframes([existing_df, new_df])
    assert df.shape == (2, 4)


def test_adds_to_existing_df_with_unbalanced_dfs(grammer_instance: Grammer) -> None:
    """It combines two dataframes, adding NaN when later dataframe has more rows."""
    existing_df = pd.DataFrame(
        {"2 gram": ["snacks low", "low cal"], "2 gram frequency": [2, 1]}
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
    grammer_instance: Grammer, mock_get_ngrams: Mock, mock_df_from_terms: Mock
) -> None:
    """It returns dataframe of single word ngrams with values."""
    mock_df_from_terms.return_value = pd.DataFrame(
        {"2 gram": ["snacks low", "low cal"], "2 gram frequency": [2, 1]}
    )
    output_df = grammer_instance.ngram_range(1)
    assert len(output_df.columns) == 2
    assert mock_get_ngrams.call_count == 1


def test_ngram_range_2_gram(
    grammer_instance: Grammer, mock_get_ngrams: Mock, mock_df_from_terms: Mock
) -> None:
    """It returns dataframe of single word ngrams and bigrams with values."""
    mock_df_from_terms.return_value = pd.DataFrame(
        {"2 gram": ["snacks low", "low cal"], "2 gram frequency": [2, 1]}
    )
    output_df = grammer_instance.ngram_range(2)
    assert len(output_df.columns) == 4
    assert mock_get_ngrams.call_count == 2


def test_ngram_range_3_gram(
    grammer_instance: Grammer, mock_get_ngrams: Mock, mock_df_from_terms: Mock
) -> None:
    """It returns dataframe with 1-3grams and their values."""
    dataframe_return_values = [
        pd.DataFrame({"1 gram": ["low", "snacks"], "1 gram frequency": [2, 1]}),
        pd.DataFrame({"2 gram": ["snacks low", "low cal"], "2 gram frequency": [2, 1]}),
        pd.DataFrame(
            {"3 gram": ["big snacks low", "low cal time"], "3 gram frequency": [7, 3]}
        ),
    ]
    mock_df_from_terms.side_effect = dataframe_return_values
    output_df = grammer_instance.ngram_range(3)
    assert len(output_df.columns) == 6
    assert mock_get_ngrams.call_count == 3
