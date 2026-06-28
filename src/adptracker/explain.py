from __future__ import annotations

from .forecast import Forecast


def explain_forecast(forecast: Forecast) -> str:
    latest = forecast.latest
    direction = "increase" if forecast.projected_change >= 0 else "decrease"

    return (
        f"The latest national private employment value is "
        f"{_millions(latest.private_employment)} million for {latest.date:%B %Y}. "
        f"The forecast projects {_millions(forecast.projected_private_employment)} "
        f"million for {forecast.next_month:%B %Y}, a {_abs_thousands(forecast.projected_change)} "
        f"thousand {direction}. The estimate uses a transparent weighted momentum model: "
        f"50% of the last 3-month average change ({_signed_thousands(forecast.average_change_3m)}k), "
        f"30% of the last 6-month average change ({_signed_thousands(forecast.average_change_6m)}k), "
        f"and 20% of the last 12-month average change ({_signed_thousands(forecast.average_change_12m)}k). "
        f"It is based on {forecast.observations} monthly observations and should be read as a simple "
        f"baseline, not a statistical confidence interval."
    )


def _millions(value: int | float) -> str:
    return f"{value / 1_000_000:.3f}"


def _signed_thousands(value: int | float) -> str:
    return f"{value / 1_000:+.1f}"


def _abs_thousands(value: int | float) -> str:
    return f"{abs(value) / 1_000:.1f}"
