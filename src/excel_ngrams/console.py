"""Command-line interface."""
import click

from . import __version__
from .grammer import FileHandler, Grammer


@click.command()
@click.option("--file-path", "-f", type=click.Path(exists=True), required=True)
@click.option("--sheet-name", "-s", default=0, type=str, show_default=True)
@click.option("--column-name", "-c", default="Keyword", type=str, show_default=True)
@click.option("--max-n", "-m", default=5, show_default=True)
@click.option("--top-results", "-t", default=250, show_default=True)
@click.option("--stopwords", "-w", default=True, show_default=True)
@click.version_option(version=__version__)
def main(
    file_path: str,
    sheet_name: str,
    column_name: str,
    max_n: int,
    top_results: int,
    stopwords: bool,
) -> None:
    """Excel n-grams project CLI interface."""
    file_handler = FileHandler(
        file_path=file_path, sheet_name=sheet_name, column_name=column_name
    )
    text_to_anlayse = file_handler.get_terms()

    click.echo("Reading file...")

    grammer = Grammer(text_to_anlayse)

    click.echo("Performing n-gram analysis...")

    results_dataframe = grammer.ngram_range(
        max_n, top_n_results=top_results, stopwords=stopwords
    )
    output_file_path = file_handler.write(results_dataframe)

    click.secho(f"CSV file written to {output_file_path}.", fg="green")
