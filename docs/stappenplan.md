# Stappenplan IFC-hoeveelhedentool met Claude Code

*Jordi Aantjes · 26 nov 2026 — Markdown-versie van `referentie/Stappenplan_IFC-hoeveelhedentool_met_Claude_Code.pdf` (bij verschil is de PDF leidend).*

## Doel en werkwijze

We bouwen een lokale webtool die een IFC-model inleest, de elementen aan STABU koppelt en een ingevulde uittrekstaat plus een ingekleurd IFC-model teruggeeft. De bouw gaat in 6 fases: fase 0 (opzet) en daarna de 5 functionele stappen. Elke fase eindigt met groene tests én een controlemoment door Bastiaan; zonder akkoord begin je niet aan de volgende fase.

| Wie | Rol | Levert |
|---|---|---|
| Bastiaan (werkvoorbereider/calculator) | Opdrachtgever, bouwkundige kennis | Testmodellen, calculatie-Excel, uittrekstaat-template, STABU-koppeltabel, akkoord per fase |
| Jordi Aantjes (ICT) | Bouwer, stuurt Claude Code aan | Werkende code, tests, korte demo per fase |
| Claude Code | Schrijft code en tests | Voorstellen, code, testresultaten |

Vaste werkwijze per fase:

1. Start een nieuwe sessie in Claude Code en laat eerst een plan maken (plan mode). Keur het plan pas goed als het past bij deze guide.
2. Laat Claude Code eerst de tests schrijven, met uitkomsten die je vooraf kent (zie het testmodel in fase 0).
3. Laat bouwen tot alle tests groen zijn. Lees mee; vraag uitleg als je iets niet snapt.
4. Plan een demo van 15–30 minuten met Bastiaan: dat is het controlemoment.
5. Akkoord? Commit en tag in git (bijv. `fase-1-akkoord`). Niet akkoord? Bevindingen als issue vastleggen en eerst oplossen.

Norm voor akkoord: op het testmodel wijkt elke hoeveelheid maximaal 1% af van de handberekening. Op een echt project bepaalt Bastiaan per post of de afwijking acceptabel is.

## Voorbereiding

De tool is zo goed als het referentiemateriaal. Zonder de bestanden hieronder gaat Claude Code gokken naar de opbouw van onze Excel, en dat kost later meer tijd dan nu.

**Aanleveren door Bastiaan** (in de map `referentie/` van het project):

- [ ] Klein testmodel met bekende maten + handberekening (Jordi kan dit ook laten genereren, zie fase 0)
- [ ] 1–2 echte project-IFC's, liefst één IFC2x3 en één IFC4, geëxporteerd mét base quantities
- [ ] Calculatie-Excel: leeg sjabloon + één ingevuld voorbeeld, met uitleg welke kolom code, omschrijving, eenheid en hoeveelheid is
- [ ] Uittrekstaat-template (leeg) + dezelfde uittrekstaat met de hand ingevuld voor een echt project: dit is de referentie voor fase 5
- [ ] Eerste STABU-koppeltabel: IFC-klasse + materiaal/typenaam → STABU-code → calculatieregel → eenheid (m1, m2, m3, st, kg)
- [ ] Meetregels op papier, bijv. sparingen kleiner dan X m² niet aftrekken, schilderwerk één of twee zijden, afronding op 2 decimalen

**Techniekkeuze** (advies; afwijken mag, maar dan met reden):

| Onderdeel | Keuze | Waarom |
|---|---|---|
| Backend | Python 3.12 + FastAPI | IfcOpenShell is de standaard om IFC te lezen, te rekenen en te schrijven |
| IFC-verwerking | IfcOpenShell 0.8.x | Volumes, oppervlaktes, property sets en kleuren wegschrijven |
| Excel | openpyxl | Calculatie lezen, template vullen |
| Frontend | TypeScript + Vite + That Open Engine | 3D-viewer, selecteren, inkleuren, meetgereedschap voor lengte, oppervlak en volume |
| Opslag | SQLite of JSON per project | Koppelingen en instellingen bewaren |
| Tests | pytest (backend), Playwright (frontend) | Elke fase automatisch controleren |

Alles draait lokaal op de pc: geen projectdata naar externe servers.

**Claude Code inrichten:**

1. Installeer Claude Code en log in met het bedrijfsaccount.
2. Maak een lege map `ifc-hoeveelheden`, zet er `git init` op en kopieer de referentiebestanden naar `referentie/`.
3. Start Claude Code in die map en plak de startprompt onderaan deze guide.
4. Claude Code maakt een `CLAUDE.md` met de projectafspraken. Lees die na; daar leest Claude Code elke sessie opnieuw uit.

## Fase 0 – Projectopzet en testset

Na fase 0 staat het skelet van de applicatie, ligt het datamodel vast en is er een testmodel waarvan we elke hoeveelheid vooraf kennen. Er is nog niets zichtbaar voor de gebruiker.

Architectuur: al het rekenwerk zit in de backend; Excel-opbouw staat in config.

```
Invoer (referentie/)        Backend (Python)                       Uitvoer
IFC-model           ──►     IFC inlezen en meten (IfcOpenShell) ──► uittrekstaat.xlsx
Calculatie-Excel            STABU-koppeling en rekenregels          naam_BMN_calc.ifc
Uittrekstaat-template       export Excel (openpyxl) en IFC
                            opslag per project (SQLite/JSON)
                                 ▲ API              ▲ leest
                     Frontend (browser)       Config (beheer Bastiaan)
                     3D-viewer, modelboom,    excel_mapping.yaml
                     meten, overzicht,        stabu_koppeling.xlsx
                     kleuren, instellingen
```

De browser toont en meet; alle berekeningen en exports lopen via de backend, die de Excel-opbouw en koppelregels uit config leest.

**Bouwen**

- Mappen: `backend/`, `frontend/`, `config/`, `referentie/`, `tests/`.
- Datamodel met vier onderdelen: Element (GlobalId, IFC-klasse, naam, type, materiaal, verdieping), Calculatieregel (uit onze Excel), Koppeling (element ↔ calculatieregel + meetwijze + aan/uit) en Meetinstellingen.
- **Belangrijk voor ICT:** één element hangt vaak aan meerdere calculatieregels. Een betonwand levert betonmortel (m³), bekisting (m²), wapening (kg) en schilderwerk (m²). De koppeling is dus veel-op-veel.
- De opbouw van de Excel (sheetnaam, startrij, kolommen) komt in `config/excel_mapping.yaml`, niet in de code. Verandert de Excel, dan pas je alleen de config aan.
- Een script dat met IfcOpenShell het testmodel hieronder genereert, plus `tests/verwacht.json` met de uitkomsten.

**Testmodel**

| Element | Maten | Verwacht |
|---|---|---|
| Betonwand | 10,00 × 3,00 m, dik 0,30 m | Bruto 9,00 m³; zijvlak 30,00 m² per zijde |
| Raamsparing in die wand | 1,00 × 1,50 m | Wand netto 8,55 m³; zijvlak netto 28,50 m² per zijde |
| Betonvloer | 10,00 × 8,00 m, dik 0,25 m | 20,00 m³; bovenvlak 80,00 m² |
| Betonkolom | 0,40 × 0,40 m, hoog 3,00 m | 0,48 m³ |
| Kalkzandsteenwand | 5,00 × 2,70 m, dik 0,10 m | 1,35 m³; zijvlak 13,50 m² per zijde |

**Testen**

- `pytest` draait (mag nog leeg zijn op één rooktest na).
- Het testmodel opent zonder fouten in IfcOpenShell en bevat 4 bouwelementen plus 1 sparing, elk bouwelement met materiaal en verdieping.
- De Excel-config leest de calculatieregels uit het voorbeeld en het aantal regels klopt.

**Controlemoment 0 – Bastiaan (±30 min)**

- Reken de tabel hierboven na en vul aan met posten die voor ons vaak fout gaan.
- Check of de uitgelezen calculatieregels (code, omschrijving, eenheid) overeenkomen met de Excel.
- Bevestig dat het veel-op-veel-principe klopt met hoe wij calculeren.

## Fase 1 – IFC importeren, bekijken en meten

Na fase 1 kun je een IFC-bestand openen, door het model draaien, elementen aanklikken en per element m² en m³ zien. Dit is de basis: klopt het inlezen niet, dan klopt niets daarna.

**Bouwen**

- IFC openen via slepen of knop; backend leest met IfcOpenShell, frontend toont met That Open Engine.
- Modelboom per verdieping en per IFC-klasse, met zoekveld.
- Klik op element: oplichten + eigenschappenpaneel (klasse, naam, type, materiaal, verdieping, alle property sets).
- Per element automatisch berekend: volume bruto en netto, zijvlak, bovenvlak, totaal oppervlak, lengte, hoogte, dikte.
- Meten als **2D-vlak**: klik een vlak van een element of teken een polygoon → m² (bijv. schilderwerk).
- Meten als **3D-blok**: selecteer één of meer elementen → opgeteld m³ (bijv. betonmortel). Plus een lengtemaat.
- Vergelijking: eigen berekening naast de hoeveelheden die al in het IFC staan (base quantities), met afwijking in %.
- Importrapport: aantal elementen per klasse, en lijstjes van elementen zonder geometrie, materiaal of verdieping.

**Testen (automatisch)**

- Alle waarden van het testmodel binnen 1% van `verwacht.json`, bruto én netto.
- Een IFC2x3- en een IFC4-bestand laden allebei zonder fouten.
- Browsertest: model laden, betonwand aanklikken, paneel toont 9,00 m³ bruto en 8,55 m³ netto.
- Laadtijd van het echte projectmodel noteren (richtwaarde: onder 1 minuut).

**Controlemoment 1 – Bastiaan (±1 uur, belangrijkste check)**

- Testmodel: klik alle 4 elementen aan en vergelijk met de tabel uit fase 0.
- Echt project dat je kent: meet 5 elementen na (wand, vloer, kolom, kozijn, dak) en vergelijk met tekening of eerdere uittrekstaat.
- Worden sparingen en kozijnopeningen netjes afgetrokken bij netto?
- Importrapport: zijn alle verdiepingen er, en herken je wat ontbreekt als modelfout in plaats van toolfout?
- Akkoord als: testmodel binnen 1%, steekproef plausibel, geen hoofdgroepen kwijt.

## Fase 2 – Elementen koppelen aan STABU

Na fase 2 heeft elk element één of meer koppelingen naar een STABU-code en calculatieregel, automatisch voorgesteld en handmatig te corrigeren. De regels staan in een koppeltabel die Bastiaan zelf beheert, niet in de code.

**Bouwen**

- Koppeltabel `config/stabu_koppeling.xlsx`: als IFC-klasse + materiaal (of typenaam) = X, dan STABU-code Y met calculatieregels en meetwijze.
- Automatisch voorstel op basis van de koppeltabel. Staat er een NL-SfB-code in het model (verplicht volgens de BIM basis ILS), dan mag die als extra sleutel dienen.
- Status per element: automatisch, handmatig of niet gekoppeld. Filter op "niet gekoppeld".
- Handmatig koppelen: selecteer elementen in 3D of lijst, of alle elementen van één type, en kies de code. Handmatig wint altijd van automatisch.
- Koppelingen bewaren per project en bij een nieuwe modelversie terugvinden via de GlobalId.

**Voorbeeld koppeltabel** (Bastiaan vult de echte regels in)

| IFC-klasse | Materiaal bevat | STABU | Calculatieregels | Meetwijze |
|---|---|---|---|---|
| IfcWall | beton | 21 Betonwerk | Betonmortel, bekisting, wapening | m³ netto; m² zijvlak 2 zijden; kg via kg/m³ |
| IfcWall | kalkzandsteen | 22 Metselwerk | Lijmwerk kalkzandsteen | m² zijvlak 1 zijde netto |
| IfcSlab, IfcColumn | beton | 21 Betonwerk | Betonmortel | m³ netto |
| IfcWall | (afwerking) | 46 Schilderwerk | Muurverf | m² zijvlak netto |

**Testen (automatisch)**

- Testmodel: 4 van 4 elementen automatisch gekoppeld; de betonwand heeft minimaal 3 koppelingen.
- Handmatige koppeling overschrijft de automatische en blijft bewaard na herstart.
- Model opnieuw inladen: alle koppelingen blijven staan.
- Element zonder materiaal krijgt "niet gekoppeld" en valt niet stilletjes ergens onder.

**Controlemoment 2 – Bastiaan (±1 uur, eventueel in rondes)**

- Echt project: welk deel is automatisch gekoppeld? Loop de lijst "niet gekoppeld" door.
- Steekproef van 10 elementen: juiste STABU-code en juiste calculatieregels?
- Vul de koppeltabel aan en laat opnieuw draaien tot de dekking goed is (richtwaarde: 90% automatisch).
- Is handmatig koppelen werkbaar voor een calculator, of kost het te veel klikken?

## Fase 3 – Hoeveelheden berekenen en ingekleurd controleren

Na fase 3 rekent de tool per calculatieregel de totale hoeveelheid uit in de eenheid van onze Excel, en kleurt het 3D-model zodat je in één oogopslag ziet wat meetelt en wat vergeten is.

**Bouwen**

- Per koppeling de hoeveelheid berekenen volgens de meetwijze, in de eenheid van de calculatieregel (m1, m2, m3, st, kg).
- Elke rekenregel is een losse functie met een herkenbare naam, bijv. `zijvlak_netto_2_zijden`. Zo kan Bastiaan per regel zien wat er gebeurt.
- Afgeleide hoeveelheden via kengetallen uit de Excel, bijv. wapening in kg/m³.
- Overzicht: STABU-code → calculatieregel → totaal + eenheid + aantal elementen; uitklapbaar naar elementniveau.
- Klik op een regel: die elementen lichten op in 3D, de rest wordt transparant.
- Inkleuren per STABU-hoofdstuk met legenda. Niet gekoppeld = **rood**, uitgevinkt = grijs. Weergave te kiezen per hoofdstuk of per calculatieregel, omdat één element in meerdere regels kan zitten.

**Testen (automatisch)**

- Betonmortel netto testmodel (wand + vloer + kolom) = 8,55 + 20,00 + 0,48 = **29,03 m³**.
- Bekisting betonwand 2 zijden netto = **57,00 m²** (zonder dagkanten van de sparing).
- Lijmwerk kalkzandsteen = **13,50 m²**.
- Unittest per rekenregel; som van alle elementen = totaal in het overzicht (geen dubbeltellingen).
- Aantal rode elementen = aantal niet-gekoppelde elementen.

**Controlemoment 3 – Bastiaan (±2 uur, de calculatiecheck)**

- Testmodel: kloppen de totalen hierboven? Moeten dagkanten van sparingen bij bekisting en schilderwerk mee?
- Echt project: leg de totalen per calculatieregel naast de handmatige uittrekstaat. Bespreek elke afwijking boven 3%: modelfout, koppelfout of rekenregel?
- Kijk naar overlap bij aansluitingen, zoals een wand die door de vloer loopt: wordt beton dubbel geteld?
- Draai het kleurenmodel rond: is rood echt vergeten en is grijs terecht uitgezet?

## Fase 4 – Meetinstellingen en aan/uitvinken

Na fase 4 kan de calculator de meetregels zelf fijnstellen en onderdelen uitsluiten, en ziet hij het effect direct in het overzicht en in de kleuren.

**Bouwen**

- Instellingenpaneel, globaal en per calculatieregel te overschrijven:
  - Bruto of netto
  - Sparingen kleiner dan X m² niet aftrekken (drempel instelbaar)
  - Zijvlakken: 1 of 2 zijden; dagkanten wel of niet meenemen
  - Kengetallen, bijv. wapening in kg/m³
  - Afronding (aantal decimalen) en optioneel een opslag per regel (standaard 0%)
- Aan/uitvinken op elk niveau: element, type, IFC-klasse, verdieping, STABU-hoofdstuk, calculatieregel. Ook vanuit 3D: selecteren en uitsluiten.
- Bij uitvinken optioneel een reden invullen; lijst van uitgesloten onderdelen blijft zichtbaar.
- Elke wijziging werkt direct door in overzicht en kleuren.
- Instellingen bewaren per project en als herbruikbaar profiel ("BMN standaard").

**Testen (automatisch)**

- Sparingsdrempel op 2,00 m²: sparing van 1,50 m² telt niet → betonwand weer 9,00 m³ en 30,00 m² per zijde.
- Betonwand uitvinken → betonmortel 29,03 − 8,55 = **20,48 m³**, wand grijs in 3D.
- Bekisting op 1 zijde → 28,50 m².
- Instellingen staan er na herstart nog; profiel laadt in een nieuw project.

**Controlemoment 4 – Bastiaan (±1 uur)**

- Zet onze standaard meetregels in de tool en bewaar ze als profiel.
- Speel met drempel, zijden en uitvinken: reageren de totalen zoals je verwacht?
- Mis je instellingen, of zijn er overbodige?
- Herhaal de vergelijking met de handmatige uittrekstaat: vallen de afwijkingen uit fase 3 nu binnen de norm?

## Fase 5 – Exporteren: uittrekstaat en ingekleurd IFC

Na fase 5 levert de tool twee bestanden: een ingevulde uittrekstaat in ons eigen template en een nieuw IFC-model met kleuren en een calculatiereferentie per element. Het originele IFC en het template blijven altijd onaangeroerd.

**Bouwen – uittrekstaat**

- Kopie van het template vullen via `config/excel_mapping.yaml`: per calculatieregel hoeveelheid en eenheid in de juiste cel.
- Alleen invoercellen vullen; formules, opmaak en tabbladen blijven staan. Excel rekent de formules zelf na openen.
- Extra tabblad "Specificatie": per element GlobalId, naam, STABU-code, calculatieregel, hoeveelheid en gebruikte meetinstelling.
- Bestandsnaam: `<projectnr>_uittrekstaat_<datum>.xlsx`.

**Bouwen – ingekleurd IFC**

- Nieuw bestand `<naam>_BMN_calc.ifc`; GlobalIds blijven gelijk aan het origineel.
- Kleuren gelijk aan de 3D-weergave (per STABU-hoofdstuk, rood = niet gekoppeld).
- Per element een property set `BMN_Calculatie` met: `CalculatieRef` (verwijzing naar de regel in onze calculatie-Excel), `STABUCode`, `Hoeveelheid`, `Eenheid`, `Meetwijze`, `Meegenomen`. Bij meerdere koppelingen alle referenties, gescheiden door een puntkomma. Stem het formaat van de referentie af met Bastiaan.
- **Let op voor ICT:** elementen die hun geometrie via een type delen, krijgen allemaal dezelfde kleur als je de typegeometrie kleurt. Kleur per element afhandelen en dit expliciet testen.

**Testen (automatisch)**

- Uittrekstaat testmodel: 29,03 m³ betonmortel staat in de juiste cel; aantal formules vóór en na export is gelijk.
- Export-IFC opent zonder fouten en doorstaat de schemavalidatie van IfcOpenShell.
- 4 van 4 elementen hebben `BMN_Calculatie`; GlobalIds gelijk aan het origineel; kleur in export = kleur in viewer.
- Roundtrip: export opnieuw inladen geeft dezelfde totalen.

**Controlemoment 5 – Bastiaan (±2 uur, eindcheck)**

- Open de uittrekstaat in Excel: juiste cellen, werkende formules, opmaak zoals ons template?
- Leg hem naast de handmatige uittrekstaat van het referentieproject.
- Open het ingekleurde IFC in een andere viewer (bijv. BIMcollab Zoom) en klik elementen aan: staat de referentie erin en wijst die naar de juiste Excel-regel?
- Draai daarna één lopend project parallel aan de gewone werkwijze voordat de tool het overneemt.

## Overzicht controlemomenten

Bastiaan controleert zes keer, samen ongeveer 7,5 uur. De zwaarste momenten zijn fase 1 (klopt het inlezen) en fase 3 (kloppen de hoeveelheden).

| Fase | Moment | Bastiaan controleert | Akkoord als | Tijd |
|---|---|---|---|---|
| 0 | Na projectopzet | Handberekening testmodel, uitgelezen calculatieregels, veel-op-veel | Tabel klopt, regels compleet | 30 min |
| 1 | Na import en viewer | 4 elementen testmodel, steekproef echt project | Testmodel binnen 1%, geen hoofdgroepen kwijt | 1 uur |
| 2 | Na STABU-koppeling | Dekking automatisch koppelen, steekproef 10 elementen | Circa 90% automatisch, steekproef goed | 1 uur |
| 3 | Na berekening | Totalen naast handmatige uittrekstaat, dubbeltellingen | Elke afwijking boven 3% verklaard | 2 uur |
| 4 | Na meetinstellingen | Standaardprofiel, effect van instellingen | Afwijkingen binnen de norm | 1 uur |
| 5 | Na export | Uittrekstaat in Excel, IFC in andere viewer | Klaar voor proefproject | 2 uur |

(De actuele status per fase staat in `CLAUDE.md`.)

## Startprompt voor Claude Code

Exporteer deze guide eerst als Markdown en zet hem in het project als `docs/stappenplan.md`. Plak daarna onderstaande prompt in Claude Code. Daarin staan alle fases, zodat Claude Code vanaf het begin weet waar het naartoe gaat. Claude Code bouwt toch steeds maar één fase en stopt dan tot Bastiaan akkoord geeft.

```text
Je gaat samen met mij (Jordi Aantjes, ICT) een lokale webapplicatie bouwen
voor BMN De Klerk, een bouwbedrijf. Opdrachtgever is onze
werkvoorbereider/calculator Bastiaan. Doel: hoeveelheden uittrekken uit IFC-
modellen. Hieronder staan het eindbeeld, de afspraken en alle fases. Lees
alles, maar bouw steeds maar EEN fase tegelijk.


## Eindbeeld van de tool
1. IFC-bestand (IFC2x3 en IFC4) importeren en tonen in een 3D-viewer.
Elementen zijn selecteerbaar en je kunt meten als 2D-vlak (m2, bijv.
schilderwerk) en als 3D-blok (m3, bijv. betonmortel), om te controleren of
alles goed is ingeladen.
2. Elementen koppelen aan STABU-codes en calculatieregels: automatisch via
een koppeltabel, handmatig te corrigeren. Een element kan aan meerdere
calculatieregels hangen (veel-op-veel).
3. Hoeveelheden berekenen op basis van onze calculatie-Excel







(m1/m2/m3/st/kg), met een overzicht en een ingekleurd 3D-model ter controle.
4. Meetinstellingen aanpassen en onderdelen aan/uitvinken om de uitkomst fijn
te stellen.
5. Exporteren: ingevulde uittrekstaat in ons eigen Excel-template, en een
nieuw ingekleurd IFC-bestand waarin elk element een property set
BMN_Calculatie krijgt met de referentie naar onze calculatie-Excel.


## Techniek
- Backend: Python 3.12, FastAPI, IfcOpenShell 0.8.x, openpyxl. Tests met
pytest.
- Frontend: TypeScript, Vite, That Open Engine (@thatopen/components en
@thatopen/components-front). Browsertests met Playwright.
- Opslag: SQLite of JSON per project.
- Alles draait lokaal; geen projectdata naar externe diensten.
- Controleer de actuele API's van IfcOpenShell en That Open Engine in hun
documentatie voordat je code schrijft; ga niet uit van verouderde
voorbeelden.


## Werkafspraken
- HARDE REGEL: bouw alleen de fase die aan de beurt is. Na elke fase stop je
en wacht je tot ik schrijf "Fase X akkoord". Begin nooit uit jezelf aan de
volgende fase.
- Begin elke fase met een plan, inclusief de tests en verwachte uitkomsten,
en wacht op mijn akkoord voordat je code schrijft.
- Schrijf eerst de tests, daarna de code. Een fase is pas klaar als alle
tests groen zijn.
- Sluit elke fase af met: wat gebouwd is, testresultaten, open vragen voor
Bastiaan en een korte demo-instructie zodat Bastiaan het kan controleren.
- Neem het fasenplan op in CLAUDE.md en houd daar per fase de status bij
(open / bezig / akkoord), zodat een nieuwe sessie direct weet waar we zijn.
- Hardcode nooit de opbouw van onze Excel-bestanden: sheetnamen, rijen en
kolommen staan in config/excel_mapping.yaml. Koppelregels staan in
config/stabu_koppeling.xlsx, beheerd door Bastiaan.
- Rekenregels zijn losse functies met een herkenbare Nederlandse naam (bijv.
zijvlak_netto_2_zijden) en uitleg in gewone taal, zodat een bouwkundige ze
kan nalezen.
- Bestanden in referentie/ zijn alleen-lezen. Wijzig nooit het originele IFC
of template; exports zijn altijd nieuwe bestanden.
- Gebruikersinterface in het Nederlands. Vakbegrippen (uittrekstaat,
calculatieregel, meetwijze, STABU) blijven Nederlands, ook in de code.
- Twijfel je over een bouwkundige keuze (dagkanten, overlap bij
aansluitingen, meetwijze)? Vraag het; beslis niet zelf.
- Commit na elke afgeronde deelstap; tag na akkoord (bijv. fase-1-akkoord).

## Testmodel (wordt gemaakt in fase 0, gebruikt in alle fases)
- Betonwand 10,00 x 3,00 m, dik 0,30 m: bruto 9,00 m3; zijvlak 30,00 m2 per








zijde.
- Raamsparing in die wand 1,00 x 1,50 m: wand netto 8,55 m3; zijvlak netto
28,50 m2 per zijde.
- Betonvloer 10,00 x 8,00 m, dik 0,25 m: 20,00 m3; bovenvlak 80,00 m2.
- Betonkolom 0,40 x 0,40 m, hoog 3,00 m: 0,48 m3.
- Kalkzandsteenwand 5,00 x 2,70 m, dik 0,10 m: 1,35 m3; zijvlak 13,50 m2 per
zijde.
Dat zijn 4 bouwelementen plus 1 sparing, elk bouwelement met materiaal en
verdieping.


## Fase 0 – Projectopzet en testset
Bouw:
1. Lees docs/stappenplan.md en de bestanden in referentie/.
2. Maak CLAUDE.md met deze afspraken, het fasenplan, het datamodel en de
mappenstructuur.
3. Projectstructuur: backend/, frontend/, config/, referentie/, tests/.
4. Datamodel: Element (GlobalId, IFC-klasse, naam, type, materiaal,
verdieping), Calculatieregel (uit de Excel), Koppeling (veel-op-veel, met
meetwijze en aan/uit) en Meetinstellingen.
5. Script dat met IfcOpenShell het testmodel hierboven genereert; verwachte
waarden in tests/verwacht.json.
6. Eerste config/excel_mapping.yaml op basis van de calculatie-Excel in
referentie/.
Tests:
- pytest draait.
- Testmodel opent zonder fouten en bevat 4 bouwelementen plus 1 sparing met
materiaal en verdieping.
- De Excel-config leest de calculatieregels uit het voorbeeld en het aantal
regels klopt.

## Fase 1 – IFC importeren, bekijken en meten
Bouw:
1. IFC openen via slepen of een knop. Backend leest met IfcOpenShell,
2. Modelboom per verdieping en per IFC-klasse, met zoekveld.
3. Klik op element: oplichten + paneel met klasse, naam, type, materiaal,
verdieping en alle property sets.
4. Per element berekend: volume bruto en netto, zijvlak, bovenvlak, totaal
oppervlak, lengte, hoogte, dikte.
5. Meten als 2D-vlak (vlak aanklikken of polygoon tekenen, m2) en als 3D-blok
(een of meer elementen selecteren, opgetelde m3). Plus een lengtemaat.
6. Vergelijking eigen berekening met de base quantities uit het IFC, met
afwijking in %.
7. Importrapport: aantal elementen per klasse, en lijsten van elementen
zonder geometrie, materiaal of verdieping.
Tests:








- Alle waarden van het testmodel binnen 1% van tests/verwacht.json, bruto en
netto.
- Een IFC2x3- en een IFC4-bestand laden zonder fouten.
- Playwright: testmodel laden, betonwand aanklikken, paneel toont 9,00 m3
bruto en 8,55 m3 netto.
- Laadtijd van het projectmodel in referentie/ meten en melden (richtwaarde:
onder 1 minuut).

## Fase 2 – Elementen koppelen aan STABU
Bouw:
1. Koppeltabel config/stabu_koppeling.xlsx inlezen: IFC-klasse + materiaal
(of typenaam) geeft STABU-code, een of meer calculatieregels en per regel de
meetwijze.
2. Automatisch koppelvoorstel; een NL-SfB-code in het model mag als extra
sleutel dienen.
3. Status per element: automatisch, handmatig of niet gekoppeld, met filter
op niet gekoppeld.
4. Handmatig koppelen: elementen selecteren in 3D of lijst, of alle elementen
van een type, en code kiezen. Handmatig wint altijd van automatisch.
5. Koppelingen bewaren per project en bij een nieuwe modelversie terugvinden
via de GlobalId.
Tests:
- Testmodel: 4 van 4 bouwelementen automatisch gekoppeld; de betonwand heeft
minimaal 3 koppelingen.
- Handmatige koppeling overschrijft automatisch en blijft na herstart
bewaard.
- Model opnieuw inladen: alle koppelingen blijven staan.
- Element zonder materiaal krijgt de status niet gekoppeld.
- Meld het percentage automatisch gekoppeld op het projectmodel in
referentie/.

## Fase 3 – Hoeveelheden berekenen en ingekleurd controleren
Bouw:
1. Per koppeling de hoeveelheid volgens de meetwijze, in de eenheid van de
calculatieregel.
2. Afgeleide hoeveelheden via kengetallen uit de Excel, bijv. wapening in
kg/m3.
3. Overzicht: STABU-code > calculatieregel > totaal + eenheid + aantal
elementen, uitklapbaar naar elementniveau.
4. Klik op een regel: die elementen lichten op in 3D, de rest wordt
transparant.
5. Inkleuren per STABU-hoofdstuk met legenda; niet gekoppeld = rood,
uitgevinkt = grijs. Weergave per hoofdstuk of per calculatieregel.
6. Export van de totalen per calculatieregel voor het projectmodel, zodat
Bastiaan ze naast de handmatige uittrekstaat kan leggen.
Tests:








- Betonmortel netto testmodel (wand + vloer + kolom) = 29,03 m3.
- Bekisting betonwand 2 zijden netto = 57,00 m2 (zonder dagkanten).
- Lijmwerk kalkzandsteen = 13,50 m2.
- Unittest per rekenregel; som over alle elementen = totaal in het overzicht.
- Aantal rode elementen = aantal niet-gekoppelde elementen.

## Fase 4 – Meetinstellingen en aan/uitvinken
Bouw:
1. Instellingenpaneel, globaal en per calculatieregel: bruto of netto;
sparingen kleiner dan X m2 niet aftrekken; zijvlakken 1 of 2 zijden;
dagkanten wel/niet; kengetallen; afronding; optionele opslag per regel
(standaard 0%).
2. Aan/uitvinken op element, type, IFC-klasse, verdieping, STABU-hoofdstuk en
calculatieregel, ook vanuit 3D.
3. Bij uitvinken optioneel een reden; de lijst van uitgesloten onderdelen
blijft zichtbaar.
4. Elke wijziging werkt direct door in overzicht en kleuren.
5. Instellingen bewaren per project en als profiel "BMN standaard".
Tests:
- Sparingsdrempel 2,00 m2: betonwand weer 9,00 m3 en 30,00 m2 per zijde.
- Betonwand uitvinken: betonmortel 20,48 m3, wand grijs in 3D.
- Bekisting op 1 zijde: 28,50 m2.
- Instellingen blijven na herstart; profiel laadt in een nieuw project.

## Fase 5 – Exporteren: uittrekstaat en ingekleurd IFC
Bouw:
1. Kopie van het uittrekstaat-template vullen via config/excel_mapping.yaml.
Alleen invoercellen; formules, opmaak en tabbladen blijven intact (.xlsm
openen met keep_vba).
2. Extra tabblad Specificatie: per element GlobalId, naam, STABU-code,
calculatieregel, hoeveelheid, meetinstelling.
3. Bestandsnaam: <projectnr>_uittrekstaat_<datum>.xlsx.
4. Nieuw IFC <naam>_BMN_calc.ifc; origineel onaangeroerd, GlobalIds gelijk.
5. Kleuren gelijk aan de 3D-weergave. Let op elementen die geometrie via een
type delen: kleur per element.
6. Property set BMN_Calculatie per element: CalculatieRef, STABUCode,
Hoeveelheid, Eenheid, Meetwijze, Meegenomen. Meerdere koppelingen gescheiden
door een puntkomma. Stel het formaat van CalculatieRef eerst voor ter
goedkeuring.
Tests:
- Uittrekstaat testmodel: 29,03 m3 betonmortel in de juiste cel; aantal
- Export-IFC opent zonder fouten en doorstaat de schemavalidatie van
IfcOpenShell.
- 4 van 4 bouwelementen hebben BMN_Calculatie; GlobalIds gelijk; kleur in
export = kleur in viewer.








- Roundtrip: export opnieuw inladen geeft dezelfde totalen.

## Nu
Bevestig kort dat je het hele plan begrijpt, stel eventuele vragen, en maak
dan het plan voor fase 0. Wacht op mijn akkoord voordat je code schrijft.
```

**Na elk controlemoment** stuurt Jordi alleen dit bericht (in dezelfde sessie, of in een nieuwe sessie na `/clear`):

```text
Fase X akkoord. Bevindingen van Bastiaan: <plak hier, of "geen">. Werk eerst
de bevindingen bij, start daarna fase X+1 met een plan en wacht op mijn
akkoord.
```

## Tips en valkuilen

De grootste risico's zitten niet in de code maar in te grote stappen en in de kwaliteit van de IFC-modellen.

| Valkuil | Gevolg | Aanpak |
|---|---|---|
| Te veel in één keer vragen | Veel ongeteste code die lastig te controleren is | Eén fase per sessie, plan eerst laten goedkeuren |
| Lange sessies | Claude Code vergeet afspraken | Afspraken in `CLAUDE.md`; nieuwe sessie per fase (`/clear`) |
| Fouten in het IFC-model | Modelfouten lijken toolfouten | Altijd eerst het importrapport uit fase 1 bekijken |
| Excel-opbouw verandert | Hoeveelheden in verkeerde cellen | Alleen `excel_mapping.yaml` aanpassen en de exporttest opnieuw draaien |
| Gedeelde typegeometrie | Verkeerde kleuren in het export-IFC | Expliciete test in fase 5 |
| openpyxl | Rekent geen formules; kan afbeeldingen of macro's uit een template verliezen | Template in fase 0 testen; `.xlsm` openen met `keep_vba` |
| Projectdata in AI-sessie | Klantbestanden gaan mee naar Claude Code | Check het AI-beleid van BMN; waar mogelijk eigen of geanonimiseerde modellen |
| Grote modellen | Traag laden en rekenen | Laadtijd meten in fase 1; zo nodig berekende geometrie cachen |
