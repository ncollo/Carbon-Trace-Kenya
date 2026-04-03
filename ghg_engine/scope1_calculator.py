from .emission_factor_registry import get_factor


def calculate_scope1(activity_amount: float, unit: str = "km") -> float:
    """Simple placeholder: multiplies activity by a factor.

    `activity_amount` should be in the unit expected by the factor.
    """
    factor = get_factor("diesel_l_per_km") or 0
    return activity_amount * factor
