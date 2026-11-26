# Uitgelezen calculatieregels uit de uittrekstaat

*Gegenereerd door `tools/genereer_excel_mapping.py` uit `uittrekstaat_template.xlsx` via `config/excel_mapping.yaml`. Niet met de hand bewerken.*

**233 calculatieregels** op 28 tabbladen; 4 tabbladen zonder regels; 8 regels met een waarschuwing.

Controle Bastiaan: kloppen code, omschrijving en eenheid met de Excel? Zijn de waarschuwingen fouten in het template of bewust zo?

## Tabbladen zonder calculatieregels

| Tabblad | Reden |
|---|---|
| §10 | alleen prijskolommen, geen hoeveelheden |
| §16 | alleen prijskolommen, geen hoeveelheden |
| §47 | geen formules in de totaalregel |
| Installaties | geen formules in de totaalregel |

## Waarschuwingen

| Regel | Titel | Waarschuwing |
|---|---|---|
| 21.05 | Traditionele bekisting | Kolom J: formules verschillen binnen het blok: J60 '=I60*G60*D60' / J61:J74 '=G61*E61*D61'. |
| 21.05 | Traditionele bekisting | Invoerkolom P ('Wap.') wordt in geen enkele formule gebruikt. |
| 21.08 | wapening/beton | Geen titel boven de kopregel (rij 109); titel genomen uit A110. |
| 21.18 | Kelderwanden van beton | Totaalregel H217 noemt eenheid 'm1', invoerrijen 'm2'. |
| 21.18 | Kelderwanden van beton | Totaalformule G217 telt G203:G216, maar de invoerrijen van dit blok zijn G212:G215. |
| 22.29 | Steigerwerk | Kolom G: gemengde eenheden in de invoerrijen (m1, m2); totaal G304 telt ze op. |
| 22.29 | Steigerwerk | Kolom G: formules verschillen binnen het blok: G293:G296 '=F293*D293*C293' / G298:G301 '=F298*C298'. |
| 30.02 | Aluminium kozijnen | Kolom F ('aantal'): totaal F18 telt de invoer op; eenheid ontbreekt in het template. |
| 30.04 | Houten buitenkozijnen | Kolom F ('aantal'): totaal F38 telt de invoer op; eenheid ontbreekt in het template. |
| 30.07 | Houten binnenkozijnen | Kolom F ('aantal'): totaal F68 telt de invoer op; eenheid ontbreekt in het template. |
| 37.01 | Na-isolatie | Kolom G: eenheid ontbreekt in het template. |

## Alle calculatieregels

| Code | Tabblad | Titel | Omschrijving | Eenheid | Afgeleid | Totaalcel |
|---|---|---|---|---|---|---|
| 12.01 | §12 | Ontgraven | Ontgraven grond t.b.v. fundering en vloer | m3 | | G8 |
| 14.01 | §14 | Buitenriolering | Aanbrengen buitenriolering | m1 | | G9 |
| 15.01 | §15 | Brekerpuin | Aanbrengen brekerpuin onder bestrating | m3 | | G8 |
| 15.02 | §15 | Zand onder brekerpuin | Aanbrengen zand onder brekerpuin (300mm) | m2 | | G18 |
| 15.03 | §15 | Bestratingszand onder straatwerk | Aanbrengen zand onder brekerpuin (50mm) | m2 | | G28 |
| 15.04 | §15 | Doek onder straatzand | Aanbrengen doek onder straatzand | m2 | | G38 |
| 15.05 | §15 | Aanbrengen bestrating | Aanbrengen bestrating | m2 | | G48 |
| 15.06 | §15 | Herstellen bestrating | Herstellen bestrating | m2 | | G58 |
| 15.07 | §15 | Stelconplaten t.p.v. overheaddeuren | Aanbrengen stelconplaten t.b.v. overheaddeuren | st | | G73 |
| 17.01 | §17 | Spijlenhekwerk | Aanbrengen spijlenhekwerk | m1 | | G8 |
| 17.02 | §17 | Gaashekwerk | Aanbrengen gaashekwerk | m1 | | G18 |
| 20.01 | §20 | Betonpalen | Aanbrengen betonpalen | st | tot. (m1) | G8 |
| 20.02 | §20 | Stalen buispalen | Aanbrengen stalen buispalen | st | tot. (m1) | G18 |
| 20.03 | §20 | Vibro-palen | Aanbrengen vibro-palen | st | | G28 |
| 20.04 | §20 | Betonschroefpalen | Aanbrengen betonschroefpalen | st | | G38 |
| 21.01 | §21 | Werkvloer van beton | Aanbrengen werkvloer van beton | m2 | | G8 |
| 21.02 | §21 | Aanbrengen werkvloer van noppenfolie | Aanbrengen werkvloer van noppenfolie | m2 | | G18 |
| 21.03 | §21 | Vloerisolatie | Aanbrengen vloerisolatie | m2 | | G32 |
| 21.04 | §21 | PS-fundering | Aanbrengen PS-fundering | m1 | beton (m3), tot. Wap. (kg) | G55 |
| 21.05 | §21 | Traditionele bekisting | Aanbrengen traditionele bekisting | m1 | tot. M2 (m2), beton (m3), tot. Wap. (kg) | G78 |
| 21.06 | §21 | Aanbrengen opstorting | Aanbrengen opstorting 1 | m2 | beton (m3), tot. Wap. (kg) | G95 |
| 21.07 | §21 | Aanbrengen i.h.w.g betonvloer | Aanbrengen randkist t.b.v. betonvloer | m1 | | G107 |
| 21.08 | §21 | wapening/beton | wapening/beton | m2 | beton (m3), tot. Wap. (kg) | G117 |
| 21.09 | §21 | Paalkopverzwaringen | Aanbrengen paalkopverzwaringen | st | | G127 |
| 21.10 | §21 | Monolytische betonvloer | Aanbrengen monolytische betonvloer | m2 | | G137 |
| 21.11 | §21 | Staalvezelbetonvloer | Aanbrengen staalvezelbetonvloer | m2 | | G147 |
| 21.12 | §21 | Dilataties in betonvloer | Aanbrengen dilataties in betonvloer | m1 | | G157 |
| 21.13 | §21 | Ontkisten beton | Ontkisten beton | m2 | | G167 |
| 21.14 | §21 | Aanbrengen doorvoeringen | Aanbrengen paalkopverzwaringen | st | | G177 |
| 21.15 | §21 | Stekankers t.b.v. kolommen | Aanbrengen stekankers | st | | G187 |
| 21.16 | §21 | EPS-isolatie tegen wanden onder MV | Aanbrengen EPS tegen wanden onder MV | m2 | | G197 |
| 21.17 | §21 | Aanbrengen stalen strip t.p.v. aansl. Wand op vloer | Aanbrengen stalen strip | m1 | | G207 |
| 21.18 | §21 | Kelderwanden van beton | Kelderwanden | m2 | beton (m3), tot. Wap. (kg) | G217 |
| 21.19 | §21 | Afwerken konusgaten | Afwerken konusgaten | m2 | | G227 |
| 21.20 | §21 | Balkwapening | Bijlegwapening | kg | | G248 |
| 21.21 | §21 | Vloerwapening netten | Wapeningsnetten | kg | | H269 |
| 21.22 | §21 | Bijlegwapening vloer | Bijlegwapening | kg | | G290 |
| 22.01 | §22 | Aanbrengen gevelmetselwerk | Aanbrengen werkvloer van beton | m2 | | G10 |
| 22.02 | §22 | Opmetselen fundering dik … | Opmetselen fundering | m2 | | G22 |
| 22.03 | §22 | Kalkzandsteen lijmblokken dik … | Aanbrengen kalkzandsteen lijmblokken | m2 | | G34 |
| 22.04 | §22 | Kalkzandsteen lijmelementen dik … | Aanbrengen kalkzandsteen lijmelementen | m2 | | G46 |
| 22.05 | §22 | Kalkzandsteen vellingblokken dik … | Aanbrengen kalkzandsteen vellingblokken | m2 | | G58 |
| 22.06 | §22 | Gibo binnenwanden | Aanbrengen kalkzandsteen vellingblokken | m2 | | G68 |
| 22.07 | §22 | MBI wanden | Aanbrengen MBI wanden | m2 | | G78 |
| 22.08 | §22 | Poriso binnenwanden | Aanbrengen poriso | m2 | | G88 |
| 22.09 | §22 | Ytong binnenwanden | Aanbrengen ytong | m2 | | G98 |
| 22.10 | §22 | Snelbouwbaksteen | Aanbrengen snelbouwbaksteen | m2 | | G108 |
| 22.11 | §22 | Gemetselde schoorsteen | Aanbrengen gemetselde schoorsteen | m2 | | G118 |
| 22.12 | §22 | Raamdorpelstenen | Aanbrengen raamdorpelstenen | m1 | | G128 |
| 22.13 | §22 | Glazen bouwstenen | Aanbrengen glazen bouwstenen | m2 | | G138 |
| 22.14 | §22 | Cellenbeton koudebrugonderbreking | Aanbrengen cellenbeton koudebrugonderbreking | m1 | | G148 |
| 22.15 | §22 | Dilatatievoegen | Aanbrengen dilatatievoegen | m1 | | G158 |
| 22.16 | §22 | Murfor boven kozijnen | Aanbrengen murfor | m1 | | G168 |
| 22.17 | §22 | Metselwerkondersteuning (halfen) | Aanbrengen metselwerkondersteuning | m1 | | G178 |
| 22.18 | §22 | Stalen lateien | Aanbrengen stalen lateien | m1 | | G188 |
| 22.19 | §22 | Harde isolatie op fundering | Aanbrengen harde isolatie op fundering | m2 | | G198 |
| 22.20 | §22 | DPC folie op fundering | Aanbrengen DPC-folie op fundering | m1 | | G208 |
| 22.21 | §22 | Kunststof slabbe boven kozijnen | Aanbrengen kunststof slabbe | m1 | | G218 |
| 22.22 | §22 | Vloerventilatierooster | Aanbrengen vloerventilatieroosters | st | | G228 |
| 22.23 | §22 | Loden loketten | Aanbrengen loden loketten | st | | G238 |
| 22.24 | §22 | Loden vochtkeringsstrook | Aanbrengen vochtkeringsstrook | m1 | | G248 |
| 22.25 | §22 | Afkwastlaag op metselwerk | Aanbrengen afkwastlaag | m2 | | G258 |
| 22.26 | §22 | Toeslag rond metselwerk/lijmwerk | Toeslag rond metselwerk/lijmwerk | m2 | | G268 |
| 22.27 | §22 | Toeslag 2-zijdig schoonwerk | Toeslag 2-zijdig schoonwerk | m2 | | G278 |
| 22.28 | §22 | Rollagen | Aanbrengen rollagen | m1 | | G288 |
| 22.29 | §22 | Steigerwerk | Steiger | ? | | G304 |
| 23.01 | §23 | PS-isolatievloer | Aanbrengen PS-isolatievloer | m2 | | G8 |
| 23.02 | §23 | Geïsoleerde kanaalplaatvloer | Aanbrengen geïsoleerde kanaalplaatvloer | m2 | | G18 |
| 23.03 | §23 | Kanaalplaatvloer | Aanbrengen kanaalplaatvloer | m2 | | G28 |
| 23.04 | §23 | Aanbrengen druklaag | Aanbrengen druklaag | m2 | | G38 |
| 23.05 | §23 | Betonnen trappen | Aanbrengen betonnen trappen | st | | G48 |
| 23.06 | §23 | Aanbrengen ribcasettevloer | Aanbrengen ribcasettevloer | m2 | | G58 |
| 23.07 | §23 | Aanbrengen breedplaatvloer | Aanbrengen breedplaatvloer | m2 | | G68 |
| 23.08 | §23 | Betonnen lateien boven kozijnen binnen | Aanbrengen betonnen lateien | m1 | | G78 |
| 23.09 | §23 | Betonnen lateien boven kozijnen spouw | Aanbrengen betonnen lateien | m1 | | G88 |
| 23.10 | §23 | Betonnen spek/ afdekbanden | Aanbrengen spekbanden | m1 | | G98 |
| 23.11 | §23 | Betonnen kantplanken | Aanbrengen kantplanken | m1 | | G108 |
| 23.12 | §23 | Betonnen kolommen | Aanbrengen betonnen kolommen | st | | G118 |
| 24.01 | §24 | Timmerwerkzaamheden | | m2 | | G8 |
| 24.02 | §24 | Timmerwerkzaamheden | | m1 | | G18 |
| 24.03 | §24 | Timmerwerkzaamheden | | st | | G28 |
| 25.01 | §25 | Staalconstructie | | kg | | G21 |
| 25.02 | §25 | Ondersabelen kolommen | Ondersabelen kolommen | st | | G31 |
| 25.03 | §25 | Vullen stalen kolommen met beton | Vullen stalen kolommen met beton | st | | G41 |
| 25.04 | §25 | Aanbrengen chemische ankers | Aanbrengen chemische ankers | st | | G51 |
| 26.01 | §26 | Aanbrengen prefab schoorsteen | Aanbrengen chemische ankers | st | | G8 |
| 30.01 | §30 | Stelkozijnen voor aluminium/kunststof koz. | Aanbrengen stelkozijnen | m1 | | G8 |
| 30.02 | §30 | Aluminium kozijnen | Aanbrengen aluminium kozijnen | m2 | aantal (?) | G18 |
| 30.03 | §30 | Aluminium vliesgevels | Aanbrengen aluminium kozijnen | m2 | | G28 |
| 30.04 | §30 | Houten buitenkozijnen | Aanbrengen houten buitenkozijnen | m2 | aantal (?) | G38 |
| 30.05 | §30 | Afhangen deuren in houten buitenkozijnen | Afhangen deuren in houten buitenkozijnen | st | | G48 |
| 30.06 | §30 | Overheaddeur | Aanbrengen overheaddeur | st | | G58 |
| 30.07 | §30 | Houten binnenkozijnen | Aanbrengen houten binnenkozijnen | m2 | aantal (?) | G68 |
| 30.08 | §30 | Houten montage kozijn | Aanbrengen houten montagekozijn | st | | G78 |
| 30.09 | §30 | Binnendeuren in houten kozijnen | Aanbrengen binnendeuren in houten kozijnen | st | | G88 |
| 30.10 | §30 | Hardglazen deur | Aanbrengen hardglazen deur | st | | G98 |
| 30.11 | §30 | Ventilatierooster | Aanbrengen ventilatieroosters | m1 | | G108 |
| 30.12 | §30 | Aanbrengen panelenschuifwand | Aanbrengen vouwwand | st | | G118 |
| 30.13 | §30 | Hang & sluitwerk t.b.v. binnendeuren | Aanbrengen hang & sluitwerk t.b.v. binnendeur | st | | G128 |
| 30.14 | §30 | Aanbrengen vingerbeveiliging | Aanbrengen vingerbeveiliging | st | | G138 |
| 30.15 | §30 | Schopplaten | Aanbrengen schopplaten | st | | G148 |
| 30.16 | §30 | Lichtkoepels | Aanbrengen lichtkoepels | st | | G158 |
| 30.17 | §30 | Lichtstraten | Aanbrengen lichtstraten | st | | G168 |
| 30.18 | §30 | Aanbrengen dakramen | Aanbrengen lichtstraten | st | | G178 |
| 30.19 | §30 | dakluik | Aanbrengen dakluik t.b.v. bereikbaarheid pl.dak | st | | G188 |
| 30.20 | §30 | Garagedeur | Aanbrengen lichtstraten | st | | G198 |
| 30.21 | §30 | Trafopui | Aanbrengen trafopui | st | | G208 |
| 31.01 | §31 | Gevelbeplating | Aanbrengen gevelbeplating | m2 | | G19 |
| 31.02 | §31 | Lichtstraatopstand | Aanbrengen lichtstraatopstand | m1 | | G29 |
| 31.03 | §31 | Dakbeplating | Aanbrengen dakbeplating | m2 | | G45 |
| 31.04 | §31 | Gezette staalplaat op dak | Aanbrengen gezette staalplaat op dak | m1 | | G55 |
| 31.05 | §31 | Trespa buitenplafond | Aanbrengen trespa buitenplafond | m2 | | G65 |
| 31.06 | §31 | Trespa gevelbekleding | Aanbrengen trespa gevelbekleding | m2 | | G75 |
| 32.01 | §32 | Stalen trap | Aanbrengen stalen trappen | st | | G8 |
| 32.02 | §32 | Stalen spiltrap | Aanbrengen stalen spiltrap | st | | G18 |
| 32.03 | §32 | Hardhouten trap | Aanbrengen hardhouten trap | st | | G28 |
| 32.04 | §32 | Vuren trap | Aanbrengen vuren trap | st | | G38 |
| 32.05 | §32 | Traphekwerk op vloerrand hardhouten trap | Aanbrengen traphekwerk op vloerrand hardh. Trap | m1 | | G48 |
| 32.06 | §32 | Traphekwerk op vloerrand vuren trap | Aanbrengen traphekwerk op vloerrand vuren trap | m1 | | G58 |
| 32.07 | §32 | Muurleuning t.b.v. hardhouten trap | Aanbrengen traphekwerk op vloerrand vuren trap | m1 | | G68 |
| 32.08 | §32 | Muurleuning t.b.v. vuren trap | Aanbrengen traphekwerk op vloerrand vuren trap | m1 | | G78 |
| 32.09 | §32 | Vlizotrappen | Aanbrengen vlizotrap | st | | G88 |
| 33.01 | §33 | Bitumieuze dakbedekking | Aanbrengen bitumieuze dakbedekking | m2 | | G14 |
| 33.02 | §33 | Kunststof dakbedekking | Aanbrengen kunststof dakbedekking | m2 | | G30 |
| 33.03 | §33 | Cannelurevulling | Aanbrengen cannelurevulling boven wanden | m1 | | G40 |
| 33.04 | §33 | APP gebrand op fundering | APP gebrand op fundering | m1 | | G50 |
| 33.05 | §33 | Keramische dakpannen | Aanbrengen keramische dakpannen | m2 | | G60 |
| 33.06 | §33 | Betonnen dakpannen | Aanbrengen betonnen dakpannen | m2 | | G70 |
| 34.01 | §34 | Isolatieglas in houten buitenkozijnen | Isolatieglas | m2 | | G8 |
| 34.02 | §34 | Enkelglas | Aanbrengen enkelglas | m2 | | G18 |
| 34.03 | §34 | 30 minuten brandwerend glas | Aanbrengen 30 minuten brandwerend glas | m2 | | G28 |
| 34.04 | §34 | 60 minuten brandwerend glas | Aanbrengen 60 minunten brandwerend glas | m2 | | G38 |
| 34.05 | §34 | Spiegeldraadglas | Aanbrengen spiegeldraadglas | m2 | | G48 |
| 34.06 | §34 | Veiligheidsglas tot 1200 + vloer | Aanbrengen veiligheidsglas tot 1200 + vloer | m2 | | G58 |
| 34.07 | §34 | Gelaagd glas | Aanbrengen gelaagd glas | m2 | | G68 |
| 34.08 | §34 | Veiligheidsglas tot 1200 + vloer | Aanbrengen gehard glas | m2 | | G78 |
| 35.01 | §35 | Holonite vensterbanken | Aanbrengen holonite vensterbanken | m1 | | G8 |
| 35.02 | §35 | Natuursteen vensterbanken | Aanbrengen natuursteen vensterbanken | m1 | | G18 |
| 35.03 | §35 | Holonite binnendeurdorpels | Aanbrengen holonite binnendeurdorpels | m1 | | G28 |
| 35.04 | §35 | Hardstenen binnendeurdorpels | Aanbrengen hardstenen binnendeurdorpels | m1 | | G38 |
| 35.05 | §35 | Hardstenen buitendeurdorpels | Aanbrengen hardstenen buitendeurdorpels | m1 | | G48 |
| 35.06 | §35 | Hardstenen neuten | Aanbrengen hardstenen neuten | st | | G58 |
| 35.07 | §35 | Natuurstenen vloer | Aanbrengen natuurstenen vloer | m2 | | G68 |
| 35.08 | §35 | Natuurstenen bekleding gevel | Aanbrengen natuurstenen bekleding op de gevel | m2 | | G78 |
| 36.01 | §36 | Aanbrengen kitwerk tegelwerk | Aanbrengen kitwerk inwendige hoeken tegelwerk | m1 | | G8 |
| 36.02 | §36 | Kitwerk rond sanitair + aanrecht | Aanbrengen kitwerk rond sanitair + aanrecht | m1 | | G18 |
| 36.03 | §36 | Kitwerk tussen prefab betonnen elementen | Aanbrengen kitwerk tussen prefab elementen | m1 | | G28 |
| 36.04 | §36 | Schuimband rondom stelkozijnen | Aanbrengen schuimband rondom stelkozijnen | m1 | | G38 |
| 36.05 | §36 | Kitwerk rondom buitenkozijnen | Aanbrengen kitwerk rondom buitenkozijnen | m1 | | G48 |
| 36.06 | §36 | Kitwerk dilatatievoegen | Aanbrengen kitwerk in dilatatievoegen | m1 | | G58 |
| 37.01 | §37 | Na-isolatie | | ? | | G8 |
| 38.01 | §38 | Screens handbediend | Aanbrengen screens handbediend | m2 | | G8 |
| 38.02 | §38 | Screens elektrisch | Aanbrengen screens elektrisch | m2 | | G18 |
| 38.03 | §38 | Rolluik handbediend | Aanbrengen rolluiken handbediend | m2 | | G28 |
| 38.04 | §38 | Rolluik elektrisch | Aanbrengen rolluiken elektrisch | m2 | | G38 |
| 38.05 | §38 | Uitval zonnescherm | Aanbrengen uitval zonnescherm | m1 | | G48 |
| 40.01 | §40 | Aanwerken sleuven + naden | Aanwerken sleuven + naden | m1 | | G8 |
| 40.02 | §40 | Affilmen kalkzandsteen lijmblokken | Affilmen kalkzandsteen lijmblokken | m2 | | G24 |
| 40.03 | §40 | B12 achter tegelwerk | Affilmen kalkzandsteen lijmelementen | m2 | | G34 |
| 40.04 | §40 | Filmlaag op MS-wanden | Filmlaag op MS-wanden | m2 | | G50 |
| 40.05 | §40 | Blauwpleisterwerk | Aanbrengen blauw pleisterwerk | m2 | | G66 |
| 40.06 | §40 | Behangklaar maken betonnen kolommen | Behangklaar maken betonnen kolommen | m1 | | G76 |
| 40.07 | §40 | Toeslag stucwerk ronde wand | Toeslag stucwerk ronde wand | m2 | | G86 |
| 40.08 | §40 | Toeslag wanden sausklaar | Toeslag wanden sausklaar | m2 | | G96 |
| 40.09 | §40 | Spuitwerk op wanden | Aanbrengen spuitwerk op wanden | m2 | | G106 |
| 40.10 | §40 | Spuitwerk op plafond | Aanbrengen spuitwerk op plafond | m2 | | G116 |
| 40.11 | §40 | Stucwerk op plafond | Aanbrengen stucwerk op plafond | m2 | | G126 |
| 40.12 | §40 | Schuurwerk op wanden | Aanbrengen schuurwerk op wanden | m2 | | G136 |
| 40.13 | §40 | Schuurwerk op plafond | Aanbrengen schuurwerk op plafond | m2 | | G146 |
| 40.14 | §40 | Hoeksperen | Aanbrengen hoeksperen | m1 | | G156 |
| 40.15 | §40 | Stucstopprofielen | Aanbrengen stucstopprofielen | m1 | | G166 |
| 40.16 | §40 | Wapeningsgaas | Aanbrengen wapeningsgaas | m1 | | G176 |
| 40.17 | §40 | Buitengevelisolatie | Aanbrengen buitengevelisolatie | m2 | | G192 |
| 40.18 | §40 | Spachtelputz | Aanbrengen spachtelputz | m2 | | G202 |
| 41.01 | §41 | Wandtegelwerk | Aanbrengen wandtegelwerk | m2 | | G19 |
| 41.02 | §41 | Vloertegelwerk | Aanbrengen vloertegelwerk | m2 | | G40 |
| 41.03 | §41 | Plinttegels | Aanbrengen plinttegels | m1 | | G50 |
| 41.04 | §41 | Striptegels | Aanbrengen striptegels | m1 | | G60 |
| 41.05 | §41 | Toeslag wandtegels diagonaal | toeslag wandtegels diagonaal | m2 | | G70 |
| 41.06 | §41 | Toeslag vloertegels diagonaal | Toeslag vloertegels diagonaal | m2 | | G80 |
| 41.07 | §41 | Hoekprofielen t.p.v. uitwendige hoeken | Aanbrengen hoekprofielen t.p.v. uitwendige hoek | m1 | | G90 |
| 41.08 | §41 | Kimband + pasta | Aanbrengen kimband + pasta | m1 | | G100 |
| 42.01 | §42 | Zandcementdekvloer dik … | Aanbrengen zandcementdekvloer | m2 | Meerdikte (m2), Wapeningsnet (m2), Carborundum (m2) | G19 |
| 42.02 | §42 | Kunststof gietvloeren | Aanbrengen gietvloeren | m2 | | G29 |
| 42.03 | §42 | Afschotlaag op plat dak | Aanbrengen afschotlaag op plat dak | m2 | | G39 |
| 43.01 | §43 | Vloerluik | Aanbrengen vloerluik | st | | G8 |
| 43.02 | §43 | Matomranding | Aanbrengen matomranding | m1 | | G18 |
| 43.03 | §43 | Hoeklijn t.p.v. overheaddeur | Aanbrengen hoeklijn t.p.v. overheaddeur | m1 | | G28 |
| 43.04 | §43 | Aluminium dakrandprofiel | Aanbrengen aluminium dakrandprofiel | m1 | | G38 |
| 43.05 | §43 | Noodoverstorten (spuwer) | Aanbrengen noodoverstorten (spuwer) | st | | G48 |
| 43.06 | §43 | Waterslagen onder kozijnen | Aanbrengen waterslagen onder kozijnen | m1 | | G58 |
| 43.07 | §43 | Bodemplaat in meterkast | Aanbrengen bodemplaat in meterkast | st | | G68 |
| 43.08 | §43 | Hoeklijnen boven kruipopeningen | Aanbrengen hoeklijnen boven kruipopeningen | m1 | | G78 |
| 44.01 | §44 | Systeemplafond | Aanbrengen systeemplafond | m2 | | G14 |
| 44.02 | §44 | Gipsvinylplafond | Aanbrengen gipsvinylplafond | m2 | | G30 |
| 44.03 | §44 | Houtwolcementplaat plafond | Aanbrengen houtwolcementplaat plafond | m2 | | G46 |
| 44.04 | §44 | MS-wanden | Aanbrengen MS-wanden | m2 | | G67 |
| 44.05 | §44 | MS-voorzetwanden | Aanbrengen MS-voorzetwanden | m2 | | G88 |
| 44.06 | §44 | Voorzetwanden t.p.v. toilet | Aanbrengen voorzetwanden t.p.v. toilet | m2 | | G98 |
| 44.07 | §44 | Drukschotten boven hardglazen wanden | Aanbrengen drukschotten | m1 | | G108 |
| 44.08 | §44 | Sanitaire wanden | Aanbrengen sanitaire wanden | m2 | | G124 |
| 45.01 | §45 | Brandwerende betimmeringen | Aanbrengen brandwerende betimmeringen | m1 | | G8 |
| 45.02 | §45 | Vloerplinten | Aanbrengen vloerplinten | m1 | | G18 |
| 45.03 | §45 | Koof t.p.v. systeemplafond | Aanbrengen koof t.p.v. systeemplafond | m1 | | G28 |
| 45.04 | §45 | Aftimmeren houten buitenkozijnen | Aftimmeren houten buitenkozijnen | m1 | | G38 |
| 45.05 | §45 | Aftimmeren houten binnenkozijnen | Aftimmeren houten binnenkozijnen | m1 | | G48 |
| 45.06 | §45 | Werzalith vensterbanken | Aanbrengen Werzalith vensterbanken | m1 | | G58 |
| 45.07 | §45 | Boeiboord | Aanbrengen boeiboord | m1 | | G68 |
| 45.08 | §45 | Betimmeringen vloerranden | Aanbrengen vloerrand betimmeringen | m1 | | G78 |
| 45.09 | §45 | gipsplafond | Aanbrengen gipsplafond | m2 | | G88 |
| 45.10 | §45 | Omtimmering t.b.v. verdelers | Omtimmering t.b.v. verdelers | st | | G98 |
| 46.01 | §46 | Schilderwerk buitenkozijnen | Schilderwerk buitenkozijnen | m2 | | G8 |
| 46.02 | §46 | Schilderwerk binnenkozijnen | Schilderwerk binnenkozijnen | m1 | | G18 |
| 46.03 | §46 | Schilderwerk voordeuren | Schilderwerk voordeuren | st | | G28 |
| 46.04 | §46 | Schilderwerk vloerplinten | Schilderwerk vloerplinten | m1 | | G38 |
| 46.05 | §46 | Schilderwerk betimmeringen | Schilderwerk betimmeringen | m2 | | G48 |
| 46.06 | §46 | Schilderwerk gipsplaten | Schilderwerk gipsplaten | m2 | | G58 |
| 46.07 | §46 | Schilderwerk trap | Schilderwerk trap | st | | G68 |
| 46.08 | §46 | Sauswerk wanden | Sauswerk wanden | m2 | | G89 |
| 46.09 | §46 | Glasvliesweefsel + texen | Glasvliesweefsel + texen | m2 | | G110 |
| 46.10 | §46 | Latex op beton | Aanbrengen latex op beton | m2 | | G120 |
| 46.11 | §46 | Brandwerend schilderen ronde kolommen | Brandwerend schilderen van ronde kolommen | st | | G130 |
| 48.01 | §48 | Marmoleum | Aanbrengen marmoleum | m2 | | G19 |
| 48.02 | §48 | Schoonloopmat | Aanbrengen schoonloopmat | m2 | | G29 |
| 48.03 | §48 | rRubberen ringmat | Aanbrengen rubberen ringmat | m2 | | G39 |
| 48.04 | §48 | Zachte vloerbedekking | Aanbrengen zachte vloerbedekking | m2 | | G60 |
| 48.05 | §48 | Overgangsprofielen | Aanbrengen overgangsprofielen | st | | G70 |
| 48.06 | §48 | Kunststof vloerafwerking | Aanbrengen kunststof vloerafwerking | m2 | | G91 |
| 48.07 | §48 | Egaliseren vloeren | Egaliseren vloeren | m2 | | G112 |
| 48.08 | §48 | Bekleden traptreden | Bekleden traptreden | m1 | | G122 |
| 48.09 | §48 | Parketvloeren | Aanbrengen parketvloeren | m2 | | G143 |
| 48.10 | §48 | Siergrindvloer | Aanbrengen siergrindvloer | m2 | | G164 |
| 48.11 | §48 | Oxaanolie op betonvloeren | Aanbrengen oxaanolie op betonvloeren | m2 | | G174 |
