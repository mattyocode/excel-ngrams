import pytest

from excel_ngrams.grammer import Grammer

def test_gets_list_from_excel():
    result = Grammer().word_list_from_excel_doc(
        'input/test_search_listings.xlsx',
        'Keyword'
    )
    assert type(result) == list

def test_gets_words_list_from_excel():
    result = Grammer().word_list_from_excel_doc(
        'input/test_search_listings.xlsx',
        'Keyword'
    )
    assert result == [
        'diet snacks', 'keto snacks', 
        'low carb snacks', 'low calorie snacks'
        ]

def test_get_bi_grams():
    word_list = [
        'best thing ever', 
        "it's the best thing",
        'best day ever',
        'not the best thing']
    result = Grammer().get_n_grams(
        word_list, 2, 1
    )
    assert result == [(('best', 'thing'), 3)]

def test_get_tri_grams():
    word_list = [
        'best thing ever', 
        "it's the best thing ever",
        'best day ever',
        'not the best thing ever']
    result = Grammer().get_n_grams(
        word_list, 3, 1
    )
    assert result == [(('best', 'thing', 'ever'), 3)]