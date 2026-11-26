"""Eenmalige scan van het uittrekstaat-template -> config/excel_mapping.yaml (+ docs/excel_analyse.md).

Gebruik:
    .venv/bin/python tools/genereer_excel_mapping.py [--template ...] [--uitvoer ...] [--overschrijf]

Na deze eerste generatie is config/excel_mapping.yaml LEIDEND en wordt hij met de hand bijgehouden.
De applicatie zelf leest de opbouw van de Excel uitsluitend uit die YAML, nooit uit dit script.
Opnieuw genereren overschrijft handmatige wijzigingen en gebeurt daarom alleen met --overschrijf.
Het analyse-document (docs/excel_analyse.md) kan altijd opnieuw gemaakt worden met --alleen-analyse.

Hoe het template herkend wordt (vastgesteld op het template van 26-11-2026):
- Een blok (= calculatieregel) begint bij een kopregel: kolom A = "Omschrijving" of kolom B = "nr.".
- De titel staat in kolom A van de rij boven de kopregel.
- Het blok eindigt bij de eerste rij waarvan kolom A met "Totaal" begint.
- Hoeveelheidskolommen = kolommen met een formule in de totaalregel (prijskolommen uitgezonderd).
  De eenheid staat in de kolom rechts ervan.
- Invoerrijen = rijen tussen kopregel en (sub)totaal met een formule in een hoeveelheidskolom.
- Een rij met het woord "verlies" bevat per hoeveelheidskolom het verliespercentage.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
import yaml
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

EENHEDEN = {"m1", "m2", "m3", "st", "kg"}
MAATKOLOMMEN = {"omschrijving", "nr.", "lengte", "hoogte", "breedte", "aantal"}
CELREF = re.compile(r"(\$?)([A-Z]{1,3})(\$?)(\d+)")
SOM = re.compile(r"SUM\(([A-Z]{1,3})(\d+):([A-Z]{1,3})(\d+)\)", re.IGNORECASE)


def _tekst(waarde) -> str | None:
    return waarde.strip() if isinstance(waarde, str) and waarde.strip() else None


def _is_formule(waarde) -> bool:
    return isinstance(waarde, str) and waarde.startswith("=")


def _is_kopregel(ws, r: int) -> bool:
    a, b = _tekst(ws.cell(r, 1).value), _tekst(ws.cell(r, 2).value)
    return (a or "").lower() == "omschrijving" or (b or "").lower() == "nr."


def _relatief(formule: str, rij: int) -> str:
    """Formule met rijnummers relatief t.o.v. de eigen rij, om formules per rij te vergelijken."""
    return CELREF.sub(lambda m: f"{m[1]}{m[2]}{m[3]}[{int(m[4]) - rij:+d}]", formule)


def _bereiken(kolom: str, rijen: list[int]) -> str:
    """[60, 61, 62, 64] -> 'J60:J62, J64'."""
    delen, start, vorige = [], rijen[0], rijen[0]
    for r in rijen[1:] + [None]:
        if r is not None and r == vorige + 1:
            vorige = r
            continue
        delen.append(f"{kolom}{start}" if start == vorige else f"{kolom}{start}:{kolom}{vorige}")
        if r is not None:
            start = vorige = r
    return ", ".join(delen)


def scan_blok(ws, kop: int, volgende_kop: int) -> tuple[dict | None, str | None]:
    """Scan één blok vanaf kopregel `kop`. Geeft (regel, None) of (None, reden_overgeslagen)."""
    waarschuwingen: list[str] = []
    totaal = subtotaal = verlies = None
    for r in range(kop + 1, volgende_kop):
        a = (_tekst(ws.cell(r, 1).value) or "").lower()
        if a.startswith("subtotaal") and subtotaal is None:
            subtotaal = r
        elif a.startswith("totaal"):
            totaal = r
            break
        if any((_tekst(ws.cell(r, c).value) or "").lower() == "verlies" for c in range(1, ws.max_column + 1)):
            verlies = r
    if totaal is None:
        return None, "geen totaalregel"

    kopnamen = {c: _tekst(ws.cell(kop, c).value) for c in range(1, ws.max_column + 1)}
    hoeveelheidskolommen = [
        c for c in range(1, ws.max_column + 1)
        if _is_formule(ws.cell(totaal, c).value)
        and not any(p in (kopnamen.get(c) or "").lower() for p in ("prijs", "pr."))
    ]
    if not hoeveelheidskolommen:
        prijs = any(_is_formule(ws.cell(totaal, c).value) for c in range(1, ws.max_column + 1))
        return None, "alleen prijskolommen, geen hoeveelheden" if prijs else "geen formules in de totaalregel"

    # Opgetelde invoerkolommen (bijv. 'aantal' bij kozijnen) komen achteraan: de hoofdhoeveelheid
    # is de eerste echte uitkomstkolom ('tot.').
    telkolommen = [c for c in hoeveelheidskolommen if (kopnamen.get(c) or "").lower() in MAATKOLOMMEN]
    if len(telkolommen) < len(hoeveelheidskolommen):
        hoeveelheidskolommen = [c for c in hoeveelheidskolommen if c not in telkolommen] + telkolommen

    eind = (subtotaal or totaal) - 1
    invoerrijen = [r for r in range(kop + 1, eind + 1)
                   if any(_is_formule(ws.cell(r, c).value) for c in hoeveelheidskolommen)]

    # Titel en omschrijving
    titelrij = kop - 1
    if kop > 1 and _tekst(ws.cell(kop - 1, 1).value):
        titelcel = f"A{kop - 1}"
    elif invoerrijen and _tekst(ws.cell(invoerrijen[0], 1).value):
        titelrij = invoerrijen[0]
        titelcel = f"A{titelrij}"
        waarschuwingen.append(f"Geen titel boven de kopregel (rij {kop}); titel genomen uit {titelcel}.")
    else:
        return None, "geen titel"
    omschrijvingcel = next((f"A{r}" for r in invoerrijen if _tekst(ws.cell(r, 1).value)), None)

    hoeveelheden = []
    for c in hoeveelheidskolommen:
        kol = get_column_letter(c)
        ekol = get_column_letter(c + 1)
        h: dict = {"naam": kopnamen.get(c) or f"kolom {kol}", "kolom": kol}

        # Eenheid: rechts van de hoeveelheid, in de invoerrijen
        eenheden = {r: _tekst(ws.cell(r, c + 1).value) for r in invoerrijen if _is_formule(ws.cell(r, c).value)}
        gevonden = {e for e in eenheden.values() if e}
        totaal_eenheid = _tekst(ws.cell(totaal, c + 1).value)
        if len(gevonden) == 1 and gevonden <= EENHEDEN:
            eenheid = gevonden.pop()
            h["eenheidcel"] = f"{ekol}{next(r for r, e in eenheden.items() if e)}"
            if totaal_eenheid and totaal_eenheid != eenheid:
                waarschuwingen.append(f"Totaalregel {ekol}{totaal} noemt eenheid '{totaal_eenheid}', "
                                      f"invoerrijen '{eenheid}'.")
        elif len(gevonden) > 1:
            waarschuwingen.append(f"Kolom {kol}: gemengde eenheden in de invoerrijen ({', '.join(sorted(gevonden))}); "
                                  f"totaal {kol}{totaal} telt ze op.")
        elif gevonden:
            waarschuwingen.append(f"Kolom {kol}: onbekende eenheid '{gevonden.pop()}'.")
        elif c in telkolommen:
            waarschuwingen.append(f"Kolom {kol} ('{h['naam']}'): totaal {kol}{totaal} telt de invoer op; "
                                  f"eenheid ontbreekt in het template.")
        else:
            waarschuwingen.append(f"Kolom {kol}: eenheid ontbreekt in het template.")
        h["totaalcel"] = f"{kol}{totaal}"

        # Verlies
        if verlies:
            vcel = f"{kol}{verlies}"
            vwaarde = ws.cell(verlies, c).value
            if isinstance(vwaarde, (int, float)) or vcel in str(ws.cell(totaal, c).value):
                h["verliescel"] = vcel

        # Totaalbereik controleren
        for formule_rij in (subtotaal, totaal):
            if formule_rij is None:
                continue
            formule = str(ws.cell(formule_rij, c).value or "")
            for m in SOM.finditer(formule):
                van, tot = int(m[2]), int(m[4])
                rijen_met_formule = [r for r in invoerrijen if _is_formule(ws.cell(r, c).value)]
                if rijen_met_formule and (van < kop or van > rijen_met_formule[0] or tot < rijen_met_formule[-1]):
                    waarschuwingen.append(
                        f"Totaalformule {kol}{formule_rij} telt {m[1]}{van}:{m[3]}{tot}, maar de invoerrijen "
                        f"van dit blok zijn {kol}{rijen_met_formule[0]}:{kol}{rijen_met_formule[-1]}.")

        # Formules binnen de kolom vergelijken
        patronen: dict[str, list[int]] = defaultdict(list)
        for r in invoerrijen:
            if _is_formule(ws.cell(r, c).value):
                patronen[_relatief(ws.cell(r, c).value, r)].append(r)
        if len(patronen) > 1:
            delen = [f"{_bereiken(kol, rijen)} '{ws.cell(rijen[0], c).value}'" for rijen in patronen.values()]
            waarschuwingen.append(f"Kolom {kol}: formules verschillen binnen het blok: {' / '.join(delen)}.")
        hoeveelheden.append(h)

    # Invoerkolommen: koppen links van de laatste eenheidskolom, geen hoeveelheid of eenheid
    laatste = max(hoeveelheidskolommen) + 1
    eenheidskolommen = {c + 1 for c in hoeveelheidskolommen}
    invoerkolommen = {get_column_letter(c): naam for c, naam in kopnamen.items()
                      if naam and c <= laatste and c not in eenheidskolommen
                      and (c not in hoeveelheidskolommen or c in telkolommen)}

    # Kengetal-kolommen die in geen enkele formule voorkomen
    alle_formules = " ".join(str(ws.cell(r, c).value) for r in range(kop + 1, totaal + 1)
                             for c in range(1, ws.max_column + 1) if _is_formule(ws.cell(r, c).value))
    gebruikt = {m[2] for m in CELREF.finditer(alle_formules)}
    for kol, naam in invoerkolommen.items():
        if naam.lower() not in MAATKOLOMMEN and kol not in gebruikt:
            waarschuwingen.append(f"Invoerkolom {kol} ('{naam}') wordt in geen enkele formule gebruikt.")

    regel = {
        "titel": _tekst(ws[titelcel].value),
        "titelcel": titelcel,
        "kopregel": kop,
        "omschrijvingcel": omschrijvingcel,
        "invoerrijen": invoerrijen,
        "invoerkolommen": invoerkolommen,
        "hoeveelheden": hoeveelheden,
        "waarschuwingen": waarschuwingen,
    }
    return regel, None


def scan_template(template: Path) -> dict:
    wb = openpyxl.load_workbook(template)  # formules, geen waarden
    regels, overgeslagen = [], []
    for ws in wb.worksheets:
        hoofdstuk = ws.title.lstrip("§").strip()
        koppen = [r for r in range(1, ws.max_row + 1) if _is_kopregel(ws, r)]
        redenen = []
        n = 0
        for i, kop in enumerate(koppen):
            volgende = koppen[i + 1] if i + 1 < len(koppen) else ws.max_row + 1
            regel, reden = scan_blok(ws, kop, volgende)
            if regel is None:
                redenen.append(reden)
                continue
            n += 1
            regels.append({"id": f"{hoofdstuk}.{n:02d}", "tabblad": ws.title, **regel})
        if n == 0:
            overgeslagen.append({"tabblad": ws.title,
                                 "reden": "; ".join(sorted(set(redenen))) or "geen blokken gevonden"})
    return {"versie": 1, "standaard_template": str(template.relative_to(ROOT)) if template.is_relative_to(ROOT)
            else str(template), "overgeslagen_tabbladen": overgeslagen, "calculatieregels": regels}


class _Dumper(yaml.SafeDumper):
    pass


def _lijst(dumper, data):
    eenvoudig = all(isinstance(x, (int, float, str)) for x in data) and not any(
        isinstance(x, str) and len(x) > 40 for x in data)
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=eenvoudig)


def _dict(dumper, data):
    eenvoudig = all(isinstance(v, (int, float, str)) for v in data.values()) and len(data) <= 12
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items(), flow_style=eenvoudig)


_Dumper.add_representer(list, _lijst)
_Dumper.add_representer(dict, _dict)

KOP = """\
# excel_mapping.yaml – opbouw van de BMN-uittrekstaat
#
# LEIDEND BESTAND: de applicatie leest sheetnamen, rijen, kolommen en cellen alleen hieruit.
# Eerste versie gegenereerd met tools/genereer_excel_mapping.py op het template in referentie/;
# daarna met de hand bijhouden. Verandert het template, pas dan alleen dit bestand aan.
#
# Per calculatieregel (= één blok in de uittrekstaat):
#   id               <hoofdstuk>.<volgnummer>, vaste sleutel (titels zijn niet uniek)
#   tabblad          naam van het tabblad
#   titel / titelcel titel ter controle: de lezer meldt een fout als de cel iets anders bevat
#   kopregel         rij met Omschrijving | nr. | lengte | ...
#   omschrijvingcel  cel met de omschrijving van de eerste invoerrij
#   invoerrijen      rijen die gevuld worden (fase 5)
#   invoerkolommen   kolom -> kopnaam van de invoervelden (maten, aantallen, kengetallen)
#   hoeveelheden     uitkomsten van het blok; de eerste is de hoofdhoeveelheid
#                    naam, kolom, eenheidcel, totaalcel, verliescel (optioneel)
#   waarschuwingen   opvallende zaken in het template, ter beoordeling door Bastiaan
"""


def schrijf_analyse(mapping_pad: Path, template: Path, uitvoer: Path) -> None:
    from backend.app.excel.calculatieregels import lees_calculatieregels, laad_mapping

    regels = lees_calculatieregels(mapping_pad, template)
    mapping = laad_mapping(mapping_pad)
    per_tab = Counter(r.tabblad for r in regels)
    met_waarschuwing = [r for r in regels if r.waarschuwingen]
    regels_md = [
        "# Uitgelezen calculatieregels uit de uittrekstaat",
        "",
        f"*Gegenereerd door `tools/genereer_excel_mapping.py` uit `{template.name}` via "
        "`config/excel_mapping.yaml`. Niet met de hand bewerken.*",
        "",
        f"**{len(regels)} calculatieregels** op {len(per_tab)} tabbladen; "
        f"{len(mapping['overgeslagen_tabbladen'])} tabbladen zonder regels; "
        f"{len(met_waarschuwing)} regels met een waarschuwing.",
        "",
        "Controle Bastiaan: kloppen code, omschrijving en eenheid met de Excel? Zijn de waarschuwingen "
        "fouten in het template of bewust zo?",
        "",
        "## Tabbladen zonder calculatieregels",
        "",
        "| Tabblad | Reden |",
        "|---|---|",
        *[f"| {t['tabblad']} | {t['reden']} |" for t in mapping["overgeslagen_tabbladen"]],
        "",
        "## Waarschuwingen",
        "",
        "| Regel | Titel | Waarschuwing |",
        "|---|---|---|",
        *[f"| {r.id} | {r.titel} | {w} |" for r in met_waarschuwing for w in r.waarschuwingen],
        "",
        "## Alle calculatieregels",
        "",
        "| Code | Tabblad | Titel | Omschrijving | Eenheid | Afgeleid | Totaalcel |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in regels:
        afgeleid = ", ".join(f"{h.naam} ({h.eenheid or '?'})" for h in r.afgeleide_hoeveelheden)
        regels_md.append(f"| {r.id} | {r.tabblad} | {r.titel} | {r.omschrijving or ''} | {r.eenheid or '?'} | "
                         f"{afgeleid} | {r.hoeveelheden[0].totaalcel} |")
    uitvoer.write_text("\n".join(regels_md).replace("|  |", "| |") + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Scan het uittrekstaat-template naar excel_mapping.yaml")
    p.add_argument("--template", type=Path, default=ROOT / "referentie" / "uittrekstaat_template.xlsx")
    p.add_argument("--uitvoer", type=Path, default=ROOT / "config" / "excel_mapping.yaml")
    p.add_argument("--analyse", type=Path, default=ROOT / "docs" / "excel_analyse.md")
    p.add_argument("--overschrijf", action="store_true", help="bestaande (handmatig bijgewerkte) YAML overschrijven")
    p.add_argument("--alleen-analyse", action="store_true", help="alleen docs/excel_analyse.md opnieuw maken")
    args = p.parse_args()

    if not args.alleen_analyse:
        if args.uitvoer.exists() and not args.overschrijf:
            sys.exit(f"{args.uitvoer} bestaat al en is leidend. Gebruik --overschrijf om opnieuw te genereren.")
        data = scan_template(args.template)
        args.uitvoer.parent.mkdir(parents=True, exist_ok=True)
        args.uitvoer.write_text(KOP + "\n" + yaml.dump(data, Dumper=_Dumper, allow_unicode=True, sort_keys=False,
                                                         width=120), encoding="utf-8")
        print(f"Geschreven: {args.uitvoer} ({len(data['calculatieregels'])} calculatieregels)")
    schrijf_analyse(args.uitvoer, args.template, args.analyse)
    print(f"Geschreven: {args.analyse}")


if __name__ == "__main__":
    main()
