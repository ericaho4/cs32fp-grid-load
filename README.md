# cs32fp-grid-load
2026 CS32 Final Project: Balancing Grid Load with wind, solar, batteries, and baseload energy sources.

Project Description

Build a Python program, and possibly a polished website, that simulates an hourly electricity system for Boston in January. The user can choose capacities for solar, wind, battery storage, and possibly baseload sources like nuclear or gas, and the model checks whether demand is met every hour while reporting cost, curtailment, and dark hours.

Computational Substack

The computationally tractable components of this project include importing hourly load and generation data, simulating hourly system balance, modeling battery charging and discharging over time, calculating unmet demand and curtailment, computing cost metrics, searching across different solar/wind/storage combinations to identify feasible systems, generating visualizations, and building an interactive front end. These tasks are well suited to Python because they rely on time-series data, rule-based simulation, and repeated scenario testing. The necessary data can be referenced from a spreadsheet provided from ESPP90S, which shows grid data for the month of January, sourced from the Boston ISO. This could be expanded later with external load or generation datasets.
