# ADP Tracker CLI

CLI for ADP National Employment Report data. It can fetch the
official national private-employment CSV, show historical values, forecast next
month, and explain the forecast inputs.

The first version uses only the Python standard library at runtime.

## Install for local development

```powershell
python -m pip install -e .
```

## Commands

Download the national ADP artifact:

```powershell
python -m adptracker fetch
```

Show the latest 12 monthly national values from the local data:

```powershell
python -m adptracker history --last 12
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



## Approach and the key tradeoffs you made

I focused on building a simple, maintainable CLI that supports the required commands and uses a lightweight forecasting model to predict next month's national private employment. One key tradeoff was fetching the latest CSV directly from the ADP website instead of implementing an email subscription workflow, which kept the solution simpler while still providing current data. Another tradeoff was prioritizing code quality, readability, and testing over adding additional features, ensuring the core functionality was reliable before expanding the project's scope.


## How you evaluated forecast accuracy and what the results were

I evaluated the forecasting model using Mean Absolute Error (MAE) with a simple backtesting approach. I chose MAE because it is easy to interpret, well-suited for this use case, and can be implemented using only Python's standard library. The model achieved a Mean Absolute Error of approximately 115.5 thousand jobs.


## What you'd build next if you had another week

I would expand the CLI to support forecasting for the Industry, Establishment Size, and Region datasets in addition to the national report. I would also replace direct CSV downloads with an email subscription workflow to automatically retrieve newly released ADP data. Finally, I would implement and compare additional forecasting models with more comprehensive backtesting to improve forecast accuracy and evaluate model performance.
