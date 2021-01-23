# from datatest import validate
from unittest.mock import Mock, patch

import pandas as pd
import pytest

import excel_ngrams
from excel_ngrams.grammer import FileToList, Grammer


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
def file_to_list():
    file_to_list = FileToList(
        'input/test_search_listings.xlsx',
        'Keyword'
        )
    return file_to_list

@pytest.fixture
def grammer_instance():
    file_to_list_mock = Mock()
    grammer_instance = Grammer(
        file_to_list_mock,
        )
    return grammer_instance


def test_file_to_list_gets_term_list_attribute(file_to_list):
    result = file_to_list.get_terms()
    assert type(result) == list


def test_gets_words_list_from_excel(file_to_list):
    result = file_to_list.get_terms()
    assert result == [
        'diet snacks', 'keto snacks', 
        'low carb snacks', 'low calorie snacks'
        ]


def test_get_bi_grams_mocked(grammer_instance):
    grammer_instance.term_list = [
        'best thing', 
        "it's the best thing ever",
        'best day ever',
        'not the best thing ever'
        ]
    result = grammer_instance.get_ngrams(
        n=2, top_n=1
    )
    assert result == [(('best', 'thing'), 3)]


def test_get_tri_grams(grammer_instance):
    grammer_instance.term_list = [
        'best thing ever', 
        "it's the best thing ever",
        'best day ever',
        'not the best thing ever'
        ]
    result = grammer_instance.get_ngrams(
        n=3, top_n=1
    )
    assert result == [(('best', 'thing', 'ever'), 3)]


# def test_ngram_range(grammer_instance, mock_get_ngrams):
#     grammer_instance.term_list = ['test', 'test two']
#     grammer_instance.ngram_range(3)
#     assert 2 == mock_get_ngrams.call_count


# def test_ngram_dict_w_n_value_as_key(grammer_instance, mock_get_ngrams):
#     grammer_instance.term_list = ['test', 'test two']
#     output = grammer_instance.ngram_range(3)
#     assert 2 in output.keys()
#     assert 3 in output.keys()


def test_get_bi_grams_from_file():
    """It returns bigram from test file."""
    file_to_list = FileToList(
        'input/test_search_listings.xlsx',
        'Keyword'
        )
    grammer_from_list = Grammer(file_to_list)
    result = grammer_from_list.get_ngrams(
        n=2, top_n=1
    )
    assert result == [(('snacks', 'low'), 2)]


# def test_ngram_range_from_file():
#     file_to_list = FileToList(
#         'input/test_search_listings.xlsx',
#         'Keyword'
#         )
#     grammer_from_list = Grammer(file_to_list)
#     output = grammer_from_list.ngram_range(2)
#     assert ('snacks', 'low') in output[2][0]
#     assert 2 in output.keys()

def test_terms_to_columns(grammer_instance):
    tuple_list = [
        (('snacks', 'low'), 2),
        (('low', 'calorie'), 1)
    ]
    output = grammer_instance.terms_to_columns(tuple_list)
    output_terms, output_values = output
    assert output_terms == ['snacks low', 'low calorie']
    assert output_values == [2, 1]


def test_tuple_list_to_dataframe(grammer_instance, mock_terms_to_cols):
    mock_terms_to_cols.return_value = [
        'snacks low', 'low calorie'], [2, 1]
    test_tuple_list = [(('test', 'thing'), 3)]
    df = grammer_instance.df_from_tuple_list(test_tuple_list)
    assert df.shape == (2, 2)
    assert df["2-gram"][0] == 'snacks low'


def test_adds_to_existing_df(grammer_instance):
    existing_df = pd.DataFrame(
        {
            "2 gram": ["snacks low", "low cal"],
            "2 gram frequency": [2, 1],
        }
    )
    new_df = pd.DataFrame(
        {
            "3 gram": ['snacking more fine', 'no calorie stuff'],
            "3 gram frequency": [5, 3]
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
            "3 gram": ['snacking more fine', 'no calorie stuff', 'extra one added'],
            "3 gram frequency": [5, 3, 2]
        }
    )
    df = grammer_instance.combine_dataframes([existing_df, new_df])
    assert df.shape == (3, 4)


def test_ngram_range_2_gram_only(grammer_instance, mock_get_ngrams, mock_df_from_tuple_list):
    mock_df_from_tuple_list.return_value = pd.DataFrame(
        {
            "2 gram": ["snacks low", "low cal"],
            "2 gram frequency": [2, 1],
        }
    )
    output_df = grammer_instance.ngram_range(2)
    assert len(output_df.columns) == 2
    assert mock_get_ngrams.call_count == 1



# @pytest.mark.parametrize(
#     "test_input,expected",
#     [
#         ({2: [(('snacks', 'low'), 2), (('other', 'stuff'), 1)]}, (2, 1)),
#         ({2: [(('snacks', 'low'), 2), (('other', 'stuff'), 1)],
#             3: [(('three', 'snacks', 'low'), 2), (('other', 'some', 'stuff'), 1)]}, (2, 2)),
#         ({2: [(('snacks', 'low'), 2), (('other', 'stuff'), 1), (('one', 'more'), 1)],
#             3: [(('three', 'snacks', 'low'), 2), (('other', 'some', 'stuff'), 1)]}, (3, 2)),
#     ]
# )
# def test_ngrams_dict_to_dataframe(grammer_instance, test_input, expected):
#     df = grammer_instance.df_from_dict(test_input)
#     assert df.shape == expected