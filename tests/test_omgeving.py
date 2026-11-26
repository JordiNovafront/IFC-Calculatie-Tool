"""Rooktest: de omgeving is zoals afgesproken in CLAUDE.md."""
import sys


def test_python_312():
    assert sys.version_info[:2] == (3, 12)


def test_ifcopenshell_08x():
    import ifcopenshell

    # Updaten naar een nieuwere versie alleen na goedkeuring van Bastiaan.
    assert ifcopenshell.version.startswith("0.8."), ifcopenshell.version


def test_bibliotheken_importeerbaar():
    import fastapi  # noqa: F401
    import openpyxl  # noqa: F401
    import pydantic  # noqa: F401
    import yaml  # noqa: F401
