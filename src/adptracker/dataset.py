from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True, order=True)
class EmploymentPoint:
    date: date
    private_employment: int

    @property
    def private_employment_millions(self) -> float:
        return self.private_employment / 1_000_000


def load_points(path: Path | str) -> list[EmploymentPoint]:
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    if not reader.fieldnames:
        raise ValueError(f"{csv_path} does not contain a CSV header")

    points = _parse_rows(rows, reader.fieldnames)
    if not points:
        raise ValueError(f"{csv_path} does not contain national monthly employment data")

    return sorted(points)


def latest_point(points: Iterable[EmploymentPoint]) -> EmploymentPoint:
    ordered = sorted(points)
    if not ordered:
        raise ValueError("No employment points available")
    return ordered[-1]


def _parse_rows(rows: list[dict[str, str]], fieldnames: list[str]) -> list[EmploymentPoint]:
    if {"date", "Private Employment"}.issubset(fieldnames):
        return [_point_from_values(row["date"], row["Private Employment"]) for row in rows]

    if {"timestep", "agg_RIS", "category", "date", "NER_SA"}.issubset(fieldnames):
        return [
            _point_from_values(row["date"], row["NER_SA"])
            for row in rows
            if row.get("timestep") == "M"
            and row.get("agg_RIS") == "National"
            and row.get("category") == "U.S."
        ]

    raise ValueError(
        "Unsupported CSV format. Expected ADP national artifact columns "
        "or ADP history columns."
    )


def _point_from_values(raw_date: str, raw_value: str) -> EmploymentPoint:
    parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    value = int(round(float(raw_value)))
    return EmploymentPoint(parsed_date, value)
