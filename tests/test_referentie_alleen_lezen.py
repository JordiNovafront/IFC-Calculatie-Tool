"""referentie/ is alleen-lezen: bestanden mogen nooit wijzigen."""
import hashlib
import os

import pytest

# SHA-256 bij aanlevering (26-11-2026). Nieuw referentiebestand? Hier toevoegen.
REFERENTIE_HASHES = {
    "uittrekstaat_template.xlsx": "590e0c43567ac3e65c74742b4a9259c2f12104e5099e2ce9c29ae5146152475f",
    "Stappenplan_IFC-hoeveelhedentool_met_Claude_Code.pdf": "3694846ee89bfc4489e46078cd0504804788630c8cff823a10107bf59cd19fca",
}


@pytest.mark.parametrize("naam,sha", REFERENTIE_HASHES.items())
def test_referentiebestand_ongewijzigd(root, naam, sha):
    pad = root / "referentie" / naam
    assert pad.exists(), f"{naam} ontbreekt in referentie/"
    assert hashlib.sha256(pad.read_bytes()).hexdigest() == sha, f"{naam} is gewijzigd!"


@pytest.mark.parametrize("naam", REFERENTIE_HASHES)
def test_referentiebestand_schrijfbeveiligd(root, naam):
    pad = root / "referentie" / naam
    assert not (os.stat(pad).st_mode & 0o222), f"{naam} is niet schrijfbeveiligd"
