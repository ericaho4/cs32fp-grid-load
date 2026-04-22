import streamlit as st
import os
from data_loader import load_8760_data

HERE = os.path.dirname(os.path.abspath(__file__))
from simulator import simulate_grid
from visualize import plot_generation, plot_battery


# -----------------------------
# HELPERS
# -----------------------------
def scale_generation(raw_values, chosen_capacity_kw, baseline_capacity_kw=10.0):
    scale_factor = chosen_capacity_kw / baseline_capacity_kw
    return [value * scale_factor for value in raw_values]


def safe_divide(numerator, denominator):
    if denominator == 0:
        return 0.0
    return numerator / denominator


def pmt(r, n, pv):
    """Annual loan payment: rate r, n years, present value pv (CapEx)."""
    if r == 0:
        return pv / n
    return pv * r / (1 - (1 + r) ** -n)



# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Grid Load Simulator", layout="wide")
st.title("Grid Load Simulator")

# -----------------------------
# SIDEBAR — CAPACITY INPUTS
# -----------------------------
st.sidebar.header("Capacity Inputs")

solar_capacity_kw = st.sidebar.number_input(
    "Solar Capacity (kW)", min_value=0.0, value=10.0, step=1.0
)
wind_capacity_kw = st.sidebar.number_input(
    "Wind Capacity (kW)", min_value=0.0, value=10.0, step=1.0
)
battery_capacity_kwh = st.sidebar.number_input(
    "Battery Capacity (kWh)", min_value=0.0, value=10.0, step=1.0
)
baseload_capacity_kw = st.sidebar.number_input(
    "Baseload Capacity (kW)", min_value=0.0, value=0.0, step=1.0
)

month = st.sidebar.selectbox("Month", list(range(1, 13)))
run_full_year = st.sidebar.checkbox("Run Full Year", value=False)

# -----------------------------
# SIDEBAR — FINANCING INPUTS
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Financing Inputs")
st.sidebar.caption(
    "Enter capital cost per unit of capacity. Annual cost is computed via a PMT "
    "loan-payment formula and divided by annual generation to yield $/MWh."
)

solar_capex_per_kw = st.sidebar.number_input(
    "Solar CapEx ($/kW)", min_value=0.0, value=800.0, step=50.0, format="%.0f"
)
wind_capex_per_kw = st.sidebar.number_input(
    "Wind CapEx ($/kW)", min_value=0.0, value=1900.0, step=50.0, format="%.0f"
)
battery_capex_per_kwh = st.sidebar.number_input(
    "Battery CapEx ($/kWh storage)", min_value=0.0, value=400.0, step=25.0, format="%.0f"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Baseload Source")

nuclear_info_html = (
    '<span title="Nuclear financing: Interest rate 7%, Lifespan 40 years, '
    'CapEx ~$8,000/kW. Annual payment = CapEx × kW × PMT(7%, 40 yrs)." '
    'style="cursor:help; font-size:14px;">ℹ️</span>'
)

baseload_type = st.sidebar.selectbox(
    "Baseload Source Type",
    options=["Nuclear", "LNG"],
    index=0,
)

if baseload_type == "Nuclear":
    st.sidebar.markdown(
        f"**Nuclear** {nuclear_info_html} — PMT at 7% over 40 years, $8,000/kW CapEx",
        unsafe_allow_html=True,
    )
    default_baseload_capex = 8000.0
else:
    st.sidebar.markdown("**LNG** — PMT at 5% over 30 years, $1,000/kW CapEx")
    default_baseload_capex = 1000.0

baseload_capex_per_kw = st.sidebar.number_input(
    f"{baseload_type} CapEx ($/kW)",
    min_value=0.0,
    value=default_baseload_capex,
    step=100.0,
    format="%.0f",
)

# -----------------------------
# LOAD DATA
# -----------------------------
filename = os.path.join(HERE, "Boston Renewables Model 2026.xlsx")

if run_full_year:
    datetimes, load_vals, raw_solar_vals, raw_wind_vals = load_8760_data(filename, month=None)
    period_label = "Full Year"
else:
    datetimes, load_vals, raw_solar_vals, raw_wind_vals = load_8760_data(filename, month=month)
    period_label = f"Month {month}"

_, fy_load_vals, fy_raw_solar, fy_raw_wind = load_8760_data(filename, month=None)

# -----------------------------
# SCALE GENERATION
# -----------------------------
baseline_kw = 10.0

solar_vals = scale_generation(raw_solar_vals, solar_capacity_kw, baseline_kw)
wind_vals  = scale_generation(raw_wind_vals,  wind_capacity_kw,  baseline_kw)

fy_solar_kwh = sum(scale_generation(fy_raw_solar, solar_capacity_kw, baseline_kw)) / 1000
fy_wind_kwh  = sum(scale_generation(fy_raw_wind,  wind_capacity_kw,  baseline_kw)) / 1000

# -----------------------------
# UNIT CONVERSIONS
# -----------------------------
battery_capacity_wh = battery_capacity_kwh * 1000
baseload_capacity_w = baseload_capacity_kw  * 1000
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
    baseload_type=baseload_type.lower(),
)

# -----------------------------
# FINANCING CALCULATIONS (PMT)
# -----------------------------
SOLAR_R, SOLAR_N = 0.05, 20
WIND_R,  WIND_N  = 0.05, 20
BATT_R,  BATT_N  = 0.05, 10
NUC_R,   NUC_N   = 0.07, 40
LNG_R,   LNG_N   = 0.05, 30

solar_capex_total   = solar_capex_per_kw    * solar_capacity_kw
wind_capex_total    = wind_capex_per_kw     * wind_capacity_kw
battery_capex_total = battery_capex_per_kwh * battery_capacity_kwh

if baseload_type == "Nuclear":
    bl_r, bl_n = NUC_R, NUC_N
else:
    bl_r, bl_n = LNG_R, LNG_N
baseload_capex_total = baseload_capex_per_kw * baseload_capacity_kw

solar_annual_cost    = pmt(SOLAR_R, SOLAR_N, solar_capex_total)
wind_annual_cost     = pmt(WIND_R,  WIND_N,  wind_capex_total)
battery_annual_cost  = pmt(BATT_R,  BATT_N,  battery_capex_total)
baseload_annual_cost = pmt(bl_r,    bl_n,     baseload_capex_total)

fy_baseload_kwh = baseload_capacity_kw * 8760.0

solar_cost_per_mwh    = safe_divide(solar_annual_cost,    fy_solar_kwh)    * 1000
wind_cost_per_mwh     = safe_divide(wind_annual_cost,     fy_wind_kwh)     * 1000
battery_cost_per_mwh  = safe_divide(battery_annual_cost,  fy_solar_kwh + fy_wind_kwh) * 1000
baseload_cost_per_mwh = safe_divide(baseload_annual_cost, fy_baseload_kwh) * 1000

total_annual_cost = (
    solar_annual_cost + wind_annual_cost + battery_annual_cost + baseload_annual_cost
)
fy_total_kwh = fy_solar_kwh + fy_wind_kwh + fy_baseload_kwh
system_cost_per_mwh = safe_divide(total_annual_cost, fy_total_kwh) * 1000

# -----------------------------
# SUMMARY METRICS
# -----------------------------
total_hours = results["hours"]
hours_curtailed = sum(1 for x in results["curtailed_trace"] if x > 0)
hours_dark      = sum(1 for x in results["unmet_trace"]    if x > 0)

pct_hours_curtailed = 100 * safe_divide(hours_curtailed, total_hours)
pct_hours_dark      = 100 * safe_divide(hours_dark,      total_hours)

total_load_wh       = results["total_load"]
total_generation_wh = results["total_generation"]
total_unmet_wh      = results["total_unmet"]
total_curtailed_wh  = results["total_curtailed"]

total_generated_kwh = total_generation_wh / 1000
total_generated_mwh = total_generated_kwh / 1000
total_consumed_mwh  = (total_load_wh - total_unmet_wh) / 1_000_000

load_met = results["total_unmet"] == 0 and hours_dark == 0

# -----------------------------
# BACKGROUND COLOR
# -----------------------------
bg_color = "#1a3d1a" if load_met else "#3d1a1a"
st.markdown(
    f"<style>.stApp {{ background-color: {bg_color}; }}</style>",
    unsafe_allow_html=True,
)

# -----------------------------
# SIMULATION RESULTS
# -----------------------------
st.header("Simulation Results — " + period_label)

col1, col2 = st.columns(2)
with col1:
    st.metric("Hours Curtailed",            f"{hours_curtailed} hrs")
    st.metric("Curtailed Hours (%)",         f"{pct_hours_curtailed:.2f}%")
    st.metric("Total Curtailed Energy (Wh)", f"{total_curtailed_wh:,.0f}")
with col2:
    st.metric("Hours Dark",              f"{hours_dark} hrs")
    st.metric("Dark Hours (%)",           f"{pct_hours_dark:.2f}%")
    st.metric("Total Unmet Demand (Wh)", f"{total_unmet_wh:,.0f}")

st.markdown("---")
d1, d2, d3, d4 = st.columns(4)
with d1:
    st.metric("Feasible",         str(results["feasible"]))
with d2:
    st.metric("% Load Served",    f"{results['percent_load_served']:.2f}%")
with d3:
    st.metric("Total Generation", f"{total_generated_mwh:,.1f} MWh")
with d4:
    st.metric("Total Load",       f"{total_load_wh/1e6:,.1f} MWh")

# -----------------------------
# PLOTS
# -----------------------------
st.markdown("---")
st.subheader("Generation Plot")
fig1 = plot_generation(
    datetimes=datetimes,
    load_vals=load_vals,
    solar_vals=solar_vals,
    wind_vals=wind_vals,
    baseload_vals=baseload_vals,
    period_label=period_label,
)
st.pyplot(fig1)

st.subheader("Battery State of Charge")
fig2 = plot_battery(
    datetimes=datetimes,
    battery_trace=results["battery_trace"],
    period_label=period_label,
)
st.pyplot(fig2)

# -----------------------------
# FINANCING RESULTS
# -----------------------------
st.markdown("---")
st.header("Financing (Annualized Capital Cost)")
st.caption(
    "Annual costs are computed with the PMT loan-payment formula applied to total CapEx. "
    "$/MWh figures use full-year (8,760 h) generation estimates."
)

fc1, fc2, fc3, fc4 = st.columns(4)

with fc1:
    st.subheader("Solar")
    st.metric("CapEx",
              f"${solar_capex_total:,.0f}",
              help=f"CapEx = ${solar_capex_per_kw:,.0f}/kW × {solar_capacity_kw:,.0f} kW")
    st.metric("Annual Cost",
              f"${solar_annual_cost:,.0f}/yr",
              help=f"PMT(r=5%, n=20 yrs, PV=${solar_capex_total:,.0f})\nFormula: CapEx × r / (1 − (1+r)^−n)")
    st.metric("Full-Year Gen",
              f"{fy_solar_kwh:,.0f} kWh",
              help="Sum of all 8,760 hourly solar output values scaled to chosen capacity (kW).")
    st.metric("Cost per MWh",
              f"${solar_cost_per_mwh:,.2f}" if fy_solar_kwh > 0 else "—",
              help="Annual Cost ÷ Full-Year Generation (kWh) × 1,000")

with fc2:
    st.subheader("Wind")
    st.metric("CapEx",
              f"${wind_capex_total:,.0f}",
              help=f"CapEx = ${wind_capex_per_kw:,.0f}/kW × {wind_capacity_kw:,.0f} kW")
    st.metric("Annual Cost",
              f"${wind_annual_cost:,.0f}/yr",
              help=f"PMT(r=5%, n=20 yrs, PV=${wind_capex_total:,.0f})\nFormula: CapEx × r / (1 − (1+r)^−n)")
    st.metric("Full-Year Gen",
              f"{fy_wind_kwh:,.0f} kWh",
              help="Sum of all 8,760 hourly wind output values scaled to chosen capacity (kW).")
    st.metric("Cost per MWh",
              f"${wind_cost_per_mwh:,.2f}" if fy_wind_kwh > 0 else "—",
              help="Annual Cost ÷ Full-Year Generation (kWh) × 1,000")

with fc3:
    st.subheader("Battery")
    st.metric("CapEx",
              f"${battery_capex_total:,.0f}",
              help=f"CapEx = ${battery_capex_per_kwh:,.0f}/kWh × {battery_capacity_kwh:,.0f} kWh storage")
    st.metric("Annual Cost",
              f"${battery_annual_cost:,.0f}/yr",
              help=f"PMT(r=5%, n=10 yrs, PV=${battery_capex_total:,.0f})\nFormula: CapEx × r / (1 − (1+r)^−n)")
    st.metric("Capacity",
              f"{battery_capacity_kwh:,.0f} kWh",
              help="Total energy storage capacity entered by the user.")
    st.metric("Cost Spread over Solar+Wind MWh",
              f"${battery_cost_per_mwh:,.2f}" if (fy_solar_kwh + fy_wind_kwh) > 0 else "—",
              help="Battery Annual Cost ÷ (Full-Year Solar kWh + Full-Year Wind kWh) × 1,000")

with fc4:
    bl_r_pct = int(bl_r * 100)
    st.subheader(baseload_type)
    st.metric("CapEx",
              f"${baseload_capex_total:,.0f}",
              help=f"CapEx = ${baseload_capex_per_kw:,.0f}/kW × {baseload_capacity_kw:,.0f} kW")
    st.metric("Annual Cost",
              f"${baseload_annual_cost:,.0f}/yr",
              help=f"PMT(r={bl_r_pct}%, n={bl_n} yrs, PV=${baseload_capex_total:,.0f})\nFormula: CapEx × r / (1 − (1+r)^−n)")
    st.metric("Full-Year Gen",
              f"{fy_baseload_kwh:,.0f} kWh",
              help=f"Baseload runs at constant output: {baseload_capacity_kw:,.0f} kW × 8,760 hrs")
    st.metric("Cost per MWh",
              f"${baseload_cost_per_mwh:,.2f}" if fy_baseload_kwh > 0 else "—",
              help="Annual Cost ÷ Full-Year Generation (kWh) × 1,000")

st.markdown("---")
sys1, sys2 = st.columns(2)
with sys1:
    st.metric("Total Annual System Cost",
              f"${total_annual_cost:,.0f}/yr",
              help="Sum of annual costs for Solar + Wind + Battery + Baseload.")
with sys2:
    st.metric("Blended System Cost per MWh Generated",
              f"${system_cost_per_mwh:,.2f}" if fy_total_kwh > 0 else "—",
              help="Total Annual Cost ÷ (Solar + Wind + Baseload full-year kWh) × 1,000")
st.pyplot(fig2)
