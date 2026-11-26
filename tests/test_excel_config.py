"""Fase 0: config/excel_mapping.yaml beschrijft het template en de calculatieregels worden goed uitgelezen.

De opbouw van de Excel staat alleen in de YAML; de inhoud (titels, eenheden) wordt uit de
Excel zelf gelezen. Verandert het template, dan moet de lezer dat merken.
"""
import shutil

import openpyxl
import pytest
import yaml

from backend.app.datamodel import Calculatieregel
from backend.app.excel.calculatieregels import MappingFout, lees_calculatieregels, laad_mapping


@pytest.fixture(scope="module")
def mapping_pad(root):
    return root / "config" / "excel_mapping.yaml"


@pytest.fixture(scope="module")
def template_pad(root, verwacht):
    return root / verwacht["excel"]["template"]


@pytest.fixture(scope="module")
def regels(mapping_pad, template_pad) -> dict[str, Calculatieregel]:
    lijst = lees_calculatieregels(mapping_pad, template_pad)
    return {r.id: r for r in lijst}


def test_mapping_bestaat_en_is_geldige_yaml(mapping_pad):
    data = yaml.safe_load(mapping_pad.read_text(encoding="utf-8"))
    assert data["versie"] == 1
    assert data["calculatieregels"]


def test_mapping_verwijst_naar_bestaande_tabbladen(mapping_pad, template_pad):
    mapping = laad_mapping(mapping_pad)
    wb = openpyxl.load_workbook(template_pad, read_only=True)
    for regel in mapping["calculatieregels"]:
        assert regel["tabblad"] in wb.sheetnames, regel["id"]


def test_aantal_calculatieregels(regels, verwacht):
    assert len(regels) == verwacht["excel"]["aantal_calculatieregels"]


def test_aantal_per_tabblad(regels, verwacht):
    telling: dict[str, int] = {}
    for r in regels.values():
        telling[r.tabblad] = telling.get(r.tabblad, 0) + 1
    assert telling == verwacht["excel"]["per_tabblad"]


def test_tabbladen_zonder_regels_zijn_verantwoord(mapping_pad, verwacht):
    mapping = laad_mapping(mapping_pad)
    overgeslagen = {t["tabblad"] for t in mapping["overgeslagen_tabbladen"]}
    assert overgeslagen == set(verwacht["excel"]["tabbladen_zonder_regels"])
    assert all(t["reden"] for t in mapping["overgeslagen_tabbladen"])


def test_ids_uniek_en_herkenbaar(mapping_pad):
    ids = [r["id"] for r in laad_mapping(mapping_pad)["calculatieregels"]]
    assert len(ids) == len(set(ids))
    assert "21.01" in ids


def test_elke_regel_heeft_titel_en_hoeveelheid(regels):
    for r in regels.values():
        assert r.titel, r.id
        assert r.hoeveelheden, r.id
        assert r.invoerrijen, r.id


def test_steekproef_werkvloer(regels):
    r = regels["21.01"]
    assert r.tabblad == "§21"
    assert r.hoofdstuk == "21"
    assert r.titel == "Werkvloer van beton"
    assert r.omschrijving == "Aanbrengen werkvloer van beton"
    assert r.eenheid == "m2"
    assert r.hoeveelheden[0].kolom == "G"
    assert r.hoeveelheden[0].totaalcel == "G8"
    assert r.invoerrijen == [3, 4, 5, 6]


def test_steekproef_kalkzandsteen_lijmblokken(regels):
    r = regels["22.03"]
    assert r.titel.startswith("Kalkzandsteen lijmblokken")
    assert r.eenheid == "m2"
    assert r.hoeveelheden[0].totaalcel == "G34"


def test_steekproef_ps_fundering_afgeleide_hoeveelheden(regels):
    r = regels["21.04"]
    assert r.titel == "PS-fundering"
    assert [(h.kolom, h.eenheid) for h in r.hoeveelheden] == [("G", "m1"), ("J", "m3"), ("N", "kg")]
    beton, wapening = r.hoeveelheden[1], r.hoeveelheden[2]
    assert (beton.verliescel, beton.verlies_procent) == ("J54", 5)
    assert (wapening.verliescel, wapening.verlies_procent) == ("N54", 10)
    assert r.invoerkolommen["M"] == "Wap."  # kengetal kg/m3


def test_steekproef_kelderwanden(regels):
    r = regels["21.18"]
    assert r.titel == "Kelderwanden van beton"
    assert [(h.kolom, h.eenheid) for h in r.hoeveelheden] == [("G", "m2"), ("J", "m3"), ("N", "kg")]
    # totaalformule G217 telt vanaf rij 203 en noemt m1: moet als waarschuwing gemeld worden
    assert any("G217" in w for w in r.waarschuwingen), r.waarschuwingen


def test_steekproef_staalconstructie(regels):
    r = regels["25.01"]
    assert r.titel == "Staalconstructie"
    assert r.eenheid == "kg"
    assert r.hoeveelheden[0].verlies_procent == 10


def test_steekproef_na_isolatie_zonder_eenheid(regels):
    r = regels["37.01"]
    assert r.eenheid is None
    assert any("eenheid" in w.lower() for w in r.waarschuwingen)


def test_afwijkende_formule_bekisting_gemeld(regels):
    r = regels["21.05"]
    assert r.titel == "Traditionele bekisting"
    assert any("J61" in w for w in r.waarschuwingen), r.waarschuwingen


def test_lezer_merkt_gewijzigd_template(tmp_path, mapping_pad, template_pad):
    kopie = tmp_path / "template_gewijzigd.xlsx"
    shutil.copy(template_pad, kopie)
    kopie.chmod(0o644)
    wb = openpyxl.load_workbook(kopie)
    wb["§21"]["A1"] = "Iets anders"
    wb.save(kopie)
    with pytest.raises(MappingFout, match="21.01"):
        lees_calculatieregels(mapping_pad, kopie)


def test_lezer_volgt_alleen_de_yaml(tmp_path, mapping_pad, template_pad):
    """Geen hardcoded opbouw: een YAML met één regel levert precies één regel op."""
    data = laad_mapping(mapping_pad)
    data["calculatieregels"] = [r for r in data["calculatieregels"] if r["id"] == "22.03"]
    klein = tmp_path / "mapping.yaml"
    klein.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    lijst = lees_calculatieregels(klein, template_pad)
    assert [r.id for r in lijst] == ["22.03"]


def test_template_blijft_onaangeroerd(template_pad, mapping_pad):
    voor = template_pad.read_bytes()
    lees_calculatieregels(mapping_pad, template_pad)
    assert template_pad.read_bytes() == voor


def test_opgetelde_aantallen_zijn_geen_hoofdhoeveelheid(regels):
    """§30 Aluminium kozijnen: de totaalregel telt ook 'aantal' (F18) op; hoofdhoeveelheid blijft 'tot.' m2."""
    r = regels["30.02"]
    assert (r.hoeveelheden[0].kolom, r.eenheid) == ("G", "m2")
    assert [h.kolom for h in r.afgeleide_hoeveelheden] == ["F"]
    assert r.invoerkolommen["F"] == "aantal"
