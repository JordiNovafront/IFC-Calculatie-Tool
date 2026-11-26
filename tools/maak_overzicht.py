"""Maakt docs/fase0_overzicht.html: overzichtspagina voor het controlemoment van fase 0.

Gebruik:  .venv/bin/python tools/maak_overzicht.py   (draait ook de tests en zet de uitslag erin)

Eén los HTML-bestand zonder externe bronnen: openen door erop te dubbelklikken, werkt offline.
De inhoud komt uit het testmodel (IFC), tests/verwacht.json, config/excel_mapping.yaml en de
open vragen in CLAUDE.md, zodat de pagina altijd overeenkomt met de code.
Dit is NIET de tool zelf (die komt in fase 1).
"""
from __future__ import annotations

import argparse
import datetime
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import ifcopenshell  # noqa: E402
import ifcopenshell.geom  # noqa: E402

from backend.app.excel.calculatieregels import laad_mapping, lees_calculatieregels  # noqa: E402

E = html.escape


def nl(getal: float, decimalen: int = 2) -> str:
    """29.03 -> '29,03'; 1234.5 -> '1.234,50'."""
    return f"{getal:,.{decimalen}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def _md_inline(tekst: str) -> str:
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", E(tekst))


def open_vragen() -> list[str]:
    tekst = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(r"## Open vragen voor Bastiaan\n(.*?)(\n## |\Z)", tekst, re.S)
    vragen: list[str] = []
    for regel in (m.group(1) if m else "").splitlines():
        if re.match(r"\d+\.\s", regel):
            vragen.append(re.sub(r"^\d+\.\s+", "", regel).strip())
        elif regel.strip() and vragen:
            vragen[-1] += " " + regel.strip()
    return vragen


def kaders(ifc_pad: Path) -> dict[str, dict]:
    """Omhullende kader (min/max x, y, z in meters) per element en sparing, uit de echte geometrie."""
    f = ifcopenshell.open(str(ifc_pad))
    instellingen = ifcopenshell.geom.settings()
    instellingen.set("use-world-coords", True)
    uit = {}
    for el in f.by_type("IfcBuildingElement") + f.by_type("IfcOpeningElement"):
        # Shape eerst in een variabele houden: bij een gekoppelde aanroep ruimt IfcOpenShell het
        # tijdelijke object op voordat de coördinaten gekopieerd zijn (geheugenrommel).
        shape = ifcopenshell.geom.create_shape(instellingen, el)
        v = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
        uit[el.GlobalId] = {"naam": el.Name, "klasse": el.is_a(), "min": v.min(0), "max": v.max(0)}
    return uit


def plattegrond(kaders_: dict, verwacht: dict) -> str:
    """Bovenaanzicht (x-y) van het testmodel als SVG."""
    tm = verwacht["testmodel"]
    s, m = 56, 40  # px per meter, marge
    xs = [k["max"][0] for k in kaders_.values()]
    ys = [k["max"][1] for k in kaders_.values()]
    b, h = max(xs) * s + 2 * m, max(ys) * s + 2 * m
    hoogte_y = max(ys)

    def rect(k, klasse, extra=""):
        x0, y0 = k["min"][0], k["min"][1]
        x1, y1 = k["max"][0], k["max"][1]
        return (f'<rect x="{m + x0 * s:.1f}" y="{m + (hoogte_y - y1) * s:.1f}" width="{(x1 - x0) * s:.1f}" '
                f'height="{(y1 - y0) * s:.1f}" class="{klasse}" {extra}/>')

    stukken = []
    volgorde = ["betonvloer", "betonwand", "betonkolom", "kalkzandsteenwand"]
    klassen = {"betonvloer": "vloer", "betonwand": "beton", "betonkolom": "beton", "kalkzandsteenwand": "kzs"}
    for sleutel in volgorde:
        e = tm["elementen"][sleutel]
        k = kaders_[e["global_id"]]
        stukken.append(f'<g data-guid="{e["global_id"]}"><title>{E(e["naam"])}</title>{rect(k, klassen[sleutel])}</g>')
    sp = tm["sparingen"]["raamsparing"]
    ks = kaders_[sp["global_id"]]
    wand = kaders_[tm["elementen"]["betonwand"]["global_id"]]
    # sparing alleen tekenen binnen de wanddikte
    ks_wand = {"min": np.array([ks["min"][0], wand["min"][1], 0]), "max": np.array([ks["max"][0], wand["max"][1], 0])}
    stukken.append(f'<g data-guid="{sp["global_id"]}"><title>{E(sp["naam"])}</title>{rect(ks_wand, "sparing")}</g>')

    def label(x, y, tekst, anker="middle"):
        return (f'<text x="{m + x * s:.1f}" y="{m + (hoogte_y - y) * s:.1f}" text-anchor="{anker}" '
                f'class="label">{E(tekst)}</text>')

    stukken += [
        label(5, 7.2, "Betonvloer 10,00 × 8,00 m, dik 0,25"),
        label(5, 0.75, "Betonwand 10,00 × 3,00 m, dik 0,30 (met raamsparing)"),
        label(5.35, 4.45, "Betonkolom 0,40 × 0,40", "start"),
        label(4.5, 5.6, "Kalkzandsteenwand 5,00 × 2,70 m, dik 0,10"),
        # maatlijnen
        f'<line x1="{m}" y1="{h - 12}" x2="{m + 10 * s}" y2="{h - 12}" class="maat"/>',
        f'<text x="{m + 5 * s}" y="{h - 16}" text-anchor="middle" class="maattekst">10,00 m</text>',
        f'<line x1="{b - 12}" y1="{m}" x2="{b - 12}" y2="{m + 8 * s}" class="maat"/>',
        f'<text x="{b - 16}" y="{m + 4 * s}" text-anchor="middle" class="maattekst" '
        f'transform="rotate(-90 {b - 16} {m + 4 * s})">8,00 m</text>',
    ]
    return (f'<svg viewBox="0 0 {b:.0f} {h + 8:.0f}" role="img" aria-label="Plattegrond testmodel">'
            + "".join(stukken) + "</svg>")


def aanzicht_wand(kaders_: dict, verwacht: dict) -> str:
    """Aanzicht (x-z) van de betonwand met de raamsparing."""
    tm = verwacht["testmodel"]
    s, m = 56, 40
    w = kaders_[tm["elementen"]["betonwand"]["global_id"]]
    sp = kaders_[tm["sparingen"]["raamsparing"]["global_id"]]
    lengte, hoogte = w["max"][0] - w["min"][0], w["max"][2] - w["min"][2]
    b, h = lengte * s + 2 * m, hoogte * s + 2 * m

    def z(waarde):
        return m + (hoogte - waarde) * s

    return (
        f'<svg viewBox="0 0 {b:.0f} {h:.0f}" role="img" aria-label="Aanzicht betonwand">'
        f'<rect x="{m}" y="{z(hoogte)}" width="{lengte * s}" height="{hoogte * s}" class="beton"/>'
        f'<rect x="{m + sp["min"][0] * s}" y="{z(sp["max"][2])}" width="{(sp["max"][0] - sp["min"][0]) * s}" '
        f'height="{(sp["max"][2] - sp["min"][2]) * s}" class="sparing"/>'
        f'<line x1="{m}" y1="{z(0)}" x2="{m + lengte * s}" y2="{z(0)}" class="peil"/>'
        f'<text x="{m - 6}" y="{z(0) + 4}" text-anchor="end" class="maattekst">±0</text>'
        f'<text x="{m + 5 * s}" y="{z(sp["max"][2]) - 8}" text-anchor="middle" class="label">'
        f'raamsparing 1,00 × 1,50 m</text>'
        f'<text x="{m + 5 * s}" y="{z(0.45)}" text-anchor="middle" class="maattekst">borstwering 0,90</text>'
        f'<line x1="{m}" y1="{h - 12}" x2="{m + lengte * s}" y2="{h - 12}" class="maat"/>'
        f'<text x="{m + 5 * s}" y="{h - 16}" text-anchor="middle" class="maattekst">10,00 m</text>'
        f'<line x1="{b - 12}" y1="{z(hoogte)}" x2="{b - 12}" y2="{z(0)}" class="maat"/>'
        f'<text x="{b - 16}" y="{z(1.5)}" text-anchor="middle" class="maattekst" '
        f'transform="rotate(-90 {b - 16} {z(1.5)})">3,00 m</text>'
        "</svg>"
    )


def handberekening_rijen(verwacht: dict) -> list[tuple[str, str, str, str]]:
    el = verwacht["testmodel"]["elementen"]
    sp = verwacht["testmodel"]["sparingen"]["raamsparing"]
    f3, f4 = verwacht["testmodel"]["fase_3"], verwacht["testmodel"]["fase_4"]
    w, v, k, z = el["betonwand"], el["betonvloer"], el["betonkolom"], el["kalkzandsteenwand"]
    return [
        ("Betonwand volume bruto", f"{nl(w['lengte'])} × {nl(w['hoogte'])} × {nl(w['dikte'])}", nl(w["volume_bruto"]), "m³"),
        ("Raamsparing oppervlak", f"{nl(sp['breedte'])} × {nl(sp['hoogte'])}", nl(sp["oppervlak"]), "m²"),
        ("Betonwand volume netto", f"{nl(w['volume_bruto'])} − {nl(sp['oppervlak'])} × {nl(w['dikte'])}", nl(w["volume_netto"]), "m³"),
        ("Betonwand zijvlak bruto per zijde", f"{nl(w['lengte'])} × {nl(w['hoogte'])}", nl(w["zijvlak_bruto_per_zijde"]), "m²"),
        ("Betonwand zijvlak netto per zijde", f"{nl(w['zijvlak_bruto_per_zijde'])} − {nl(sp['oppervlak'])}", nl(w["zijvlak_netto_per_zijde"]), "m²"),
        ("Betonvloer volume", f"{nl(v['lengte'])} × {nl(v['breedte'])} × {nl(v['dikte'])}", nl(v["volume_bruto"]), "m³"),
        ("Betonvloer bovenvlak", f"{nl(v['lengte'])} × {nl(v['breedte'])}", nl(v["bovenvlak"]), "m²"),
        ("Betonkolom volume", f"{nl(k['lengte'])} × {nl(k['breedte'])} × {nl(k['hoogte'])}", nl(k["volume_bruto"]), "m³"),
        ("Kalkzandsteenwand volume", f"{nl(z['lengte'])} × {nl(z['hoogte'])} × {nl(z['dikte'])}", nl(z["volume_bruto"]), "m³"),
        ("Kalkzandsteenwand zijvlak per zijde", f"{nl(z['lengte'])} × {nl(z['hoogte'])}", nl(z["zijvlak_bruto_per_zijde"]), "m²"),
        ("Fase 3 · Betonmortel netto (wand + vloer + kolom)", f"{nl(w['volume_netto'])} + {nl(v['volume_netto'])} + {nl(k['volume_netto'])}", nl(f3["betonmortel_netto_m3"]), "m³"),
        ("Fase 3 · Bekisting betonwand 2 zijden netto (zonder dagkanten)", f"2 × {nl(w['zijvlak_netto_per_zijde'])}", nl(f3["bekisting_betonwand_2_zijden_netto_m2"]), "m²"),
        ("Fase 3 · Lijmwerk kalkzandsteen", f"{nl(z['lengte'])} × {nl(z['hoogte'])}", nl(f3["lijmwerk_kalkzandsteen_m2"]), "m²"),
        ("Fase 4 · Betonwand uitgevinkt: betonmortel", f"{nl(f3['betonmortel_netto_m3'])} − {nl(w['volume_netto'])}", nl(f4["betonwand_uitgevinkt_betonmortel_m3"]), "m³"),
        ("Fase 4 · Bekisting op 1 zijde", f"{nl(w['zijvlak_netto_per_zijde'])}", nl(f4["bekisting_1_zijde_m2"]), "m²"),
    ]


CSS = """
:root{--bg:#f6f7f9;--kaart:#fff;--tekst:#1c2430;--zacht:#5b6675;--lijn:#dfe3e8;--accent:#1f5fa8;
--beton:#8fa3b8;--vloer:#d5dde6;--kzs:#d9a66b;--sparing:#fff;--waarsch:#b25b00;--waarsch-bg:#fff4e5;--ok:#1f7a3f}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#13171c;--kaart:#1b2128;--tekst:#e6eaef;
--zacht:#9aa6b4;--lijn:#2c343e;--accent:#6aa7ec;--beton:#6f8297;--vloer:#3a4552;--kzs:#a87c4c;--sparing:#13171c;
--waarsch:#f0a34a;--waarsch-bg:#2e2416;--ok:#5cc386}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tekst);
font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{background:var(--kaart);border-bottom:1px solid var(--lijn);padding:20px 16px}
header .in,main{max-width:1100px;margin:0 auto}h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--zacht);font-size:14px}.badges{margin-top:10px;display:flex;gap:8px;flex-wrap:wrap}
.badge{font-size:13px;padding:3px 10px;border-radius:999px;border:1px solid var(--lijn);background:var(--bg)}
.badge.ok{color:var(--ok);border-color:currentColor}.badge.wacht{color:var(--waarsch);border-color:currentColor}
nav{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--lijn)}
nav .in{max-width:1100px;margin:0 auto;padding:8px 16px;display:flex;gap:16px;overflow-x:auto}
nav a{color:var(--accent);text-decoration:none;white-space:nowrap;font-size:14px}
main{padding:8px 16px 48px}section{background:var(--kaart);border:1px solid var(--lijn);border-radius:10px;
padding:18px;margin:16px 0}h2{font-size:18px;margin:0 0 4px}.uitleg{color:var(--zacht);margin:0 0 14px;font-size:14px}
.tekeningen{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media (max-width:760px){.tekeningen{grid-template-columns:1fr}}
figure{margin:0}figcaption{font-size:13px;color:var(--zacht);margin-top:4px}svg{width:100%;height:auto;display:block}
svg .vloer{fill:var(--vloer);stroke:var(--zacht);stroke-width:1}svg .beton{fill:var(--beton);stroke:var(--tekst);stroke-width:1}
svg .kzs{fill:var(--kzs);stroke:var(--tekst);stroke-width:1}svg .sparing{fill:var(--sparing);stroke:var(--tekst);
stroke-dasharray:4 3}svg .label{font-size:12px;fill:var(--tekst)}svg .maattekst{font-size:11px;fill:var(--zacht)}
svg .maat,svg .peil{stroke:var(--zacht);stroke-width:1}svg .peil{stroke-dasharray:6 4}
svg g[data-guid]:hover rect{stroke:var(--accent);stroke-width:2.5}
.tabelwrap{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--lijn);vertical-align:top}
th{font-size:12px;text-transform:uppercase;letter-spacing:.03em;color:var(--zacht);font-weight:600}
td.getal{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}td.uitkomst{font-weight:600}
tr.fase td:first-child{color:var(--accent)}code{font-size:13px;background:var(--bg);padding:1px 4px;border-radius:4px}
.filters{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:10px;align-items:center}
input[type=search],select{font:inherit;padding:6px 10px;border:1px solid var(--lijn);border-radius:6px;
background:var(--bg);color:var(--tekst)}input[type=search]{flex:1;min-width:180px}
.teller{color:var(--zacht);font-size:13px}.w{display:inline-block;font-size:12px;color:var(--waarsch);
background:var(--waarsch-bg);border-radius:4px;padding:0 6px;margin:2px 0}
.waarsch td:last-child{color:var(--waarsch)}ol{margin:0;padding-left:22px}ol li{margin:6px 0}
.veel{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;align-items:center;font-size:14px}
.veel .el{font-weight:600}.veel .pijl{color:var(--zacht)}
.kolommen{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
.kaartje{border:1px solid var(--lijn);border-radius:8px;padding:10px 12px}.kaartje b{display:block}
footer{color:var(--zacht);font-size:13px;text-align:center;padding:16px}
input[type=checkbox]{width:16px;height:16px;accent-color:var(--accent)}
"""

JS = """
(function(){
  var zoek=document.getElementById('zoek'),tab=document.getElementById('tab'),
      alleenW=document.getElementById('alleenW'),teller=document.getElementById('teller'),
      rijen=[].slice.call(document.querySelectorAll('#regels tbody tr'));
  function filter(){
    var q=zoek.value.toLowerCase().trim(),t=tab.value,n=0;
    rijen.forEach(function(r){
      var ok=(!q||r.textContent.toLowerCase().indexOf(q)>=0)&&(!t||r.dataset.tab===t)&&(!alleenW.checked||r.dataset.w==='1');
      r.hidden=!ok;if(ok)n++;});
    teller.textContent=n+' van '+rijen.length+' regels';
  }
  [zoek,tab,alleenW].forEach(function(e){e.addEventListener('input',filter);e.addEventListener('change',filter);});
  filter();
  // Afvinken door Bastiaan: alleen in deze browser bewaard
  document.querySelectorAll('input[data-check]').forEach(function(c){
    var k='bmn-fase0-'+c.dataset.check;
    try{c.checked=localStorage.getItem(k)==='1';}catch(e){}
    c.addEventListener('change',function(){try{localStorage.setItem(k,c.checked?'1':'0');}catch(e){}});
  });
})();
"""


def maak_overzicht(uitvoer: Path, testresultaat: str | None = None) -> Path:
    verwacht = json.loads((ROOT / "tests" / "verwacht.json").read_text(encoding="utf-8"))
    tm = verwacht["testmodel"]
    k = kaders(ROOT / tm["bestanden"]["IFC4"])
    mapping_pad = ROOT / "config" / "excel_mapping.yaml"
    template_pad = ROOT / verwacht["excel"]["template"]
    regels = lees_calculatieregels(mapping_pad, template_pad)
    mapping = laad_mapping(mapping_pad)
    met_w = [r for r in regels if r.waarschuwingen]
    tabbladen = sorted({r.tabblad for r in regels}, key=lambda t: (len(t), t))

    rij_hand = "".join(
        f'<tr class="{"fase" if post.startswith("Fase") else ""}"><td>{E(post)}</td><td>{E(som)}</td>'
        f'<td class="getal uitkomst">{E(uit)} {eenh}</td>'
        f'<td><input type="checkbox" data-check="hand{i}" aria-label="klopt"></td></tr>'
        for i, (post, som, uit, eenh) in enumerate(handberekening_rijen(verwacht)))

    rij_el = "".join(
        f'<tr><td>{E(e["naam"])}</td><td><code>{E(e["ifc_klasse"])}</code></td><td>{E(e["type_naam"])}</td>'
        f'<td>{E(e["materiaal"])}</td><td>{E(e["verdieping"])}</td><td><code>{E(e["global_id"])}</code></td></tr>'
        for e in tm["elementen"].values())

    rij_regels = []
    for r in regels:
        afgeleid = ", ".join(f"{h.naam} ({h.eenheid or '?'})" for h in r.afgeleide_hoeveelheden)
        w = "".join(f'<div class="w">⚠ {E(x)}</div>' for x in r.waarschuwingen)
        rij_regels.append(
            f'<tr data-id="{r.id}" data-tab="{E(r.tabblad)}" data-w="{1 if r.waarschuwingen else 0}">'
            f'<td><code>{r.id}</code></td><td>{E(r.tabblad)}</td><td>{E(r.titel)}{w}</td>'
            f'<td>{E(r.omschrijving or "")}</td><td>{E(r.eenheid or "?")}</td><td>{E(afgeleid)}</td>'
            f'<td><code>{E(r.hoeveelheden[0].totaalcel or "")}</code></td></tr>')

    rij_w = "".join(f'<tr class="waarsch"><td><code>{r.id}</code></td><td>{E(r.titel)}</td><td>{E(w)}</td></tr>'
                    for r in met_w for w in r.waarschuwingen)
    rij_over = "".join(f"<tr><td>{E(t['tabblad'])}</td><td>{E(t['reden'])}</td></tr>"
                       for t in mapping["overgeslagen_tabbladen"])
    vragen = "".join(f"<li>{_md_inline(v)}</li>" for v in open_vragen())
    opties = "".join(f'<option value="{E(t)}">{E(t)}</option>' for t in tabbladen)
    datum = datetime.date.today().strftime("%d-%m-%Y")
    test_badge = (f'<span class="badge ok">Tests: {E(testresultaat)}</span>' if testresultaat and "failed" not in testresultaat
                  else f'<span class="badge wacht">Tests: {E(testresultaat or "niet gedraaid")}</span>')

    pagina = f"""<!doctype html>
<html lang="nl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fase 0 overzicht</title><style>{CSS}</style></head>
<body>
<header><div class="in">
<h1>IFC-hoeveelhedentool · Fase 0 – controle</h1>
<div class="sub">BMN De Klerk · controlemoment 0 voor Bastiaan (±30 min) · gegenereerd {datum}</div>
<div class="badges"><span class="badge wacht">Status: wacht op akkoord</span>{test_badge}
<span class="badge">{len(regels)} calculatieregels</span><span class="badge">{len(met_w)} regels met waarschuwing</span></div>
</div></header>
<nav><div class="in"><a href="#testmodel">Testmodel</a><a href="#handberekening">Handberekening</a>
<a href="#veel">Veel-op-veel</a><a href="#regels-sectie">Calculatieregels</a><a href="#waarschuwingen">Waarschuwingen</a>
<a href="#vragen">Open vragen</a></div></nav>
<main>
<section id="testmodel"><h2>Testmodel</h2>
<p class="uitleg">Tekening gemaakt uit de echte geometrie van <code>{E(tm["bestanden"]["IFC4"])}</code>
(ook als IFC2x3). Open het IFC-bestand in BIMcollab Zoom om het in 3D te bekijken. Beweeg over een element voor de naam.</p>
<div class="tekeningen">
<figure>{plattegrond(k, verwacht)}<figcaption>Bovenaanzicht · alle elementen op verdieping "{E(tm["verdieping"]["naam"])}"</figcaption></figure>
<figure>{aanzicht_wand(k, verwacht)}<figcaption>Aanzicht betonwand met raamsparing (stippellijn)</figcaption></figure>
</div>
<div class="tabelwrap" style="margin-top:14px"><table><thead><tr><th>Element</th><th>IFC-klasse</th><th>Type</th>
<th>Materiaal</th><th>Verdieping</th><th>GlobalId</th></tr></thead><tbody>{rij_el}</tbody></table></div>
</section>

<section id="handberekening"><h2>Handberekening</h2>
<p class="uitleg">Graag narekenen en afvinken. Het vinkje wordt alleen in deze browser bewaard.
Vul aan met posten die bij ons vaak fout gaan.</p>
<div class="tabelwrap"><table><thead><tr><th>Post</th><th>Berekening</th><th style="text-align:right">Uitkomst</th>
<th>Klopt</th></tr></thead><tbody>{rij_hand}</tbody></table></div>
<p class="uitleg" style="margin-top:10px">Ter info (vraag voor fase 3): dagkanten van de sparing zijn
2 × 1,50 × 0,30 + 2 × 1,00 × 0,30 = 1,50 m². Die zitten níet in de 57,00 m² bekisting.</p>
</section>

<section id="veel"><h2>Veel-op-veel</h2>
<p class="uitleg">Eén element hangt aan meerdere calculatieregels, en één calculatieregel telt veel elementen op.
Klopt dit met hoe wij calculeren?</p>
<div class="kolommen">
<div class="kaartje"><b>Eén element → meerdere regels</b>
<div class="veel"><span class="el">Betonwand</span><span class="pijl">→ betonmortel (m³)</span>
<span></span><span class="pijl">→ bekisting (m²)</span><span></span><span class="pijl">→ wapening (kg, via kg/m³)</span>
<span></span><span class="pijl">→ schilderwerk (m²)</span></div></div>
<div class="kaartje"><b>Eén regel ← meerdere elementen</b>
<div class="veel"><span class="el">Betonmortel</span><span class="pijl">← betonwand 8,55 m³</span>
<span></span><span class="pijl">← betonvloer 20,00 m³</span><span></span><span class="pijl">← betonkolom 0,48 m³</span>
<span></span><span class="pijl">= 29,03 m³</span></div></div>
</div></section>

<section id="regels-sectie"><h2>Uitgelezen calculatieregels</h2>
<p class="uitleg">Zo leest de tool de uittrekstaat. Komen code, titel, omschrijving en eenheid overeen met de Excel?
Code = hoofdstuk.volgnummer binnen het tabblad.</p>
<div class="filters"><input type="search" id="zoek" placeholder="Zoek op titel, omschrijving of code…">
<select id="tab"><option value="">Alle tabbladen</option>{opties}</select>
<label><input type="checkbox" id="alleenW"> alleen met waarschuwing</label><span class="teller" id="teller"></span></div>
<div class="tabelwrap"><table id="regels"><thead><tr><th>Code</th><th>Tabblad</th><th>Titel</th><th>Omschrijving</th>
<th>Eenheid</th><th>Afgeleid</th><th>Totaalcel</th></tr></thead><tbody>{"".join(rij_regels)}</tbody></table></div>
</section>

<section id="waarschuwingen"><h2>Waarschuwingen over het template</h2>
<p class="uitleg">Automatisch gevonden. Fout in het template, of bewust zo? Het template zelf wijzigen we niet.</p>
<div class="tabelwrap"><table><thead><tr><th>Code</th><th>Titel</th><th>Waarschuwing</th></tr></thead>
<tbody>{rij_w}</tbody></table></div>
<h2 style="margin-top:18px;font-size:16px">Tabbladen zonder calculatieregels</h2>
<div class="tabelwrap"><table><thead><tr><th>Tabblad</th><th>Reden</th></tr></thead><tbody>{rij_over}</tbody></table></div>
</section>

<section id="vragen"><h2>Open vragen voor Bastiaan</h2><ol>{vragen}</ol></section>
</main>
<footer>Gegenereerd door <code>tools/maak_overzicht.py</code> · volledig lokaal, geen internetverbinding nodig ·
dit is nog niet de tool zelf (die volgt in fase 1)</footer>
<script>{JS}</script>
</body></html>
"""
    uitvoer.parent.mkdir(parents=True, exist_ok=True)
    uitvoer.write_text(pagina, encoding="utf-8")
    return uitvoer


def draai_tests() -> str:
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=ROOT,
                       capture_output=True, text=True)
    regels = [x for x in r.stdout.strip().splitlines() if x.strip()]
    return re.sub(r"=+", "", regels[-1]).strip() if regels else "onbekend"


def main() -> None:
    p = argparse.ArgumentParser(description="Maak de overzichtspagina van fase 0")
    p.add_argument("--uitvoer", type=Path, default=ROOT / "docs" / "fase0_overzicht.html")
    p.add_argument("--zonder-tests", action="store_true", help="tests niet draaien")
    args = p.parse_args()
    uitslag = None if args.zonder_tests else draai_tests()
    print(f"Geschreven: {maak_overzicht(args.uitvoer, uitslag)}  (tests: {uitslag or 'niet gedraaid'})")


if __name__ == "__main__":
    main()
