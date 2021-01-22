import pytest

import excel_ngrams
from excel_ngrams.grammer import Grammer

@pytest.fixture
def mock_get_ngrams(mocker):
    return mocker.patch("excel_ngrams.grammer.Grammer.get_ngrams")

@pytest.fixture
def grammer_default():
    grammer_default = Grammer(
        'input/test_search_listings.xlsx',
        'Keyword'
        )
    return grammer_default


def test_gets_list_from_excel(grammer_default):
    result = grammer_default.term_list
    assert type(result) == list

def test_gets_words_list_from_excel(grammer_default):
    result = grammer_default.term_list
    assert result == [
        'diet snacks', 'keto snacks', 
        'low carb snacks', 'low calorie snacks'
        ]

def test_get_bi_grams(grammer_default):
    input_list = [
        'best thing ever', 
        "it's the best thing",
        'best day ever',
        'not the best thing']
    result = grammer_default.get_ngrams(
        n=2, term_list=input_list, top_n=1
    )
    assert result == [(('best', 'thing'), 3)]

def test_get_tri_grams(grammer_default):
    input_list = [
        'best thing ever', 
        "it's the best thing ever",
        'best day ever',
        'not the best thing ever']
    result = grammer_default.get_ngrams(
        n=3, term_list=input_list, top_n=1
    )
    assert result == [(('best', 'thing', 'ever'), 3)]

def test_ngram_range(grammer_default, mock_get_ngrams):
    input_list = ['test', 'test two']
    grammer_default.ngram_range(3)
    assert 2 == mock_get_ngrams.call_count

def test_ngram_dict_w_n_value_as_key(grammer_default, mock_get_ngrams):
    input_list = ['test', 'test two']
    output = grammer_default.ngram_range(3)
    assert 2 in output.keys()
    assert 4 in output.keys()

# @pytest.mark.e2e
# def test_ngram_range_from_file(grammer_default)