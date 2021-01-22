from unittest.mock import Mock, patch
import pytest

import excel_ngrams
from excel_ngrams.grammer import FileToList, Grammer

# @pytest.fixture
# def mock_get_terms(mocker):
#     return mocker.patch("excel_ngrams.grammer.Grammer.get_terms")

# @pytest.fixture
# def mock_get_ngrams(mocker):
#     return mocker.patch("excel_ngrams.grammer.Grammer.get_ngrams")

# @pytest.fixture
# def grammer_default(mock_get_terms):
#     mock_get_terms.return_value = [
#         'best thing ever', 
#         "it's the best thing ever",
#         'best day ever',
#         'not the best thing ever'
#         ]
#     grammer_default = Grammer(
#         'no_file.xlsx',
#         'col_name'
#         )
#     return grammer_default

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
        'input/test_search_listings.xlsx',
        'Keyword'
        )
    return grammer_instance


def test_get_terms_from_excel_returns_list(file_to_list):
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


# def test_get_bi_grams_from_file(grammer_from_file, mock_get_terms):
#     result = grammer_from_file.get_ngrams(
#         n=2, top_n=1
#     )
#     assert result == [(('snacks', 'low'), 2)]

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

# def test_ngram_range(grammer_default, mock_get_ngrams):
#     input_list = ['test', 'test two']
#     grammer_from_file.ngram_range(3)
#     assert 2 == mock_get_ngrams.call_count

# def test_ngram_dict_w_n_value_as_key(grammer_default, mock_get_ngrams):
#     input_list = ['test', 'test two']
#     output = grammer_from_file.ngram_range(3)
#     assert 2 in output.keys()
#     assert 3 in output.keys()

# @pytest.mark.e2e
# def test_ngram_range_from_file(grammer_from_file):
#     output = grammer_from_file.ngram_range(3)
#     assert output == []