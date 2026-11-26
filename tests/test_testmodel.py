"""Fase 0: het gegenereerde testmodel (IFC4 en IFC2x3) is compleet en klopt met verwacht.json.

Let op: de echte hoeveelheidsberekening is fase 1. Hier controleren we alleen dat het
testmodel zelf goed in elkaar zit, zodat latere fases er blind op kunnen vertrouwen.
"""
import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.element as ue
import ifcopenshell.util.shape as us
import ifcopenshell.util.unit as uu
import ifcopenshell.validate

SCHEMAS = ["IFC4", "IFC2X3"]


@pytest.fixture(scope="module", params=SCHEMAS)
def model(request, root, verwacht):
    pad = root / verwacht["testmodel"]["bestanden"][request.param]
    assert pad.exists(), f"Testmodel ontbreekt: {pad} – draai tools/maak_testmodel.py"
    return request.param, ifcopenshell.open(str(pad))


def _bouwelementen(f):
    return [e for e in f.by_type("IfcBuildingElement") if not e.is_a("IfcOpeningElement")]


def test_schema(model):
    schema, f = model
    assert f.schema == schema


def test_schemavalidatie_zonder_fouten(model):
    _, f = model
    logger = ifcopenshell.validate.json_logger()
    ifcopenshell.validate.validate(f, logger)
    fouten = [s for s in logger.statements if s.get("level", "").lower() == "error"]
    assert not fouten, fouten


def test_lengte_eenheid_mm(model, verwacht):
    _, f = model
    lengte = uu.get_project_unit(f, "LENGTHUNIT")
    assert (lengte.Prefix, lengte.Name) == ("MILLI", "METRE")


def test_vier_bouwelementen_en_een_sparing(model, verwacht):
    _, f = model
    tm = verwacht["testmodel"]
    assert len(_bouwelementen(f)) == tm["aantal_bouwelementen"]
    assert len(f.by_type("IfcOpeningElement")) == tm["aantal_sparingen"]


def test_een_verdieping(model, verwacht):
    _, f = model
    verdiepingen = f.by_type("IfcBuildingStorey")
    assert [v.Name for v in verdiepingen] == [verwacht["testmodel"]["verdieping"]["naam"]]
    assert verdiepingen[0].GlobalId == verwacht["testmodel"]["verdieping"]["global_id"]


@pytest.mark.parametrize("sleutel", ["betonwand", "betonvloer", "betonkolom", "kalkzandsteenwand"])
def test_element_eigenschappen(model, verwacht, sleutel):
    _, f = model
    v = verwacht["testmodel"]["elementen"][sleutel]
    el = f.by_guid(v["global_id"])
    assert el.is_a(v["ifc_klasse"])
    assert el.Name == v["naam"]
    # materiaal
    mat = ue.get_material(el)
    assert mat is not None, f"{sleutel} heeft geen materiaal"
    assert mat.Name == v["materiaal"]
    # verdieping
    container = ue.get_container(el)
    assert container is not None and container.is_a("IfcBuildingStorey")
    assert container.Name == v["verdieping"]
    # type
    typ = ue.get_type(el)
    assert typ is not None and typ.Name == v["type_naam"]
    # geometrie
    assert el.Representation is not None


def test_globalids_uniek(model):
    _, f = model
    ids = [e.GlobalId for e in f.by_type("IfcRoot")]
    assert len(ids) == len(set(ids))


def test_sparing_in_betonwand(model, verwacht):
    _, f = model
    sp = verwacht["testmodel"]["sparingen"]["raamsparing"]
    opening = f.by_guid(sp["global_id"])
    assert opening.is_a("IfcOpeningElement")
    wand = ue.get_voided_element(opening)
    assert wand.GlobalId == verwacht["testmodel"]["elementen"][sp["in_element"]]["global_id"]


# Base quantities (fase 1 vergelijkt de eigen berekening hiermee).
BASE_QUANTITIES = {
    "betonwand": {"Length": "lengte", "Height": "hoogte", "Width": "dikte",
                  "GrossVolume": "volume_bruto", "NetVolume": "volume_netto",
                  "GrossSideArea": "zijvlak_bruto_per_zijde", "NetSideArea": "zijvlak_netto_per_zijde"},
    "kalkzandsteenwand": {"Length": "lengte", "Height": "hoogte", "Width": "dikte",
                          "GrossVolume": "volume_bruto", "NetVolume": "volume_netto",
                          "GrossSideArea": "zijvlak_bruto_per_zijde", "NetSideArea": "zijvlak_netto_per_zijde"},
    "betonvloer": {"Length": "lengte", "Width": "breedte", "Depth": "dikte",
                   "GrossArea": "bovenvlak", "NetArea": "bovenvlak",
                   "GrossVolume": "volume_bruto", "NetVolume": "volume_netto"},
    "betonkolom": {"Length": "hoogte", "GrossVolume": "volume_bruto", "NetVolume": "volume_netto"},
}


@pytest.mark.parametrize("sleutel", list(BASE_QUANTITIES))
def test_base_quantities(model, verwacht, sleutel):
    _, f = model
    v = verwacht["testmodel"]["elementen"][sleutel]
    el = f.by_guid(v["global_id"])
    lengte_factor = uu.calculate_unit_scale(f)  # projecteenheid -> meter
    gevonden = {}
    for qto in ue.get_psets(el, qtos_only=True).values():
        gevonden.update(qto)
    for ifc_naam, verwacht_veld in BASE_QUANTITIES[sleutel].items():
        assert ifc_naam in gevonden, f"{sleutel}: base quantity {ifc_naam} ontbreekt"
        waarde = gevonden[ifc_naam]
        if ifc_naam in ("Length", "Height", "Width", "Depth"):
            waarde *= lengte_factor
        assert waarde == pytest.approx(v[verwacht_veld], rel=1e-6), ifc_naam


@pytest.mark.parametrize("sleutel", ["betonwand", "betonvloer", "betonkolom", "kalkzandsteenwand"])
def test_zelfcontrole_geometrie_netto_volume(model, verwacht, sleutel):
    """De geometrie in het testmodel geeft het verwachte netto volume (sparing afgetrokken)."""
    _, f = model
    v = verwacht["testmodel"]["elementen"][sleutel]
    settings = ifcopenshell.geom.settings()
    shape = ifcopenshell.geom.create_shape(settings, f.by_guid(v["global_id"]))
    volume = us.get_volume(shape.geometry)  # geom levert meters
    tol = verwacht["tolerantie_procent"] / 100
    assert volume == pytest.approx(v["volume_netto"], rel=tol)
