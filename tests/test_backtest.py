from datetime import date

import pytest

from adptracker.backtest import backtest_forecast
from adptracker.dataset import EmploymentPoint


def test_backtest_reports_mae_in_thousands() -> None:
    points = [
        EmploymentPoint(month, 100_000_000 + (index * 10_000))
        for index, month in enumerate(_month_starts(2025, 1, 13))
    ]
    points.append(EmploymentPoint(date(2026, 2, 1), 100_140_000))

    result = backtest_forecast(points)

    assert result.test_periods == 1
    assert result.mean_absolute_error == 10_000
    assert result.mean_absolute_error_thousands == 10


def test_backtest_requires_enough_history() -> None:
    points = [
        EmploymentPoint(month, 100_000_000 + (index * 10_000))
        for index, month in enumerate(_month_starts(2025, 1, 13))
    ]

    with pytest.raises(ValueError, match="At least 14"):
        backtest_forecast(points)


def _month_starts(year: int, month: int, count: int) -> list[date]:
    months: list[date] = []
    current_year = year
    current_month = month

    for _ in range(count):
        months.append(date(current_year, current_month, 1))
        current_month += 1
        if current_month == 13:
            current_year += 1
            current_month = 1

    return months
