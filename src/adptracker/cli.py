from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .backtest import backtest_forecast
from .config import (
    ADP_PRODUCTION_JSON_URL,
    DEFAULT_CACHE_PATH,
    DEFAULT_HISTORY_PATH,
)
from .dataset import load_points
from .display import render_backtest, render_forecast, render_history
from .explain import explain_forecast
from .fetch import fetch_national_csv, sync_latest_national_csv
from .forecast import forecast_next_month


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adptracker",
        description="Fetch, view, and forecast ADP national private employment data.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch_parser = subparsers.add_parser("fetch", help="Download ADP national CSV data.")
    fetch_parser.add_argument(
        "--metadata-url",
        default=ADP_PRODUCTION_JSON_URL,
        help="ADP production metadata URL used to discover the latest release.",
    )
    fetch_parser.add_argument(
        "--url",
        default=None,
        help="Manual CSV URL override. When set, release-id checking is skipped.",
    )
    fetch_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_CACHE_PATH,
        help="Destination path for downloaded CSV.",
    )

    history_parser = subparsers.add_parser("history", help="Show historical values.")
    _add_data_argument(history_parser)
    history_parser.add_argument("--last", type=int, default=12, help="Number of rows to show.")

    forecast_parser = subparsers.add_parser(
        "forecast", help="Forecast next month's national employment."
    )
    _add_data_argument(forecast_parser)

    explain_parser = subparsers.add_parser("explain", help="Explain the next-month forecast.")
    _add_data_argument(explain_parser)

    backtest_parser = subparsers.add_parser(
        "backtest", help="Backtest the next-month forecast and report MAE."
    )
    _add_data_argument(backtest_parser)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "fetch":
            if args.url:
                path = fetch_national_csv(args.url, args.output)
                print(f"Downloaded ADP national data to {path}")
                return 0

            result = sync_latest_national_csv(
                metadata_url=args.metadata_url,
                output_path=args.output,
            )
            print(result.message)
            return 0

        points = load_points(_resolve_data_path(args.data))

        if args.command == "history":
            if args.last < 1:
                parser.error("--last must be at least 1")
            print(render_history(points, args.last))
            return 0

        if args.command == "backtest":
            print(render_backtest(backtest_forecast(points)))
            return 0

        forecast = forecast_next_month(points)

        if args.command == "forecast":
            print(render_forecast(forecast))
            return 0

        if args.command == "explain":
            print(explain_forecast(forecast))
            return 0
    except OSError as exc:
        print(f"adptracker: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"adptracker: {exc}", file=sys.stderr)
        return 2

    parser.error(f"Unknown command: {args.command}")
    return 2


def _resolve_data_path(path: Path | None) -> Path:
    if path is not None:
        return path
    if DEFAULT_CACHE_PATH.exists():
        return DEFAULT_CACHE_PATH
    return DEFAULT_HISTORY_PATH


def _add_data_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="CSV path to read. Defaults to downloaded cache, then bundled history.",
    )
