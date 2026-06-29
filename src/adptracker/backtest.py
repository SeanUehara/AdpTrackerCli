from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .dataset import EmploymentPoint
from .forecast import forecast_next_month


@dataclass(frozen=True)
class BacktestResult:
    observations: int
    test_periods: int
    first_test_month: date
    last_test_month: date
    mean_absolute_error: float

    @property
    def mean_absolute_error_thousands(self) -> float:
        return self.mean_absolute_error / 1_000


def backtest_forecast(points: list[EmploymentPoint]) -> BacktestResult:
    ordered = sorted(points)
    if len(ordered) < 14:
        raise ValueError("At least 14 monthly observations are required for a backtest")

    absolute_errors: list[int] = []
    first_test_month: date | None = None
    last_test_month: date | None = None

    for target_index in range(13, len(ordered)):
        actual = ordered[target_index]
        forecast = forecast_next_month(ordered[:target_index])

        if forecast.next_month != actual.date:
            raise ValueError("Backtest requires consecutive monthly observations")

        absolute_errors.append(
            abs(forecast.projected_private_employment - actual.private_employment)
        )
        first_test_month = first_test_month or actual.date
        last_test_month = actual.date

    return BacktestResult(
        observations=len(ordered),
        test_periods=len(absolute_errors),
        first_test_month=_require_date(first_test_month),
        last_test_month=_require_date(last_test_month),
        mean_absolute_error=sum(absolute_errors) / len(absolute_errors),
    )


def _require_date(value: date | None) -> date:
    if value is None:
        raise ValueError("Backtest did not produce any test periods")
    return value
