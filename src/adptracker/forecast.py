from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .dataset import EmploymentPoint


@dataclass(frozen=True)
class Forecast:
    next_month: date
    latest: EmploymentPoint
    projected_private_employment: int
    projected_change: int
    average_change_3m: float
    average_change_6m: float
    average_change_12m: float
    observations: int

    @property
    def projected_private_employment_millions(self) -> float:
        return self.projected_private_employment / 1_000_000


def forecast_next_month(points: list[EmploymentPoint]) -> Forecast:
    ordered = sorted(points)
    if len(ordered) < 13:
        raise ValueError("At least 13 monthly observations are required for a forecast")

    latest = ordered[-1]
    changes = [
        current.private_employment - previous.private_employment
        for previous, current in zip(ordered, ordered[1:])
    ]

    avg_3 = _average(changes[-3:])
    avg_6 = _average(changes[-6:])
    avg_12 = _average(changes[-12:])
    projected_change = round((0.50 * avg_3) + (0.30 * avg_6) + (0.20 * avg_12))
    projected_value = latest.private_employment + projected_change

    return Forecast(
        next_month=_add_one_month(latest.date),
        latest=latest,
        projected_private_employment=projected_value,
        projected_change=projected_change,
        average_change_3m=avg_3,
        average_change_6m=avg_6,
        average_change_12m=avg_12,
        observations=len(ordered),
    )


def _average(values: list[int]) -> float:
    if not values:
        raise ValueError("Cannot average an empty series")
    return sum(values) / len(values)


def _add_one_month(value: date) -> date:
    year = value.year + (1 if value.month == 12 else 0)
    month = 1 if value.month == 12 else value.month + 1
    return value.replace(year=year, month=month)
