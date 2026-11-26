"""Calculatieregels uitlezen uit de uittrekstaat-Excel.

De OPBOUW (tabbladen, rijen, kolommen, cellen) komt uitsluitend uit config/excel_mapping.yaml.
De INHOUD (titel, omschrijving, eenheid, verliespercentage) wordt uit de Excel zelf gelezen.
Komt een titelcel niet meer overeen met de YAML, dan is het template veranderd en stopt de lezer
met een duidelijke foutmelding (MappingFout) in plaats van stilletjes verkeerde cellen te gebruiken.

De Excel wordt alleen gelezen, nooit opgeslagen.
"""
from __future__ import annotations

from pathlib import Path

import openpyxl
import yaml

from backend.app.datamodel import Calculatieregel, Hoeveelheidskolom

GELDIGE_EENHEDEN = {"m1", "m2", "m3", "st", "kg"}


class MappingFout(Exception):
    """excel_mapping.yaml past niet (meer) bij de Excel."""


def laad_mapping(mapping_pad: Path | str) -> dict:
    data = yaml.safe_load(Path(mapping_pad).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("versie") != 1:
        raise MappingFout(f"{mapping_pad}: onbekende of ontbrekende versie (verwacht: versie: 1)")
    data.setdefault("overgeslagen_tabbladen", [])
    data.setdefault("calculatieregels", [])
    return data


def _tekst(waarde) -> str | None:
    if waarde is None:
        return None
    tekst = str(waarde).strip()
    return tekst or None


def lees_calculatieregels(mapping_pad: Path | str, excel_pad: Path | str) -> list[Calculatieregel]:
    """Lees alle calculatieregels uit `excel_pad` volgens `mapping_pad`."""
    mapping = laad_mapping(mapping_pad)
    # data_only=False: we lezen teksten en controleren dat totaalcellen formules zijn.
    wb = openpyxl.load_workbook(excel_pad, read_only=True)
    try:
        bladen: dict[str, dict[str, object]] = {}

        def cel(tabblad: str, adres: str | None):
            if adres is None:
                return None
            if tabblad not in bladen:
                if tabblad not in wb.sheetnames:
                    raise MappingFout(f"Tabblad '{tabblad}' bestaat niet in {Path(excel_pad).name}")
                bladen[tabblad] = {c.coordinate: c.value for rij in wb[tabblad].iter_rows() for c in rij
                                   if getattr(c, "coordinate", None) and c.value is not None}
            return bladen[tabblad].get(adres)

        regels: list[Calculatieregel] = []
        for item in mapping["calculatieregels"]:
            rid, tabblad = item["id"], item["tabblad"]
            titel = _tekst(cel(tabblad, item["titelcel"]))
            if titel != item["titel"]:
                raise MappingFout(
                    f"Calculatieregel {rid}: cel {tabblad}!{item['titelcel']} bevat '{titel}', "
                    f"verwacht '{item['titel']}'. Is het template gewijzigd? Pas config/excel_mapping.yaml aan.")

            hoeveelheden = []
            for h in item["hoeveelheden"]:
                if not str(cel(tabblad, h["totaalcel"]) or "").startswith("="):
                    raise MappingFout(f"Calculatieregel {rid}: totaalcel {tabblad}!{h['totaalcel']} bevat geen formule.")
                eenheid = _tekst(cel(tabblad, h.get("eenheidcel")))
                verlies = cel(tabblad, h.get("verliescel"))
                hoeveelheden.append(Hoeveelheidskolom(
                    naam=h["naam"],
                    kolom=h["kolom"],
                    eenheid=eenheid if eenheid in GELDIGE_EENHEDEN else None,
                    totaalcel=h["totaalcel"],
                    verliescel=h.get("verliescel"),
                    verlies_procent=float(verlies) if isinstance(verlies, (int, float)) else None,
                ))

            regels.append(Calculatieregel(
                id=rid,
                hoofdstuk=str(item.get("hoofdstuk") or tabblad.lstrip("§").strip()),
                tabblad=tabblad,
                titel=titel,
                omschrijving=_tekst(cel(tabblad, item.get("omschrijvingcel"))),
                hoeveelheden=hoeveelheden,
                invoerkolommen={str(k): str(v) for k, v in (item.get("invoerkolommen") or {}).items()},
                invoerrijen=list(item.get("invoerrijen") or []),
                waarschuwingen=list(item.get("waarschuwingen") or []),
            ))
        return regels
    finally:
        wb.close()
