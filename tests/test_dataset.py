from pathlib import Path

from adptracker.dataset import load_points


def test_loads_official_national_artifact(tmp_path: Path) -> None:
    csv_path = tmp_path / "line_national.csv"
    csv_path.write_text(
        "date,Private Employment\n"
        "2026-04-01,132502000.0\n"
        "2026-05-01,132624000.0\n",
        encoding="utf-8",
    )

    points = load_points(csv_path)

    assert len(points) == 2
    assert points[-1].private_employment == 132_624_000


def test_loads_monthly_national_rows_from_history_format(tmp_path: Path) -> None:
    csv_path = tmp_path / "history.csv"
    csv_path.write_text(
        "timestep,agg_RIS,category,date,NER,NER_SA\n"
        "M,Census Divisions,East North Central,2026-01-01,1.0,2.0\n"
        "W,National,U.S.,2026-01-03,10.0,11.0\n"
        "M,National,U.S.,2026-01-01,132270000.0,132270000.0\n"
        "M,National,U.S.,2026-02-01,132336000.0,132336000.0\n",
        encoding="utf-8",
    )

    points = load_points(csv_path)

    assert [point.private_employment for point in points] == [132_270_000, 132_336_000]
