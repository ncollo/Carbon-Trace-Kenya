"""Versioned registry of emission factors (placeholders).

Replace values with IPCC AR6 / DEFRA / KETRACO data and add versioning.
"""

EMISSION_FACTORS = {
    "diesel_l_per_km": 2.68,  # placeholder coefficient (kgCO2e per L or per km as appropriate)
    "ev_grid_kwh_per_km": 0.0,
}


def get_factor(key: str):
    return EMISSION_FACTORS.get(key)
