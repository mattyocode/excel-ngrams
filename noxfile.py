import re
import tempfile

import nox


nox.options.sessions = "lint", "safety", "tests"
locations = "src", "tests", "noxfile.py"
package = "excel_ngrams"


def install_with_constraints(session, *args, **kwargs):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )

        with open(f"{requirements.name}", "r") as full_file:
            lines = full_file.readlines()
        with open(f"{requirements.name}", "w") as new_file:
            for line in lines:
                if "en-core-web" in line.strip("\n"):
                    spacy_model = line.strip()
                else:
                    new_file.write(line)

        spacy_model_url = re.findall("(https.*)", spacy_model)[0]

        session.install(f"--constraint={requirements.name}", *args, **kwargs)
        session.install(f"{spacy_model_url}")


@nox.session(python=["3.9", "3.8", "3.7"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", "--no-dev", external=True)
    install_with_constraints(
        session, "coverage[toml]", "pytest", "pytest-cov", "pytest-mock"
    )
    session.run("pytest", *args)


@nox.session(python=["3.9", "3.8", "3.7"])
def black(session):
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python=["3.9", "3.8", "3.7"])
def lint(session):
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-bandit",
        "flake8-black",
        "flake8-bugbear",
        "flake8-import-order",
    )
    session.run("flake8", *args)


@nox.session(python=["3.9", "3.8", "3.7"])
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
