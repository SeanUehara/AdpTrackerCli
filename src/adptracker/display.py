from __future__ import annotations

from .dataset import EmploymentPoint
from .forecast import Forecast


def render_history(points: list[EmploymentPoint], limit: int) -> str:
    selected = sorted(points)[-limit:]
    lines = ["Date        Private Employment", "----------  ------------------"]
    lines.extend(
        f"{point.date:%Y-%m-%d}  {point.private_employment:>18,}"
        for point in selected
    )
    return "\n".join(lines)


def render_forecast(forecast: Forecast) -> str:
    return "\n".join(
        [
            "Forecast",
            "--------",
            f"Latest month:       {forecast.latest.date:%Y-%m-%d}",
            f"Latest employment:  {forecast.latest.private_employment:,}",
            f"Forecast month:     {forecast.next_month:%Y-%m-%d}",
            f"Forecast value:     {forecast.projected_private_employment:,}",
            f"Forecast change:    {forecast.projected_change:+,}",
        ]
    )
