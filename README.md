[![Tests](https://github.com/mattyocode/excel-ngrams/workflows/Tests/badge.svg)](https://github.com/mattyocode/excel-ngrams/actions?workflow=Tests)

[![codecov](https://codecov.io/gh/mattyocode/excel-ngrams/branch/main/graph/badge.svg?token=0621CKX30T)](https://codecov.io/gh/mattyocode/excel-ngrams)

# The Excel Ngrams Project

A project to analyse a column of text in an Excel document and
return a CSV file with the most common ngrams from that text. Output
file is returned to the same directory as the input file. You can
choose the maximum n-gram length, and maximum number of results (rows)
returned.


Words are tokenised with Spacy and ngrams are generated with NLTK.


## Installation

To install the Excel Ngrams Project,
run this command in your terminal:


$ pip install excel-ngrams

$ python3 excel-ngrams [OPTIONS]
