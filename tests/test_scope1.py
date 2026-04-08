from ghg_engine.scope1_calculator import calculate_scope1


def test_scope1_basic():
    # With placeholder factor 2.68, activity 10 should return 26.8
    result = calculate_scope1(10)
    assert abs(result - 26.8) < 1e-6


def test_scope1_zero_activity():
    assert calculate_scope1(0) == 0.0


def test_scope1_negative_activity():
    assert calculate_scope1(-5) == -13.4


def test_scope1_large_value():
    result = calculate_scope1(1_000_000)
    assert abs(result - 2_680_000) < 1e-6
