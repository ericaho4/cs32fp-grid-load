import matplotlib.pyplot as plt


def format_x_axis_midnight_noon(datetimes):
    """
    Show x-axis labels only at midnight and noon, like the spreadsheet.
    """
    ticks = []
    labels = []

    for dt in datetimes:
        if dt.hour == 0:
            ticks.append(dt)
            labels.append(dt.strftime("%m-%d 12AM"))
        elif dt.hour == 12:
            ticks.append(dt)
            labels.append(dt.strftime("%m-%d 12PM"))

    return ticks, labels


def plot_generation(datetimes, load_vals, solar_vals, wind_vals, baseload_vals, period_label):
    """
    Return a matplotlib figure for load, solar, wind, and baseload over time.
    """
    fig, ax = plt.subplots(figsize=(16, 6))

    ax.plot(datetimes, load_vals, label="Load")
    ax.plot(datetimes, solar_vals, label="Solar")
    ax.plot(datetimes, wind_vals, label="Wind")

    if baseload_vals is not None:
        ax.plot(datetimes, baseload_vals, label="Baseload")

    ticks, labels = format_x_axis_midnight_noon(datetimes)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45, fontsize=6)

    ax.set_title(f"Load and Generation: {period_label}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Power (W)")
    ax.legend()

    fig.tight_layout()
    return fig


def plot_battery(datetimes, battery_trace, period_label):
    """
    Return a matplotlib figure for battery storage over time.
    """
    fig, ax = plt.subplots(figsize=(16, 5))

    ax.plot(datetimes, battery_trace, label="Battery Storage")

    ticks, labels = format_x_axis_midnight_noon(datetimes)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, rotation=45, fontsize=6)

    ax.set_title(f"Battery Storage Over Time: {period_label}")
    ax.set_xlabel("Time")
    ax.set_ylabel("Battery Level (Wh)")
    ax.legend()

    fig.tight_layout()
    return fig
