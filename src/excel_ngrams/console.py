import click

from . import __version__
from .grammer import FileHandler, Grammer

@click.command()
@click.option(
    "--file-path",
    "-f",
    required=True)
@click.option(
    '--sheet-name',
    '-s',
    default=0,
    type=str,
    show_default=True)
@click.option(
    '--column-name',
    '-c',
    default="Keyword",
    type=str,
    show_default=True)
@click.option(
    '--max-n',
    '-m',
    default=5, 
    show_default=True)
@click.version_option(version=__version__)
def main(file_path, sheet_name, column_name, max_n):
    """Excel n-grams project."""
    read_file = FileHandler(
        file_path=file_path,
        sheet_name=sheet_name,
        column_name=column_name)
    grammer = Grammer(read_file)
    n_gram_dataframe = grammer.ngram_range(max_n)
    grammer.output_csv_file(n_gram_dataframe)

    click.echo("CSV file written to same directory as input Excel.")


