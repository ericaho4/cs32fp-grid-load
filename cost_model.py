def compute_system_cost(
    solar_capacity,
    wind_capacity,
    battery_capacity,
    baseload_capacity,
    solar_cost_per_kw,
    wind_cost_per_kw,
    battery_cost_per_kwh,
    baseload_cost_per_kw
):
    """
    Compute a simple total system cost from user-provided cost assumptions.
    """
    total_cost = (
        solar_capacity * solar_cost_per_kw
        + wind_capacity * wind_cost_per_kw
        + battery_capacity * battery_cost_per_kwh
        + baseload_capacity * baseload_cost_per_kw
    )

    return total_cost
