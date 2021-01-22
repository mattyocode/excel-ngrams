import click

from . import __version__, grammer

@click.command()
@click.version_option(version=__version__)
def main():
    """Excel n-grams project."""
    click.echo("Excel n-grams.")