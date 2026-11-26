"""Overzichtspagina fase 0 (docs/fase0_overzicht.html) voor het controlemoment van Bastiaan."""
import re

import pytest

from tools.maak_overzicht import maak_overzicht


@pytest.fixture(scope="module")
def html(tmp_path_factory):
    pad = tmp_path_factory.mktemp("overzicht") / "fase0_overzicht.html"
    maak_overzicht(pad, testresultaat="80 passed in 3.00s")
    return pad.read_text(encoding="utf-8")


def test_handberekening_staat_erin(html):
    for waarde in ("9,00", "8,55", "28,50", "20,00", "80,00", "0,48", "1,35", "13,50", "29,03", "57,00", "20,48"):
        assert waarde in html, waarde


def test_tekening_toont_alle_elementen_uit_het_ifc(html, verwacht):
    tm = verwacht["testmodel"]
    for e in list(tm["elementen"].values()) + list(tm["sparingen"].values()):
        assert f'data-guid="{e["global_id"]}"' in html, e["naam"]


def test_alle_calculatieregels_in_de_tabel(html, verwacht):
    ids = re.findall(r'<tr data-id="([0-9.]+)"', html)
    assert len(ids) == verwacht["excel"]["aantal_calculatieregels"]
    assert "21.05" in ids and "37.01" in ids


def test_waarschuwingen_en_open_vragen(html):
    assert "J61:J74" in html  # afwijkende formule bekisting
    assert "Open vragen voor Bastiaan" in html
    assert "betonmortel" in html


def test_testresultaat_vermeld(html):
    assert "80 passed" in html


def test_volledig_lokaal_geen_externe_bronnen(html):
    """Alles lokaal: geen scripts, stijlen, lettertypes of afbeeldingen van internet."""
    assert not re.search(r'(src|href)\s*=\s*["\']?\s*(https?:)?//', html)
    assert "@import" not in html


def test_tekening_heeft_juiste_maten():
    """Regressie: kaders uit de geometrie zijn de echte maten (geen geheugenrommel)."""
    from pathlib import Path

    from tools.maak_overzicht import ROOT, kaders

    k = {v["naam"]: v for v in kaders(ROOT / "tests" / "testmodel" / "testmodel_ifc4.ifc").values()}
    assert list(k["Betonwand"]["min"].round(3)) == [0.0, 0.0, 0.0]
    assert list(k["Betonwand"]["max"].round(3)) == [10.0, 0.3, 3.0]
    assert list(k["Betonkolom"]["min"].round(3)) == [4.8, 3.8, 0.0]
    assert list(k["Kalkzandsteenwand"]["max"].round(3)) == [7.0, 6.1, 2.7]
