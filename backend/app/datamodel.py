"""Datamodel van de hoeveelhedentool.

Vier onderdelen (zie CLAUDE.md):
- Element:          een bouwdeel uit het IFC-model (wand, vloer, kolom, ...).
- Calculatieregel:  één blok uit onze uittrekstaat-Excel (bijv. "Kelderwanden van beton").
- Koppeling:        verbindt een element met een calculatieregel. Veel-op-veel: één betonwand
                    hangt aan betonmortel, bekisting, wapening én schilderwerk, en één
                    calculatieregel telt de hoeveelheden van veel elementen op.
- Meetinstellingen: hoe er gemeten wordt (bruto/netto, sparingen, zijden, ...).

Opslag (SQLite per project) volgt in fase 2; dit zijn de gedeelde modellen.
"""
from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Eenheid = Literal["m1", "m2", "m3", "st", "kg"]
"""Eenheden uit de uittrekstaat: m1 (strekkende meter), m2, m3, stuks, kilogram."""


class Element(BaseModel):
    """Een bouwdeel uit het IFC-model. Herkenbaar aan de GlobalId (blijft gelijk tussen modelversies)."""

    global_id: str
    ifc_klasse: str
    naam: Optional[str] = None
    type_naam: Optional[str] = None
    materiaal: Optional[str] = None  # None = geen materiaal in het model (komt in het importrapport)
    verdieping: Optional[str] = None  # None = niet aan een verdieping gekoppeld


class Hoeveelheidskolom(BaseModel):
    """Eén uitkomst van een calculatieregel, bijv. de kolom 'tot.' in m2 of 'beton' in m3.

    De eerste hoeveelheidskolom van een regel is de hoofdhoeveelheid; de overige zijn afgeleid
    (bijv. beton en wapening bij een kelderwand).
    """

    naam: str  # kopnaam in de Excel, bijv. "tot.", "beton", "tot. Wap."
    kolom: str  # kolomletter in de Excel, bijv. "G"
    eenheid: Optional[Eenheid] = None  # None = eenheid ontbreekt in het template
    totaalcel: Optional[str] = None  # bijv. "G8"
    verliescel: Optional[str] = None  # cel met het verliespercentage, bijv. "J54"
    verlies_procent: Optional[float] = None  # waarde in het template (kan leeg zijn)


class Calculatieregel(BaseModel):
    """Eén blok in de uittrekstaat: titel, kopregel, invoerrijen en totaalregel.

    id = "<hoofdstuk>.<volgnummer>" (bijv. "21.05"); titels zijn namelijk niet uniek.
    """

    id: str
    hoofdstuk: str  # STABU-hoofdstuk, bijv. "21"
    tabblad: str  # bijv. "§21"
    titel: str
    omschrijving: Optional[str] = None  # tekst in de eerste invoerrij, bijv. "Aanbrengen werkvloer van beton"
    hoeveelheden: list[Hoeveelheidskolom] = Field(min_length=1)
    invoerkolommen: dict[str, str] = Field(default_factory=dict)  # kolom -> kopnaam, bijv. {"C": "lengte"}
    invoerrijen: list[int] = Field(default_factory=list)
    waarschuwingen: list[str] = Field(default_factory=list)  # opvallende zaken in het template

    @property
    def eenheid(self) -> Optional[str]:
        """Eenheid van de hoofdhoeveelheid."""
        return self.hoeveelheden[0].eenheid

    @property
    def afgeleide_hoeveelheden(self) -> list[Hoeveelheidskolom]:
        return self.hoeveelheden[1:]

    def hoeveelheidskolom(self, kolom: Optional[str]) -> Optional[Hoeveelheidskolom]:
        """Zoek een hoeveelheidskolom op kolomletter; None geeft de hoofdhoeveelheid."""
        if kolom is None:
            return self.hoeveelheden[0]
        return next((h for h in self.hoeveelheden if h.kolom == kolom), None)


class Koppelbron(str, Enum):
    automatisch = "automatisch"  # voorgesteld via de koppeltabel
    handmatig = "handmatig"  # door de calculator gekozen; wint altijd van automatisch


class Koppeling(BaseModel):
    """Verbindt één element met één uitkomst van één calculatieregel."""

    global_id: str
    calculatieregel_id: str
    hoeveelheidskolom: Optional[str] = None  # kolomletter; None = hoofdhoeveelheid van de regel
    meetwijze: str  # naam van de rekenregel, bijv. "zijvlak_netto_2_zijden" (fase 3)
    meegenomen: bool = True  # aan/uitvinken (fase 4)
    reden_uitgesloten: Optional[str] = None
    bron: Koppelbron = Koppelbron.automatisch

    @property
    def sleutel(self) -> tuple[str, str, Optional[str]]:
        return (self.global_id, self.calculatieregel_id, self.hoeveelheidskolom)


class Meetinstellingen(BaseModel):
    """Meetinstellingen, globaal of per calculatieregel.

    None betekent "niet ingesteld": de waarde komt dan van het niveau erboven. De bouwkundige
    standaarden (profiel "BMN standaard") stelt Bastiaan vast in fase 4; tot die tijd staan ze
    bewust op None.
    """

    model_config = ConfigDict(validate_assignment=True)

    bruto_netto: Optional[Literal["bruto", "netto"]] = None
    sparing_drempel_m2: Optional[float] = Field(default=None, ge=0)  # sparingen kleiner dan dit niet aftrekken
    zijden: Optional[Literal[1, 2]] = None  # zijvlakken 1 of 2 zijden
    dagkanten_meenemen: Optional[bool] = None
    kengetallen: dict[str, float] = Field(default_factory=dict)  # bijv. {"wapening_kg_m3": 100}
    afronding_decimalen: Optional[int] = Field(default=None, ge=0, le=6)
    opslag_procent: float = 0.0  # optionele opslag per regel, standaard 0%

    def aangevuld_met(self, basis: "Meetinstellingen") -> "Meetinstellingen":
        """Deze instellingen bovenop `basis`: alleen wat hier expliciet is ingesteld, overschrijft.

        Kengetallen worden samengevoegd (per kengetal overschrijft dit niveau het niveau erboven).
        """
        waarden = basis.model_dump()
        for veld in self.model_fields_set:
            eigen = getattr(self, veld)
            if veld == "kengetallen":
                waarden[veld] = {**basis.kengetallen, **eigen}
            elif eigen is not None:
                waarden[veld] = eigen
        return Meetinstellingen(**waarden)


class Project(BaseModel):
    """Alles van één project: elementen, calculatieregels, koppelingen en instellingen."""

    naam: str
    elementen: list[Element] = Field(default_factory=list)
    calculatieregels: list[Calculatieregel] = Field(default_factory=list)
    koppelingen: list[Koppeling] = Field(default_factory=list)
    instellingen: Meetinstellingen = Field(default_factory=Meetinstellingen)
    instellingen_per_regel: dict[str, Meetinstellingen] = Field(default_factory=dict)

    def element(self, global_id: str) -> Optional[Element]:
        return next((e for e in self.elementen if e.global_id == global_id), None)

    def regel(self, regel_id: str) -> Optional[Calculatieregel]:
        return next((r for r in self.calculatieregels if r.id == regel_id), None)

    def voeg_koppeling_toe(self, koppeling: Koppeling) -> None:
        """Voeg een koppeling toe na controle op bestaand element, regel en hoeveelheidskolom."""
        if self.element(koppeling.global_id) is None:
            raise ValueError(f"Onbekend element: {koppeling.global_id}")
        regel = self.regel(koppeling.calculatieregel_id)
        if regel is None:
            raise ValueError(f"Onbekende calculatieregel: {koppeling.calculatieregel_id}")
        if regel.hoeveelheidskolom(koppeling.hoeveelheidskolom) is None:
            raise ValueError(
                f"Calculatieregel {regel.id} heeft geen hoeveelheidskolom {koppeling.hoeveelheidskolom}"
            )
        if any(k.sleutel == koppeling.sleutel for k in self.koppelingen):
            raise ValueError(f"Koppeling bestaat al: {koppeling.sleutel}")
        self.koppelingen.append(koppeling)

    def koppelingen_van_element(self, global_id: str) -> list[Koppeling]:
        return [k for k in self.koppelingen if k.global_id == global_id]

    def elementen_van_regel(self, regel_id: str) -> list[Element]:
        ids = {k.global_id for k in self.koppelingen if k.calculatieregel_id == regel_id}
        return [e for e in self.elementen if e.global_id in ids]

    def effectieve_instellingen(self, regel_id: str) -> Meetinstellingen:
        """Instellingen per regel gaan voor de globale instellingen."""
        eigen = self.instellingen_per_regel.get(regel_id)
        return eigen.aangevuld_met(self.instellingen) if eigen else self.instellingen
