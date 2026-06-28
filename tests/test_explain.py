from datetime import date

from adptracker.dataset import EmploymentPoint
from adptracker.forecast import Forecast
from adptracker.explain import explain_forecast


def test_explanation_names_inputs_and_baseline_nature() -> None:
    forecast = Forecast(
        next_month=date(2026, 6, 1),
        latest=EmploymentPoint(date(2026, 5, 1), 132_624_000),
        projected_private_employment=132_700_000,
        projected_change=76_000,
        average_change_3m=96_000,
        average_change_6m=61_000,
        average_change_12m=51_000,
        observations=197,
    )

    explanation = explain_forecast(forecast)

    assert "May 2026" in explanation
    assert "June 2026" in explanation
    assert "weighted momentum model" in explanation
    assert "baseline" in explanation
