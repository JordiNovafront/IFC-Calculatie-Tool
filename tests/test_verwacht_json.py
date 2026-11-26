"""verwacht.json is volledig en rekenkundig consistent (de handberekening klopt met zichzelf)."""
import pytest

ELEMENTEN = ["betonwand", "betonvloer", "betonkolom", "kalkzandsteenwand"]


def test_alle_elementen_aanwezig(verwacht):
    assert set(verwacht["testmodel"]["elementen"]) == set(ELEMENTEN)
    assert verwacht["testmodel"]["aantal_bouwelementen"] == len(ELEMENTEN)
    assert verwacht["testmodel"]["aantal_sparingen"] == len(verwacht["testmodel"]["sparingen"])


@pytest.mark.parametrize("sleutel", ELEMENTEN)
def test_elk_element_heeft_materiaal_en_verdieping(verwacht, sleutel):
    e = verwacht["testmodel"]["elementen"][sleutel]
    for veld in ("global_id", "ifc_klasse", "naam", "type_naam", "materiaal", "verdieping"):
        assert e.get(veld), f"{sleutel}.{veld} ontbreekt"


def test_bruto_volumes_uit_maten(verwacht):
    el = verwacht["testmodel"]["elementen"]
    for s in ("betonwand", "kalkzandsteenwand"):
        e = el[s]
        assert e["lengte"] * e["hoogte"] * e["dikte"] == pytest.approx(e["volume_bruto"])
        assert e["lengte"] * e["hoogte"] == pytest.approx(e["zijvlak_bruto_per_zijde"])
    v = el["betonvloer"]
    assert v["lengte"] * v["breedte"] * v["dikte"] == pytest.approx(v["volume_bruto"])
    assert v["lengte"] * v["breedte"] == pytest.approx(v["bovenvlak"])
    k = el["betonkolom"]
    assert k["lengte"] * k["breedte"] * k["hoogte"] == pytest.approx(k["volume_bruto"])


def test_netto_is_bruto_min_sparing(verwacht):
    tm = verwacht["testmodel"]
    sp = tm["sparingen"]["raamsparing"]
    wand = tm["elementen"][sp["in_element"]]
    assert sp["breedte"] * sp["hoogte"] == pytest.approx(sp["oppervlak"])
    assert sp["oppervlak"] * wand["dikte"] == pytest.approx(sp["volume_in_wand"])
    assert wand["volume_bruto"] - sp["volume_in_wand"] == pytest.approx(wand["volume_netto"])
    assert wand["zijvlak_bruto_per_zijde"] - sp["oppervlak"] == pytest.approx(wand["zijvlak_netto_per_zijde"])
    # sparing past in de wand
    assert sp["borstwering"] + sp["hoogte"] <= wand["hoogte"]


def test_totalen_latere_fases(verwacht):
    el = verwacht["testmodel"]["elementen"]
    f3, f4 = verwacht["testmodel"]["fase_3"], verwacht["testmodel"]["fase_4"]
    beton = el["betonwand"]["volume_netto"] + el["betonvloer"]["volume_netto"] + el["betonkolom"]["volume_netto"]
    assert beton == pytest.approx(f3["betonmortel_netto_m3"])
    assert 2 * el["betonwand"]["zijvlak_netto_per_zijde"] == pytest.approx(f3["bekisting_betonwand_2_zijden_netto_m2"])
    assert el["kalkzandsteenwand"]["zijvlak_netto_per_zijde"] == pytest.approx(f3["lijmwerk_kalkzandsteen_m2"])
    assert f3["betonmortel_netto_m3"] - el["betonwand"]["volume_netto"] == pytest.approx(f4["betonwand_uitgevinkt_betonmortel_m3"])
    assert f4["sparingsdrempel_2m2_betonwand_volume_m3"] == pytest.approx(el["betonwand"]["volume_bruto"])
    assert f4["bekisting_1_zijde_m2"] == pytest.approx(el["betonwand"]["zijvlak_netto_per_zijde"])


def test_excel_aantallen_consistent(verwacht):
    x = verwacht["excel"]
    assert sum(x["per_tabblad"].values()) == x["aantal_calculatieregels"]
    assert len(x["per_tabblad"]) + len(x["tabbladen_zonder_regels"]) == x["aantal_tabbladen"]
