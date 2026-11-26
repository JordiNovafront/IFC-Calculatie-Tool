# CLAUDE.md – IFC-hoeveelhedentool BMN De Klerk

Lokale webtool die hoeveelheden uittrekt uit IFC-modellen voor de calculatie van BMN De Klerk.
Opdrachtgever: Bastiaan (werkvoorbereider/calculator). Bouwer: Jordi Aantjes (ICT).
Volledig stappenplan: `docs/stappenplan.md` (origineel: `referentie/Stappenplan_…pdf`).

## Fasenplan en status

| Fase | Inhoud | Status | Tag |
|---|---|---|---|
| 0 | Projectopzet, datamodel, testmodel, excel_mapping.yaml | **wacht op akkoord** (82 tests groen) | – |
| 1 | IFC importeren, viewer, meten, importrapport | open | – |
| 2 | Elementen koppelen aan STABU (koppeltabel, handmatig, bewaren) | open | – |
| 3 | Hoeveelheden berekenen, overzicht, ingekleurd 3D | open | – |
| 4 | Meetinstellingen en aan/uitvinken, profiel "BMN standaard" | open | – |
| 5 | Export: ingevulde uittrekstaat + ingekleurd IFC met BMN_Calculatie | open | – |

Status: `open` / `bezig` / `wacht op akkoord` / `akkoord`. Werk deze tabel bij bij elke statuswijziging.

## Werkafspraken (hard)

- **Bouw alleen de fase die aan de beurt is.** Na elke fase stoppen en wachten tot Jordi schrijft
  "Fase X akkoord". Nooit uit jezelf aan de volgende fase beginnen.
- Elke fase begint met een plan (incl. tests en verwachte uitkomsten); pas na akkoord code schrijven.
- Eerst tests, dan code. Een fase is pas klaar als alle tests groen zijn.
- Afsluiting per fase: wat gebouwd is, testresultaten, open vragen voor Bastiaan, korte demo-instructie.
- **Nooit de opbouw van onze Excel-bestanden hardcoden.** Sheetnamen, rijen en kolommen staan in
  `config/excel_mapping.yaml`. Koppelregels staan in `config/stabu_koppeling.xlsx` (beheer Bastiaan).
- Rekenregels zijn losse functies met een herkenbare Nederlandse naam (bijv. `zijvlak_netto_2_zijden`)
  en een docstring in gewone taal die een bouwkundige kan nalezen.
- `referentie/` is **alleen-lezen** (bestanden staan op read-only; test controleert de hashes).
  Nooit het originele IFC of template wijzigen; exports zijn altijd nieuwe bestanden.
- UI in het Nederlands. Vakbegrippen (uittrekstaat, calculatieregel, meetwijze, STABU, sparing,
  dagkant, zijvlak) blijven Nederlands, ook in code.
- **Twijfel over een bouwkundige keuze** (dagkanten, overlap bij aansluitingen, meetwijze, bruto/netto)?
  Vragen aan Bastiaan via Jordi; niet zelf beslissen. Leg open vragen vast onderaan dit bestand.
- Commit na elke afgeronde deelstap; tag na akkoord (`fase-N-akkoord`).
- Alles lokaal; geen projectdata naar externe diensten.
- Controleer actuele API's (IfcOpenShell 0.8.x, That Open Engine) in docs/bron vóór je code schrijft.
- **IfcOpenShell blijft op 0.8.5** (vastgezet in `pyproject.toml`). Updaten alleen na goedkeuring van Bastiaan.

## Techniek

- Backend: Python 3.12, FastAPI, IfcOpenShell 0.8.5, openpyxl 3.1.5, pydantic 2, PyYAML. Tests: pytest.
- Frontend (vanaf fase 1): TypeScript, Vite, That Open Engine (`@thatopen/components`,
  `@thatopen/components-front`). Browsertests: Playwright.
- Opslag: **SQLite, één bestand per project** (schema volgt in fase 2).

### IfcOpenShell 0.8.5 – aandachtspunten

- API-submodules expliciet importeren: `import ifcopenshell.api.root` enz. (`ifcopenshell.api.pset`
  bestaat pas na import).
- IFC2x3 vereist OwnerHistory: maak eerst `IfcApplication` + `IfcPersonAndOrganization` aan
  (`api.owner.add_application`, `add_person`, `add_organisation`, `add_person_and_organisation`).
- `api.geometry.add_*_representation` neemt maten in **meters** en rekent om naar de projecteenheid;
  zelf aangemaakte profielen (`IfcRectangleProfileDef`) staan in projecteenheid (testmodel: mm).
- Openingen: `api.feature.add_feature(feature=opening, element=wand)` (niet meer `void.add_opening`).
- Validatie: `ifcopenshell.validate.validate(f, ifcopenshell.validate.json_logger())`.

## Commando's

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r pyproject.toml --extra test
.venv/bin/python -m pytest                       # alle tests
.venv/bin/python tools/maak_testmodel.py          # testmodel IFC4 + IFC2x3 opnieuw genereren
.venv/bin/python tools/genereer_excel_mapping.py  # excel_mapping.yaml opnieuw genereren uit het template
```

`tools/genereer_excel_mapping.py` is een eenmalig hulpmiddel. Daarna is `config/excel_mapping.yaml`
leidend en wordt hij met de hand bijgehouden; opnieuw genereren overschrijft handmatige wijzigingen
(het script weigert zonder `--overschrijf`).

## Mappenstructuur

```
backend/app/
  datamodel.py              Element, Calculatieregel, Koppeling, Meetinstellingen (pydantic)
  excel/calculatieregels.py leest calculatieregels uit de Excel via config/excel_mapping.yaml
config/
  excel_mapping.yaml        opbouw van de uittrekstaat (tabbladen, rijen, kolommen, cellen)
  stabu_koppeling.xlsx      (fase 2) koppeltabel, beheer Bastiaan
docs/
  stappenplan.md            het volledige stappenplan
  testmodel_handberekening.md  handberekening van het testmodel voor Bastiaan
  excel_analyse.md          gegenereerd: uitgelezen calculatieregels + controles op het template
frontend/                   (fase 1) Vite + That Open Engine
referentie/                 ALLEEN-LEZEN: template, stappenplan-PDF, later project-IFC's
tests/
  verwacht.json             verwachte waarden testmodel + verwacht aantal calculatieregels
  testmodel/                gegenereerde testmodellen (IFC4 + IFC2x3)
tools/
  maak_testmodel.py         genereert het testmodel met IfcOpenShell
  genereer_excel_mapping.py eenmalige scan van het template → excel_mapping.yaml
```

## Datamodel (backend/app/datamodel.py)

- **Element**: `global_id`, `ifc_klasse`, `naam`, `type_naam`, `materiaal`, `verdieping`.
  Leeg materiaal/verdieping = `None` (komt in het importrapport, fase 1).
- **Calculatieregel**: één blok in de uittrekstaat (titel + kopregel + invoerrijen + totaal).
  `id` = `<hoofdstuk>.<volgnummer>` (bijv. `21.05`), want titels zijn niet uniek.
  Velden: `hoofdstuk`, `tabblad`, `titel`, `omschrijving`, `hoeveelheden` (lijst van
  `Hoeveelheidskolom`: naam, kolom, eenheid, totaalcel, verliescel/-percentage),
  `invoerkolommen` (kolom → kopnaam, bijv. `C: lengte`, `M: Wap.`), `invoerrijen`, `waarschuwingen`.
  De eerste hoeveelheidskolom is de hoofdhoeveelheid; overige zijn afgeleid (bijv. beton m3, wapening kg).
- **Koppeling** (veel-op-veel element ↔ calculatieregel): `global_id`, `calculatieregel_id`,
  `hoeveelheidskolom` (welke uitkomst van de regel; `None` = hoofdhoeveelheid), `meetwijze`
  (naam van de rekenregel-functie), `meegenomen` (aan/uit), `reden_uitgesloten`, `bron`
  (automatisch/handmatig). Unieke sleutel: (global_id, calculatieregel_id, hoeveelheidskolom).
- **Meetinstellingen**: `bruto_netto`, `sparing_drempel_m2`, `zijden`, `dagkanten_meenemen`,
  `kengetallen`, `afronding_decimalen`, `opslag_procent` (standaard 0). Bouwkundige standaarden
  zijn nog **niet vastgesteld** (`None`) – Bastiaan bepaalt ze in fase 4 (profiel "BMN standaard").
  Instellingen per calculatieregel overschrijven de globale.
- **Project**: bundelt elementen, calculatieregels, koppelingen en instellingen; hulpfuncties
  `koppelingen_van_element`, `elementen_van_regel`.

## Testmodel (tools/maak_testmodel.py → tests/testmodel/)

Eén verdieping "00 Begane grond", lengte-eenheid mm, vaste GlobalIds (in `tests/verwacht.json`).
Betonvloer 10×8×0,25 m (bovenkant = peil 0), betonwand 10×3×0,30 m óp de vloer langs de rand,
raamsparing 1,00×1,50 m in de wand (borstwering 0,90 m), betonkolom 0,40×0,40×3,00 m vrij op de vloer,
kalkzandsteenwand 5,00×2,70×0,10 m vrij op de vloer. Geen overlap tussen elementen.
Elk bouwelement: materiaal (IfcMaterial), type, verdieping en base quantities.

## Beslissingen

- Calculatie-Excel = uittrekstaat-template (`referentie/uittrekstaat_template.xlsx`) zolang er geen
  aparte calculatie-Excel nodig is (Jordi, 26-11-2026).
- Opslag SQLite per project (Jordi, 26-11-2026).
- Tabbladen zonder hoeveelheidskolommen (§10 en §16 sloop-prijslijsten, §47, Installaties) leveren
  geen calculatieregels op – voorlopig, ter bevestiging door Bastiaan.
- Hoofdhoeveelheid van een regel = eerste uitkomstkolom met formule in de totaalregel; opgetelde
  invoerkolommen (bijv. 'aantal' bij kozijnen §30) komen als afgeleide hoeveelheid achteraan.
- Template-check fase 0: geen macro's, afbeeldingen, grafieken of voorwaardelijke opmaak. openpyxl
  verliest bij opslaan wel de binaire printerinstellingen (`xl/printerSettings/*.bin`) – meenemen in fase 5.

## Open vragen voor Bastiaan

1. Is één blok = één calculatieregel juist, met beton/wapening als afgeleide hoeveelheden van dat blok?
2. In welke calculatieregel(s) hoort "betonmortel" (testmodel 29,03 m³)? Er is geen apart blok
   "Betonmortel"; beton m³ staat als extra kolom bij o.a. PS-fundering, bekisting, i.h.w.g.-vloer,
   kelderwanden. Betonnen kolommen (§23) alleen in stuks.
3. Template-controles uit `docs/excel_analyse.md` (formules die afwijken binnen een blok,
   totaalbereik, eenheden) – fout in template of bewust?
4. Testmodel-opbouw (één verdieping, geen overlap, sparing zonder kozijn) akkoord?
5. Standaard meetinstellingen (bruto/netto, sparingsdrempel, zijden, dagkanten, afronding) – fase 4.
6. Regel 21.08 "wapening/beton" (§21 rij 109–117) heeft geen eigen titel; hoort bij
   "Aanbrengen i.h.w.g betonvloer" (21.07)? Eigen calculatieregel of onderdeel van 21.07?
7. Totaal van 233 calculatieregels – klopt dat met wat Bastiaan verwacht?
