"""Genereert het BMN-testmodel met IfcOpenShell (IFC4 én IFC2x3).

Gebruik:  .venv/bin/python tools/maak_testmodel.py [--uitvoer tests/testmodel]

Opbouw (zie CLAUDE.md en docs/testmodel_handberekening.md), lengte-eenheid mm:
- Betonvloer 10,00 x 8,00 m, dik 0,25 m; bovenkant op peil 0 (dus van -0,25 tot 0).
- Betonwand 10,00 m lang, 3,00 m hoog, 0,30 m dik, óp de vloer langs de voorrand (y = 0..0,30).
- Raamsparing 1,00 x 1,50 m in de betonwand, x = 4,50..5,50, borstwering 0,90 m.
- Betonkolom 0,40 x 0,40 m, 3,00 m hoog, vrij op de vloer (midden op x = 5,00, y = 4,00).
- Kalkzandsteenwand 5,00 m lang, 2,70 m hoog, 0,10 m dik, vrij op de vloer (x = 2..7, y = 6,00..6,10).
Er is geen overlap tussen de elementen, zodat elk volume los na te rekenen is.

Elk bouwelement krijgt materiaal (IfcMaterial), een type, de verdieping en base quantities.
GlobalIds zijn vast (afgeleid van een vaste naam), zodat ze in tests/verwacht.json staan.
"""
from __future__ import annotations

import argparse
import importlib
import itertools
import uuid
from unittest import mock
from pathlib import Path

import numpy as np

import ifcopenshell
import ifcopenshell.guid

for _module in ("aggregate", "context", "feature", "geometry", "material", "owner", "project", "pset",
                "root", "spatial", "type", "unit"):
    importlib.import_module(f"ifcopenshell.api.{_module}")
from ifcopenshell import api  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
NAMESPACE = uuid.UUID("6f1c2b9e-4d3a-5b7c-8e9f-0a1b2c3d4e5f")


def vaste_guid(sleutel: str) -> str:
    """Reproduceerbare GlobalId voor een onderdeel van het testmodel."""
    return ifcopenshell.guid.compress(uuid.uuid5(NAMESPACE, f"bmn-testmodel/{sleutel}").hex)


def plaatsing(x: float = 0.0, y: float = 0.0, z: float = 0.0) -> np.ndarray:
    """Plaatsingsmatrix in meters (de API rekent om naar mm)."""
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


VAST_TIJDSTIP = "2026-11-26T00:00:00+01:00"
VAST_TIJDSTIP_UNIX = 1795647600  # zelfde moment, voor IfcOwnerHistory


def maak_testmodel(schema: str) -> ifcopenshell.file:
    """Bouw het testmodel. Reproduceerbaar: dezelfde invoer geeft byte-voor-byte hetzelfde bestand."""
    teller = itertools.count()
    hulp_guid = lambda: vaste_guid(f"{schema}/hulp/{next(teller)}")  # noqa: E731
    with mock.patch("ifcopenshell.guid.new", hulp_guid):
        f = _bouw(schema)
    f.header.file_name.time_stamp = VAST_TIJDSTIP
    for historie in f.by_type("IfcOwnerHistory"):
        historie.CreationDate = VAST_TIJDSTIP_UNIX
        historie.LastModifiedDate = VAST_TIJDSTIP_UNIX
    # De API verzamelt gerelateerde objecten in sets; vaste volgorde voor een reproduceerbaar bestand.
    for relatie in f.by_type("IfcRelationship"):
        for i, waarde in enumerate(relatie):
            if isinstance(waarde, tuple) and waarde and all(isinstance(x, ifcopenshell.entity_instance) for x in waarde):
                relatie[i] = tuple(sorted(waarde, key=lambda x: x.id()))
    return f


def _bouw(schema: str) -> ifcopenshell.file:
    f = api.project.create_file(version=schema)

    # Eigenaar en applicatie (verplicht in IFC2x3 voor OwnerHistory).
    api.owner.add_application(f)
    persoon = api.owner.add_person(f, identification="BMN", family_name="Testmodel", given_name="BMN")
    organisatie = api.owner.add_organisation(f, identification="BMN", name="BMN De Klerk")
    api.owner.add_person_and_organisation(f, person=persoon, organisation=organisatie)

    project = api.root.create_entity(f, ifc_class="IfcProject", name="BMN testmodel")
    project.GlobalId = vaste_guid("project")
    api.unit.assign_unit(f)  # standaard: mm, m2, m3

    model = api.context.add_context(f, context_type="Model")
    body = api.context.add_context(f, context_type="Model", context_identifier="Body",
                                   target_view="MODEL_VIEW", parent=model)

    terrein = api.root.create_entity(f, ifc_class="IfcSite", name="Terrein")
    terrein.GlobalId = vaste_guid("site")
    gebouw = api.root.create_entity(f, ifc_class="IfcBuilding", name="Testgebouw")
    gebouw.GlobalId = vaste_guid("gebouw")
    verdieping = api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="00 Begane grond")
    verdieping.GlobalId = vaste_guid("verdieping_00")
    verdieping.Elevation = 0.0
    api.aggregate.assign_object(f, products=[terrein], relating_object=project)
    api.aggregate.assign_object(f, products=[gebouw], relating_object=terrein)
    api.aggregate.assign_object(f, products=[verdieping], relating_object=gebouw)
    for ruimtelijk in (terrein, gebouw, verdieping):
        api.geometry.edit_object_placement(f, product=ruimtelijk, matrix=plaatsing())

    # IFC2x3 kent geen Category op IfcMaterial.
    ifc4 = schema != "IFC2X3"
    beton = api.material.add_material(f, name="Beton C30/37", category="concrete" if ifc4 else None)
    kzs = api.material.add_material(f, name="Kalkzandsteen", category="masonry" if ifc4 else None)

    qto_naam = {"IfcWall": "Qto_WallBaseQuantities", "IfcSlab": "Qto_SlabBaseQuantities",
                "IfcColumn": "Qto_ColumnBaseQuantities"}

    def bouwelement(sleutel, klasse, naam, type_klasse, type_naam, materiaal, representatie, matrix,
                    hoeveelheden, predefined_type=None):
        # IFC2x3: IfcWall/IfcColumn hebben geen PredefinedType en IfcWallTypeEnum kent geen SOLIDWALL.
        el = api.root.create_entity(f, ifc_class=klasse, name=naam,
                                    predefined_type=predefined_type if ifc4 or klasse == "IfcSlab" else None)
        el.GlobalId = vaste_guid(sleutel)
        type_predefined = predefined_type if ifc4 else {"IfcWallType": "STANDARD"}.get(type_klasse, predefined_type)
        typ = api.root.create_entity(f, ifc_class=type_klasse, name=type_naam, predefined_type=type_predefined)
        api.type.assign_type(f, related_objects=[el], relating_type=typ)
        api.geometry.edit_object_placement(f, product=el, matrix=matrix)
        api.geometry.assign_representation(f, product=el, representation=representatie)
        api.spatial.assign_container(f, products=[el], relating_structure=verdieping)
        api.material.assign_material(f, products=[el], type="IfcMaterial", material=materiaal)
        # IFC2x3-exporters noemen de base quantities "BaseQuantities".
        naam_qto = "BaseQuantities" if schema == "IFC2X3" else qto_naam[klasse]
        qto = api.pset.add_qto(f, product=el, name=naam_qto)
        api.pset.edit_qto(f, qto=qto, properties=hoeveelheden)
        return el

    mm = 1000.0  # lengtes in base quantities staan in projecteenheid (mm)

    # Betonvloer: 10 x 8 m, dik 0,25 m, bovenkant op peil 0.
    vloer_rep = api.geometry.add_slab_representation(
        f, context=body, depth=0.25, polyline=[(0.0, 0.0), (10.0, 0.0), (10.0, 8.0), (0.0, 8.0)])
    bouwelement("betonvloer", "IfcSlab", "Betonvloer", "IfcSlabType", "Betonvloer 250", beton, vloer_rep,
                plaatsing(z=-0.25),
                {"Length": 10 * mm, "Width": 8 * mm, "Depth": 0.25 * mm, "GrossArea": 80.0, "NetArea": 80.0,
                 "GrossVolume": 20.0, "NetVolume": 20.0},
                predefined_type="FLOOR")

    # Betonwand: 10 x 3 m, dik 0,30 m, op de vloer langs de voorrand.
    wand_rep = api.geometry.add_wall_representation(f, context=body, length=10.0, height=3.0, thickness=0.3)
    wand = bouwelement("betonwand", "IfcWall", "Betonwand", "IfcWallType", "Betonwand 300", beton, wand_rep,
                       plaatsing(),
                       {"Length": 10 * mm, "Height": 3 * mm, "Width": 0.3 * mm, "GrossVolume": 9.0,
                        "NetVolume": 8.55, "GrossSideArea": 30.0, "NetSideArea": 28.5},
                       predefined_type="SOLIDWALL")

    # Raamsparing 1,00 x 1,50 m. Het sparingslichaam is iets dikker dan de wand (0,10 m aan
    # beide kanten), zodat het zeker door de hele wand snijdt; afgetrokken wordt alleen de doorsnede.
    sparing = api.root.create_entity(f, ifc_class="IfcOpeningElement", name="Raamsparing",
                                     predefined_type="OPENING" if ifc4 else None)
    sparing.GlobalId = vaste_guid("raamsparing")
    sparing_rep = api.geometry.add_wall_representation(f, context=body, length=1.0, height=1.5, thickness=0.5)
    api.geometry.edit_object_placement(f, product=sparing, matrix=plaatsing(x=4.5, y=-0.1, z=0.9))
    api.geometry.assign_representation(f, product=sparing, representation=sparing_rep)
    api.feature.add_feature(f, feature=sparing, element=wand)

    # Betonkolom 0,40 x 0,40 m, 3,00 m hoog (profiel in projecteenheid mm, hart op de plaatsing).
    # Position is verplicht in IFC2x3 (optioneel in IFC4); altijd invullen.
    oorsprong_2d = f.create_entity("IfcAxis2Placement2D", Location=f.create_entity(
        "IfcCartesianPoint", Coordinates=(0.0, 0.0)))
    profiel = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", ProfileName="400x400",
                              Position=oorsprong_2d, XDim=0.4 * mm, YDim=0.4 * mm)
    kolom_rep = api.geometry.add_profile_representation(f, context=body, profile=profiel, depth=3.0)
    bouwelement("betonkolom", "IfcColumn", "Betonkolom", "IfcColumnType", "Betonkolom 400x400", beton,
                kolom_rep, plaatsing(x=5.0, y=4.0),
                {"Length": 3 * mm, "CrossSectionArea": 0.16, "OuterSurfaceArea": 4.8, "GrossVolume": 0.48,
                 "NetVolume": 0.48},
                predefined_type="COLUMN")

    # Kalkzandsteenwand 5,00 x 2,70 m, dik 0,10 m.
    kzs_rep = api.geometry.add_wall_representation(f, context=body, length=5.0, height=2.7, thickness=0.1)
    bouwelement("kalkzandsteenwand", "IfcWall", "Kalkzandsteenwand", "IfcWallType", "Kalkzandsteenwand 100",
                kzs, kzs_rep, plaatsing(x=2.0, y=6.0),
                {"Length": 5 * mm, "Height": 2.7 * mm, "Width": 0.1 * mm, "GrossVolume": 1.35,
                 "NetVolume": 1.35, "GrossSideArea": 13.5, "NetSideArea": 13.5},
                predefined_type="SOLIDWALL")
    return f


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--uitvoer", type=Path, default=ROOT / "tests" / "testmodel")
    args = parser.parse_args()
    args.uitvoer.mkdir(parents=True, exist_ok=True)
    for schema, bestand in (("IFC4", "testmodel_ifc4.ifc"), ("IFC2X3", "testmodel_ifc2x3.ifc")):
        pad = args.uitvoer / bestand
        maak_testmodel(schema).write(str(pad))
        print(f"Geschreven: {pad}")


if __name__ == "__main__":
    main()
