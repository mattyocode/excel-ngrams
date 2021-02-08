The Excel Ngrams Project
========================

.. toctree::
   :hidden:
   :maxdepth: 1

   license
   reference


A project to analyse a column of text in an Excel document and
return a CSV file with the most common ngrams from that text. Output
file is returned to the same directory as the input file. You can
choose the maximum n-gram length, and maximum number of results (rows)
returned.


Words are tokenised with Spacy and ngrams are generated with NLTK.


Installation
------------

To install the Excel Ngrams Project,
run this command in your terminal:

.. code-block:: console

    $ pip install excel-ngrams


Usage
-----

Excel Ngram's usage looks like:

.. code-block:: console

    $ excel-ngrams [OPTIONS]

.. option:: -f <file-path>, --file-path <file-path>

    The path to the input Excel file to be parsed for
    words to generate ngrams.

.. option:: -s <sheet-name>, --sheet-name <sheet-name>

    The name of the Excel sheet that contains the column
    of text to be analysed. By default, this is the first
    sheet in a document where none of the sheets have names.
    If any sheets are named, you must specify the one that
    contains the column to be analysed.

.. option:: -c <column-name>, --column-name <column-name>

    The name of the column containing the text to be analysed
    for ngrams. By default, this is set to 'Keyword'
    (case sensitive).

.. option:: -m <maximum-ngram-length>, --max-n <maximum-ngram-length>

    The maximum length of ngram phrase required. Each length of
    phrase below this number will also be returned in increments
    of one. For example, selecting 3 will return single word frequencies,
    bigrams, and trigrams. By default, this is set to 5.

.. option:: -t <number-of-results>, --top-results <number-of-results>

    The number of rows of results to return. By default, this is 250
    or all of the results if there are fewer than 250.

.. option:: -w <boolean>, --stopwords <boolean>

    Remove stopwords from ngram analysis - true of false. By default,
    this is set to true.

.. option:: --version

    Display the version and exit.

.. option:: --help

    Display a short message and exit.
