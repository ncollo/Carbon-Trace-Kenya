from ghg_engine.scope1_calculator import calculate_scope1


def test_scope1_basic():
    # With placeholder factor 2.68, activity 10 should return 26.8
    result = calculate_scope1(10)
    assert abs(result - 26.8) < 1e-6
