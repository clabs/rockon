from __future__ import annotations

from library.custom_model import models


class FederalState(models.TextChoices):
    BW = "BW", "Baden-Württemberg"
    BY = "BY", "Bayern"
    BE = "BE", "Berlin"
    BB = "BB", "Brandenburg"
    HB = "HB", "Bremen"
    HH = "HH", "Hamburg"
    HE = "HE", "Hessen"
    MV = "MV", "Mecklenburg-Vorpommern"
    NI = "NI", "Niedersachsen"
    NW = "NW", "Nordrhein-Westfalen"
    RP = "RP", "Rheinland-Pfalz"
    SL = "SL", "Saarland"
    SN = "SN", "Sachsen"
    ST = "ST", "Sachsen-Anhalt"
    SH = "SH", "Schleswig-Holstein"
    TH = "TH", "Thüringen"
    XX = "XX", "Nicht in Deutschland"
