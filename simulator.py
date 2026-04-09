def simulate_grid(
    load_vals,
    solar_vals,
    wind_vals,
    battery_capacity,
    baseload_capacity=0.0,
    baseload_type="baseload",
    battery_start=None
):
    """
    Simulate hourly grid balancing with solar, wind, baseload, and battery.

    Unit convention:
    - load_vals, solar_vals, wind_vals, baseload_capacity are all in W
    - because each timestep is 1 hour, the hourly net can be treated as Wh
    - battery_capacity and battery state are in Wh

    Args:
        load_vals (list[float]): hourly load in W
        solar_vals (list[float]): hourly solar generation in W
        wind_vals (list[float]): hourly wind generation in W
        battery_capacity (float): battery storage capacity in Wh
        baseload_capacity (float): constant hourly baseload generation in W
        baseload_type (str): label for baseload source
        battery_start (float or None): starting battery charge in Wh

    Returns:
        dict: simulation results and traces
    """
    if battery_start is None:
        battery = battery_capacity
    else:
        battery = battery_start

    total_load = 0.0
    total_solar = 0.0
    total_wind = 0.0
    total_baseload = 0.0
    total_generation = 0.0
    total_curtailed = 0.0
    total_unmet = 0.0
    dark_hours = 0

    battery_trace = []
    curtailed_trace = []
    unmet_trace = []
    net_trace = []

    for i in range(len(load_vals)):
        load = load_vals[i]
        solar = solar_vals[i]
        wind = wind_vals[i]
        baseload = baseload_capacity

        generation = solar + wind + baseload
        net = generation - load

        total_load += load
        total_solar += solar
        total_wind += wind
        total_baseload += baseload
        total_generation += generation

        curtailed = 0.0
        unmet = 0.0

        if net >= 0:
            charge_room = battery_capacity - battery
            charge = min(net, charge_room)
            battery += charge
            curtailed = net - charge
            total_curtailed += curtailed
        else:
            needed = -net
            discharge = min(needed, battery)
            battery -= discharge
            unmet = needed - discharge
            total_unmet += unmet

            if unmet > 0:
                dark_hours += 1

        battery_trace.append(battery)
        curtailed_trace.append(curtailed)
        unmet_trace.append(unmet)
        net_trace.append(net)

    percent_load_served = 100.0
    if total_load > 0:
        percent_load_served = 100 * (1 - total_unmet / total_load)

    return {
        "hours": len(load_vals),
        "baseload_type": baseload_type,
        "battery_capacity": battery_capacity,
        "baseload_capacity": baseload_capacity,
        "total_load": total_load,
        "total_solar": total_solar,
        "total_wind": total_wind,
        "total_baseload": total_baseload,
        "total_generation": total_generation,
        "total_curtailed": total_curtailed,
        "total_unmet": total_unmet,
        "dark_hours": dark_hours,
        "percent_load_served": percent_load_served,
        "feasible": total_unmet == 0,
        "battery_trace": battery_trace,
        "curtailed_trace": curtailed_trace,
        "unmet_trace": unmet_trace,
        "net_trace": net_trace
    }
