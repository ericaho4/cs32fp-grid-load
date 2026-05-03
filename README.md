# cs32fp-grid-load
2026 CS32 Final Project: Balancing Grid Load with wind, solar, batteries, and baseload energy sources.

Project Description

Build a Python program, and possibly a polished website, that simulates an hourly electricity system for Boston in January. The user can choose capacities for solar, wind, battery storage, and possibly baseload sources like nuclear or gas, and the model checks whether demand is met every hour while reporting cost, curtailment, and dark hours.

Computational Substack

The computationally tractable components of this project include importing hourly load and generation data, simulating hourly system balance, modeling battery charging and discharging over time, calculating unmet demand and curtailment, computing cost metrics, searching across different solar/wind/storage combinations to identify feasible systems, generating visualizations, and building an interactive front end. These tasks are well suited to Python because they rely on time-series data, rule-based simulation, and repeated scenario testing. The necessary data can be referenced from a spreadsheet provided from ESPP90S, which shows grid data for the month of January, sourced from the Boston ISO. This could be expanded later with external load or generation datasets.

Link to the Streamlit APP: https://cs32fp-grid-load.streamlit.app/

## How to Use

Open the app and use the sidebar to configure your energy system, then view the simulation results and cost breakdown on the main page.

### Capacity Inputs

These inputs set how much of each energy source you want to build. The simulation scales Boston ISO hourly generation data proportionally to your chosen capacity.

- **Solar Capacity (kW)** -- the peak power output of your solar installation. Higher values produce more daytime energy but cannot generate at night.
- **Wind Capacity (kW)** -- the rated power output of your wind installation. Wind generates at variable rates day and night based on historical Boston wind data.
- **Battery Capacity (kWh)** -- the total energy storage of your battery system. The battery charges automatically when generation exceeds demand and discharges when demand exceeds generation.
- **Baseload Capacity (kW)** -- a constant power source (Nuclear or LNG) that runs at the same output every hour of the year, regardless of weather.
- **Month** -- which month of the year to simulate (1 through 12). January has the lowest solar output and highest heating demand.
- **Run Full Year** -- check this to simulate all 8,760 hours instead of a single month.

### Financing Inputs

These inputs control the capital cost assumptions used to compute annualized costs.

- **Solar CapEx ($/kW)** -- upfront cost per kilowatt of solar capacity. Financed at 5% over 20 years.
- **Wind CapEx ($/kW)** -- upfront cost per kilowatt of wind capacity. Financed at 5% over 20 years.
- **Battery CapEx ($/kWh storage)** -- upfront cost per kilowatt-hour of battery storage. Financed at 5% over 10 years.
- **Baseload Source Type** -- choose Nuclear (financed at 7% over 40 years, default $8,000/kW) or LNG (financed at 5% over 30 years, default $1,000/kW).
- **Baseload CapEx ($/kW)** -- upfront cost per kilowatt of baseload capacity. Pre-filled with defaults for the selected source type.

### Reading the Results

- **Hours Dark / Total Unmet Demand** -- hours and energy where demand was not met. A feasible system has zero dark hours.
- **Hours Curtailed / Total Curtailed Energy** -- hours and energy where excess generation had to be thrown away because the battery was full and demand was already satisfied.
- **Feasible** -- True only when all demand is met every hour of the simulated period.
- **% Load Served** -- fraction of total demand that was successfully supplied.
- The background turns green when the system is feasible and red when it is not.
- The **Financing** section shows annualized capital cost, full-year generation, and cost per MWh for each source, along with a blended system cost per MWh.

## Tools & AI Assistance

Almost all of the code in this project was revised, checked, and rewritten with the assistance of **ChatGPT** (OpenAI) and **Claude Code** (Anthropic). 

The interactive web application is built with **Streamlit**, an open-source Python framework for creating data apps. [1]

## Citations

[1] Streamlit. *Streamlit — A faster way to build and share data apps*. https://streamlit.io
