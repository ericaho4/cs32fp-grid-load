from data_loader import load_8760_data
from simulator import simulate_grid
from cost_model import compute_system_cost
from visualize import plot_generation, plot_battery


def scale_generation(raw_values, chosen_capacity_kw, baseline_capacity_kw=10.0):
    """
    Scale hourly generation from the spreadsheet baseline capacity
    to the user-selected capacity.

    Assumes the 8760 sheet's solar and wind columns reflect
    baseline_capacity_kw systems.
    """
    scale_factor = chosen_capacity_kw / baseline_capacity_kw
    return [value * scale_factor for value in raw_values]


def main():
    filename = "Boston Renewables Model 2026.xlsx"

    # ---------------------------------
    # USER-CONTROLLED INPUTS
    # These later become UI widgets.
    # ---------------------------------

    # Time selection
    run_full_year = False
    selected_month = 1   # 1 = January, ..., 12 = December

    # Capacity inputs
    solar_capacity = 10.0          # kW
    wind_capacity = 10.0           # kW
    battery_capacity = 10000.0     # storage units consistent with workbook
    baseload_capacity = 0.0        # constant hourly generation
    baseload_type = "nuclear"      # "nuclear" or "fossil"

    # Cost assumptions
    solar_cost_per_kw = 800.0
    wind_cost_per_kw = 1900.0
    battery_cost_per_kwh = 400.0
    baseload_cost_per_kw = 6500.0 if baseload_type == "nuclear" else 1200.0

    # Spreadsheet baseline assumptions
    baseline_solar_capacity = 10.0
    baseline_wind_capacity = 10.0

    # ---------------------------------
    # LOAD DATA
    # ---------------------------------
    if run_full_year:
        datetimes, load_vals, raw_solar_vals, raw_wind_vals = load_8760_data(
            filename, month=None
        )
        period_label = "Full Year"
    else:
        datetimes, load_vals, raw_solar_vals, raw_wind_vals = load_8760_data(
            filename, month=selected_month
        )
        period_label = f"Month {selected_month}"

    # ---------------------------------
    # SCALE SOLAR AND WIND OUTPUTS
    # ---------------------------------
    solar_vals = scale_generation(
        raw_solar_vals,
        chosen_capacity_kw=solar_capacity,
        baseline_capacity_kw=baseline_solar_capacity
    )

    wind_vals = scale_generation(
        raw_wind_vals,
        chosen_capacity_kw=wind_capacity,
        baseline_capacity_kw=baseline_wind_capacity
    )

    # Create hourly baseload series for plotting
    baseload_vals = [baseload_capacity] * len(load_vals)

    # ---------------------------------
    # RUN SIMULATION
    # ---------------------------------
    results = simulate_grid(
        load_vals=load_vals,
        solar_vals=solar_vals,
        wind_vals=wind_vals,
        battery_capacity=battery_capacity,
        baseload_capacity=baseload_capacity,
        baseload_type=baseload_type
    )

    # ---------------------------------
    # COMPUTE COST
    # ---------------------------------
    total_cost = compute_system_cost(
        solar_capacity=solar_capacity,
        wind_capacity=wind_capacity,
        battery_capacity=battery_capacity,
        baseload_capacity=baseload_capacity,
        solar_cost_per_kw=solar_cost_per_kw,
        wind_cost_per_kw=wind_cost_per_kw,
        battery_cost_per_kwh=battery_cost_per_kwh,
        baseload_cost_per_kw=baseload_cost_per_kw
    )

    # ---------------------------------
    # PRINT RESULTS
    # ---------------------------------
    print("\nGRID SIMULATION RESULTS")
    print("-----------------------")
    print(f"Period: {period_label}")
    print(f"Hours simulated: {results['hours']}")
    print()
    print(f"Solar capacity (kW): {solar_capacity}")
    print(f"Wind capacity (kW): {wind_capacity}")
    print(f"Battery capacity: {battery_capacity}")
    print(f"Baseload type: {baseload_type}")
    print(f"Baseload capacity: {baseload_capacity}")
    print()
    print(f"Solar cost per kW: ${solar_cost_per_kw:,.2f}")
    print(f"Wind cost per kW: ${wind_cost_per_kw:,.2f}")
    print(f"Battery cost per kWh: ${battery_cost_per_kwh:,.2f}")
    print(f"Baseload cost per kW: ${baseload_cost_per_kw:,.2f}")
    print()

    print(f"Total load: {results['total_load']:.2f}")
    print(f"Total solar generation: {results['total_solar']:.2f}")
    print(f"Total wind generation: {results['total_wind']:.2f}")
    print(f"Total {baseload_type} generation: {results['total_baseload']:.2f}")
    print(f"Total generation: {results['total_generation']:.2f}")
    print()

    print(f"Total curtailed energy: {results['total_curtailed']:.2f}")
    print(f"Total unmet demand: {results['total_unmet']:.2f}")
    print(f"Dark hours: {results['dark_hours']}")
    print(f"Percent load served: {results['percent_load_served']:.2f}%")
    print(f"Feasible system: {results['feasible']}")
    print()
    print(f"Simple system cost: ${total_cost:,.2f}")

    print("\nFirst 5 timestamps:")
    print(datetimes[:5])

    # ---------------------------------
    # GENERATE PLOTS
    # ---------------------------------
    plot_generation(
        datetimes=datetimes,
        load_vals=load_vals,
        solar_vals=solar_vals,
        wind_vals=wind_vals,
        baseload_vals=baseload_vals,
        period_label=period_label
    )

    plot_battery(
        datetimes=datetimes,
        battery_trace=results["battery_trace"],
        period_label=period_label
    )


if __name__ == "__main__":
    main()
