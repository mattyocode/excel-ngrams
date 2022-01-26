[![Tests](https://github.com/mattyocode/excel-ngrams/workflows/Tests/badge.svg)](https://github.com/mattyocode/excel-ngrams/actions?workflow=Tests)

[![codecov](https://codecov.io/gh/mattyocode/excel-ngrams/branch/main/graph/badge.svg?token=0621CKX30T)](https://codecov.io/gh/mattyocode/excel-ngrams)

[![PyPI](https://img.shields.io/pypi/v/excel-ngrams.svg)](https://pypi.org/project/excel-ngrams/)

# The Excel Ngrams Project

A project to analyse a column of text in an Excel document and
return a CSV file with the most common ngrams from that text. Output file is returned to the same directory as the input file.

You can choose the maximum n-gram length, and maximum number of
results (rows) returned. The app defaults to looking for a column
named 'Keyword' but any column name can be passed in as an argument.

The column of terms to analyse must be the longest (or only) column in the document to prevent the addition of NaN as a placeholder in final cells, which will cause errors.

Words are tokenised with Spacy and ngrams are generated with NLTK.

## Built with

- Python (with static type checking)
- Poetry
- Click
- Pandas
- Spacy
- NLTK
- PyTest
- Flake8
- Sphinx

## Requirements

Requires: Python >=3.7.1, <4.0.0

## Installation

To install the Excel Ngrams Project,
run this command in your terminal:

$ pip install excel-ngrams

![Excel-ngrams-usage](https://media.giphy.com/media/L3QRuhyMhdgUWNtwFp/giphy.gif)

## Documentation

Documentation is available at: https://excel-ngrams.readthedocs.io/en/latest/
