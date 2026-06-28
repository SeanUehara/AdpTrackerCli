from datetime import date

from adptracker.dataset import EmploymentPoint
from adptracker.forecast import forecast_next_month


def test_forecast_uses_weighted_recent_changes() -> None:
    points = [
        EmploymentPoint(date(2025, month, 1), 100_000_000 + (month * 10_000))
        for month in range(1, 13)
    ]
    points.append(EmploymentPoint(date(2026, 1, 1), 100_130_000))

    forecast = forecast_next_month(points)

    assert forecast.next_month == date(2026, 2, 1)
    assert forecast.projected_change == 10_000
    assert forecast.projected_private_employment == 100_140_000
