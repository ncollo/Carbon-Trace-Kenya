from ghg_engine.emission_factor_registry import get_factor


def test_known_factor_returns_correct_value():
    assert get_factor("diesel_l_per_km") == 2.68


def test_ev_factor_is_zero():
    assert get_factor("ev_grid_kwh_per_km") == 0.0


def test_unknown_key_returns_none():
    assert get_factor("nonexistent") is None
