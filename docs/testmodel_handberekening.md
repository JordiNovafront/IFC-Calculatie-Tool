# Testmodel – handberekening (controlemoment 0)

Bastiaan, graag narekenen en aanvullen met posten die bij ons vaak fout gaan.
Bestanden: `tests/testmodel/testmodel_ifc4.ifc` en `tests/testmodel/testmodel_ifc2x3.ifc`
(te openen in bijv. BIMcollab Zoom). Verwachte waarden staan ook in `tests/verwacht.json`.

## Opbouw

Eén verdieping **00 Begane grond** (peil 0,00). Lengte-eenheid in het model: mm.

| Element | IFC-klasse | Type | Materiaal | Plaats |
|---|---|---|---|---|
| Betonvloer | IfcSlab | Betonvloer 250 | Beton C30/37 | 10,00 × 8,00 m, onderkant −0,25, bovenkant ±0,00 |
| Betonwand | IfcWall | Betonwand 300 | Beton C30/37 | op de vloer langs de voorrand, x 0–10, y 0–0,30 |
| Raamsparing | IfcOpeningElement | – | – | in de betonwand, x 4,50–5,50, borstwering 0,90 m |
| Betonkolom | IfcColumn | Betonkolom 400x400 | Beton C30/37 | vrij op de vloer, hart x 5,00 / y 4,00 |
| Kalkzandsteenwand | IfcWall | Kalkzandsteenwand 100 | Kalkzandsteen | vrij op de vloer, x 2–7, y 6,00–6,10 |

Bewust **geen overlap** tussen elementen (de wand staat óp de vloer, niet erdoorheen), zodat elk
getal los is na te rekenen. Overlap bij aansluitingen testen we apart in fase 3.
De sparing is een lege opening zonder kozijn.

## Berekening

| Post | Berekening | Uitkomst |
|---|---|---|
| Betonwand volume bruto | 10,00 × 3,00 × 0,30 | **9,00 m³** |
| Raamsparing oppervlak | 1,00 × 1,50 | 1,50 m² |
| Raamsparing volume in wand | 1,50 × 0,30 | 0,45 m³ |
| Betonwand volume netto | 9,00 − 0,45 | **8,55 m³** |
| Betonwand zijvlak bruto per zijde | 10,00 × 3,00 | **30,00 m²** |
| Betonwand zijvlak netto per zijde | 30,00 − 1,50 | **28,50 m²** |
| Betonvloer volume | 10,00 × 8,00 × 0,25 | **20,00 m³** |
| Betonvloer bovenvlak | 10,00 × 8,00 | **80,00 m²** |
| Betonkolom volume | 0,40 × 0,40 × 3,00 | **0,48 m³** |
| Kalkzandsteenwand volume | 5,00 × 2,70 × 0,10 | **1,35 m³** |
| Kalkzandsteenwand zijvlak per zijde | 5,00 × 2,70 | **13,50 m²** |

## Totalen voor latere fases

| Fase | Post | Berekening | Uitkomst |
|---|---|---|---|
| 3 | Betonmortel netto (wand + vloer + kolom) | 8,55 + 20,00 + 0,48 | **29,03 m³** |
| 3 | Bekisting betonwand 2 zijden netto, zonder dagkanten | 2 × 28,50 | **57,00 m²** |
| 3 | Lijmwerk kalkzandsteen | 5,00 × 2,70 | **13,50 m²** |
| 4 | Sparingsdrempel 2,00 m² (sparing 1,50 m² telt niet) | 10 × 3 × 0,30 | 9,00 m³ en 30,00 m² per zijde |
| 4 | Betonwand uitgevinkt | 29,03 − 8,55 | **20,48 m³** |
| 4 | Bekisting op 1 zijde | 28,50 | **28,50 m²** |

Ter info, nog niet in de tests (vraag fase 3): dagkanten van de sparing zijn
2 × 1,50 × 0,30 + 2 × 1,00 × 0,30 = 0,90 + 0,60 = **1,50 m²** (zijkanten + boven- en onderkant).

## Base quantities in het model

Elk element heeft base quantities (`Qto_…BaseQuantities` in IFC4, `BaseQuantities` in IFC2x3)
met dezelfde waarden als hierboven. In fase 1 vergelijkt de tool zijn eigen berekening hiermee.
