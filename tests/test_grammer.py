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