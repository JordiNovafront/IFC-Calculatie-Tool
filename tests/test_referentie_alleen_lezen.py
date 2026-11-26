"""referentie/ is alleen-lezen: bestanden mogen nooit wijzigen."""
import hashlib

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


# Schrijfbeveiliging (chmod / Windows "Alleen-lezen") wordt niet door git bewaard en is dus geen
# betrouwbare test op een verse clone. De hash-test hierboven is de garantie; daarnaast controleert
# tests/test_excel_config.py::test_template_blijft_onaangeroerd dat de lezer het template niet wijzigt.
