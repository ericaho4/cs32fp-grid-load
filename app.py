import streamlit as st
from data_loader import load_8760_data
from simulator import simulate_grid
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


def safe_divide(numerator, denominator):
    if denominator == 0:
        return 0.0
    return numerator / denominator


st.set_page_config(page_title="Grid Load Simulator", layout="wide")

st.title("Grid Load Simulator")

# -----------------------------
# SIDEBAR INPUTS
# -----------------------------
st.sidebar.header("Inputs")

solar_capacity_kw = st.sidebar.number_input(
    "Solar Capacity (kW)",
    min_value=0.0,
    value=10.0,
    step=1.0
)

wind_capacity_kw = st.sidebar.number_input(
    "Wind Capacity (kW)",
    min_value=0.0,
    value=10.0,
    step=1.0
)

battery_capacity_kwh = st.sidebar.number_input(
    "Battery Capacity (kWh)",
    min_value=0.0,
    value=10.0,
    step=1.0
)

baseload_capacity_kw = st.sidebar.number_input(
    "Baseload Capacity (kW)",
    min_value=0.0,
    value=0.0,
    step=1.0
)

month = st.sidebar.selectbox("Month", list(range(1, 13)))
run_full_year = st.sidebar.checkbox("Run Full Year", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("Cost Inputs")

st.sidebar.caption("Generation source costs are entered as $ per kWh generated.")
st.sidebar.caption("Battery cost is entered as $ per kWh of storage capacity.")

solar_cost_per_kwh = st.sidebar.number_input(
    "Solar Cost ($/kWh generated)",
    min_value=0.0,
    value=0.05,
    step=0.01,
    format="%.4f"
)

wind_cost_per_kwh = st.sidebar.number_input(
    "Wind Cost ($/kWh generated)",
    min_value=0.0,
    value=0.04,
    step=0.01,
    format="%.4f"
)

baseload_cost_per_kwh = st.sidebar.number_input(
    "Baseload Cost ($/kWh generated)",
    min_value=0.0,
    value=0.08,
    step=0.01,
    format="%.4f"
)

battery_cost_per_kwh_storage = st.sidebar.number_input(
    "Battery Cost ($/kWh storage capacity)",
    min_value=0.0,
    value=0.02,
    step=0.01,
    format="%.4f"
)

# -----------------------------
# LOAD DATA
# -----------------------------
filename = "Boston Renewables Model 2026.xlsx"

if run_full_year:
    datetimes, load_vals, raw_solar_vals, raw_wind_vals = load_8760_data(filename, month=None)
    period_label = "Full Year"
else:
    datetimes, load_vals, raw_solar_vals, raw_wind_vals = load_8760_data(filename, month=month)
    period_label = f"Month {month}"

# -----------------------------
# SCALE SOLAR AND WIND
# -----------------------------
baseline_solar_capacity_kw = 10.0
baseline_wind_capacity_kw = 10.0

solar_vals = scale_generation(raw_solar_vals, solar_capacity_kw, baseline_solar_capacity_kw)
wind_vals = scale_generation(raw_wind_vals, wind_capacity_kw, baseline_wind_capacity_kw)

# -----------------------------
# UNIT CONVERSIONS
# -----------------------------
battery_capacity_wh = battery_capacity_kwh * 1000
baseload_capacity_w = baseload_capacity_kw * 1000

baseload_vals = [baseload_capacity_w] * len(load_vals)

# -----------------------------
# RUN SIMULATION
# -----------------------------
results = simulate_grid(
    load_vals=load_vals,
    solar_vals=solar_vals,
    wind_vals=wind_vals,
    battery_capacity=battery_capacity_wh,
    baseload_capacity=baseload_capacity_w,
    baseload_type="baseload"
)

# -----------------------------
# SUMMARY METRICS
# -----------------------------
total_hours = results["hours"]

hours_curtailed = sum(1 for x in results["curtailed_trace"] if x > 0)
hours_dark = sum(1 for x in results["unmet_trace"] if x > 0)

pct_hours_curtailed = 100 * safe_divide(hours_curtailed, total_hours)
pct_hours_dark = 100 * safe_divide(hours_dark, total_hours)

total_load_wh = results["total_load"]
total_generation_wh = results["total_generation"]
total_unmet_wh = results["total_unmet"]
total_curtailed_wh = results["total_curtailed"]

# Convert workbook-integrated hourly values to kWh / MWh
total_generated_kwh = total_generation_wh / 1000
total_generated_mwh = total_generated_kwh / 1000

total_consumed_kwh = (total_load_wh - total_unmet_wh) / 1000
total_consumed_mwh = total_consumed_kwh / 1000

solar_energy_kwh = results["total_solar"] / 1000
wind_energy_kwh = results["total_wind"] / 1000
baseload_energy_kwh = results["total_baseload"] / 1000

total_cost = (
    solar_energy_kwh * solar_cost_per_kwh
    + wind_energy_kwh * wind_cost_per_kwh
    + baseload_energy_kwh * baseload_cost_per_kwh
    + battery_capacity_kwh * battery_cost_per_kwh_storage
)

cost_per_mwh_generated = safe_divide(total_cost, total_generated_mwh)
cost_per_mwh_consumed = safe_divide(total_cost, total_consumed_mwh)

load_met = (results["total_unmet"] == 0 and hours_dark == 0)

# -----------------------------
# STATUS BOX
# -----------------------------
status_bg = "#163d22" if load_met else "#4a1616"
status_text = "#7CFC98" if load_met else "#ff8a8a"
status_label = "LOAD MET" if load_met else "LOAD NOT MET"

st.markdown(
    f"""
    <div style="
        background-color: {status_bg};
        color: {status_text};
        padding: 22px;
        border-radius: 12px;
        text-align: center;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 20px;
        border: 2px solid {status_text};
    ">
        {status_label}
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# RESULTS
# -----------------------------
st.header("Results")

col1, col2 = st.columns(2)

with col1:
    st.metric("Cost per MWh Generated", f"${cost_per_mwh_generated:,.2f}")
    st.metric("Hours Curtailed", f"{hours_curtailed} hours")
    st.metric("Curtailed Hours (%)", f"{pct_hours_curtailed:.2f}%")
    st.metric("Total Curtailed Energy (Wh)", f"{total_curtailed_wh:,.2f}")

with col2:
    st.metric("Cost per MWh Consumed", f"${cost_per_mwh_consumed:,.2f}")
    st.metric("Hours Dark", f"{hours_dark} hours")
    st.metric("Dark Hours (%)", f"{pct_hours_dark:.2f}%")
    st.metric("Total Unmet Demand (Wh)", f"{total_unmet_wh:,.2f}")

st.markdown("---")

detail1, detail2, detail3, detail4 = st.columns(4)
with detail1:
    st.metric("Feasible", str(results["feasible"]))
with detail2:
    st.metric("Percent Load Served", f"{results['percent_load_served']:.2f}%")
with detail3:
    st.metric("Total Generation (Wh)", f"{results['total_generation']:,.2f}")
with detail4:
    st.metric("Total Load (Wh)", f"{results['total_load']:,.2f}")

# -----------------------------
# PLOTS
# -----------------------------
st.subheader("Generation Plot")
fig1 = plot_generation(
    datetimes=datetimes,
    load_vals=load_vals,
    solar_vals=solar_vals,
    wind_vals=wind_vals,
    baseload_vals=baseload_vals,
    period_label=period_label
)
st.pyplot(fig1)

st.subheader("Battery Plot")
fig2 = plot_battery(
    datetimes=datetimes,
    battery_trace=results["battery_trace"],
    period_label=period_label
)
st.pyplot(fig2)
