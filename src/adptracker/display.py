from __future__ import annotations

from .backtest import BacktestResult
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


def render_backtest(result: BacktestResult) -> str:
    return "\n".join(
        [
            "Backtest",
            "--------",
            f"Observations:       {result.observations:,}",
            f"Test periods:       {result.test_periods:,}",
            f"First test month:   {result.first_test_month:%Y-%m-%d}",
            f"Last test month:    {result.last_test_month:%Y-%m-%d}",
            f"MAE:                {result.mean_absolute_error_thousands:,.1f} thousand jobs",
        ]
    )
