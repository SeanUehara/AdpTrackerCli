# ADP Tracker CLI

Small Python CLI for ADP National Employment Report data. It can fetch the
official national private-employment CSV, show historical values, forecast next
month, and explain the forecast inputs.

The first version uses only the Python standard library at runtime.

## Install for local development

```powershell
python -m pip install -e .
```

## Commands

Show the latest 12 monthly national values from the local data:

```powershell
python -m adptracker history --last 12
```

Download the national ADP artifact:

```powershell
python -m adptracker fetch
```

Forecast the next month:

```powershell
python -m adptracker forecast
```

Explain the forecast:

```powershell
python -m adptracker explain
```

## Forecast Method

The forecast is a transparent momentum baseline:

```text
forecast_change =
  0.50 * avg_change_last_3_months +
  0.30 * avg_change_last_6_months +
  0.20 * avg_change_last_12_months
```

The projected employment level is the latest monthly value plus that weighted
change. This is intentionally simple and explainable; it is not a confidence
interval or a full econometric model.
