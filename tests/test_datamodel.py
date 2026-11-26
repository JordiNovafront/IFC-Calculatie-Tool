"""Fase 0: datamodel – Element, Calculatieregel, Koppeling (veel-op-veel), Meetinstellingen."""
import pytest
from pydantic import ValidationError

from backend.app.datamodel import (
    Calculatieregel,
    Element,
    Hoeveelheidskolom,
    Koppelbron,
    Koppeling,
    Meetinstellingen,
    Project,
)


def _regel(id_, titel, *hoeveelheden):
    return Calculatieregel(
        id=id_, hoofdstuk=id_.split(".")[0], tabblad="§" + id_.split(".")[0], titel=titel,
        hoeveelheden=[Hoeveelheidskolom(naam=n, kolom=k, eenheid=e) for n, k, e in hoeveelheden],
        invoerrijen=[3, 4],
    )


@pytest.fixture
def project():
    p = Project(naam="test")
    p.elementen = [
        Element(global_id="WAND", ifc_klasse="IfcWall", naam="Betonwand", type_naam="Betonwand 300",
                materiaal="Beton C30/37", verdieping="00 Begane grond"),
        Element(global_id="VLOER", ifc_klasse="IfcSlab", naam="Betonvloer", materiaal="Beton C30/37",
                verdieping="00 Begane grond"),
        Element(global_id="ZONDER", ifc_klasse="IfcWall", naam="Wand zonder materiaal"),
    ]
    p.calculatieregels = [
        _regel("21.18", "Kelderwanden van beton", ("tot.", "G", "m2"), ("beton", "J", "m3"), ("tot. Wap.", "N", "kg")),
        _regel("21.05", "Traditionele bekisting", ("tot. M1", "G", "m1"), ("tot. M2", "J", "m2")),
        _regel("46.08", "Sauswerk wanden", ("tot.", "G", "m2")),
    ]
    return p


def test_element_zonder_materiaal_mag(project):
    e = project.element("ZONDER")
    assert e.materiaal is None and e.verdieping is None


def test_calculatieregel_eenheid_is_hoofdhoeveelheid(project):
    r = project.regel("21.18")
    assert r.eenheid == "m2"
    assert [h.eenheid for h in r.afgeleide_hoeveelheden] == ["m3", "kg"]


def test_ongeldige_eenheid_geweigerd():
    with pytest.raises(ValidationError):
        Hoeveelheidskolom(naam="x", kolom="G", eenheid="liter")


def test_veel_op_veel(project):
    # Eén betonwand -> betonmortel (m3), bekisting (m2), wapening (kg), sauswerk (m2)
    project.voeg_koppeling_toe(Koppeling(global_id="WAND", calculatieregel_id="21.18", hoeveelheidskolom="J",
                                         meetwijze="volume_netto"))
    project.voeg_koppeling_toe(Koppeling(global_id="WAND", calculatieregel_id="21.18", hoeveelheidskolom="N",
                                         meetwijze="wapening_via_kengetal"))
    project.voeg_koppeling_toe(Koppeling(global_id="WAND", calculatieregel_id="21.05", hoeveelheidskolom="J",
                                         meetwijze="zijvlak_netto_2_zijden"))
    project.voeg_koppeling_toe(Koppeling(global_id="WAND", calculatieregel_id="46.08",
                                         meetwijze="zijvlak_netto_2_zijden"))
    # En dezelfde regel aan een tweede element
    project.voeg_koppeling_toe(Koppeling(global_id="VLOER", calculatieregel_id="21.18", hoeveelheidskolom="J",
                                         meetwijze="volume_netto"))

    assert len(project.koppelingen_van_element("WAND")) == 4
    assert {e.global_id for e in project.elementen_van_regel("21.18")} == {"WAND", "VLOER"}
    assert project.koppelingen_van_element("ZONDER") == []


def test_dubbele_koppeling_geweigerd(project):
    k = Koppeling(global_id="WAND", calculatieregel_id="21.18", hoeveelheidskolom="J", meetwijze="volume_netto")
    project.voeg_koppeling_toe(k)
    with pytest.raises(ValueError, match="bestaat al"):
        project.voeg_koppeling_toe(k.model_copy())


def test_koppeling_naar_onbekend_element_of_regel_geweigerd(project):
    with pytest.raises(ValueError, match="element"):
        project.voeg_koppeling_toe(Koppeling(global_id="BESTAATNIET", calculatieregel_id="21.18", meetwijze="x"))
    with pytest.raises(ValueError, match="calculatieregel"):
        project.voeg_koppeling_toe(Koppeling(global_id="WAND", calculatieregel_id="99.99", meetwijze="x"))
    with pytest.raises(ValueError, match="hoeveelheidskolom"):
        project.voeg_koppeling_toe(Koppeling(global_id="WAND", calculatieregel_id="21.18", hoeveelheidskolom="Z",
                                             meetwijze="x"))


def test_koppeling_standaard_aan_en_automatisch():
    k = Koppeling(global_id="WAND", calculatieregel_id="21.18", meetwijze="volume_netto")
    assert k.meegenomen is True
    assert k.bron == Koppelbron.automatisch
    assert k.reden_uitgesloten is None


def test_meetinstellingen_standaard():
    m = Meetinstellingen()
    assert m.opslag_procent == 0.0
    # Bouwkundige standaarden zijn nog niet vastgesteld door Bastiaan (fase 4)
    assert m.bruto_netto is None
    assert m.sparing_drempel_m2 is None
    assert m.zijden is None
    assert m.dagkanten_meenemen is None
    assert m.afronding_decimalen is None


def test_meetinstellingen_per_regel_overschrijven_globaal(project):
    project.instellingen = Meetinstellingen(bruto_netto="netto", zijden=2, opslag_procent=0.0,
                                            kengetallen={"wapening_kg_m3": 100.0})
    project.instellingen_per_regel["21.05"] = Meetinstellingen(zijden=1, kengetallen={"x": 1.0})
    eff = project.effectieve_instellingen("21.05")
    assert eff.zijden == 1
    assert eff.bruto_netto == "netto"
    assert eff.kengetallen == {"wapening_kg_m3": 100.0, "x": 1.0}
    assert project.effectieve_instellingen("21.18").zijden == 2


def test_meetinstellingen_ongeldige_waarden():
    with pytest.raises(ValidationError):
        Meetinstellingen(zijden=3)
    with pytest.raises(ValidationError):
        Meetinstellingen(bruto_netto="half")
    with pytest.raises(ValidationError):
        Meetinstellingen(sparing_drempel_m2=-1)
