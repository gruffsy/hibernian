from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json
from ..shared.io import write_json
from ..shared.legacy_format import parse_date
from ..shared.legacy_format import parse_number
from ..shared.legacy_format import parse_ratio
from ..shared.legacy_format import normalize_text
from ..shared.models import PipelineStep
from ..shared.window import compute_window_start_date
from ..shared.window import filter_rows_before_date


def planned_inputs(config: PipelineConfig) -> list[Path]:
    return [
        config.product_history_base_snapshot,
        config.nav_product_day_raw,
    ]


def planned_output(config: PipelineConfig) -> Path:
    return config.product_day_publish


def describe_step(config: PipelineConfig) -> PipelineStep:
    return PipelineStep(
        name="build_product_day",
        description="Build compact product period summaries from history and NAV refresh rows.",
        inputs=tuple(str(path) for path in planned_inputs(config)),
        outputs=(str(planned_output(config)),),
    )


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "Item No_": normalize_text(row.get("Item No_")),
        "Description": normalize_text(row.get("Description")),
        "Item Category": normalize_text(row.get("Item Category")),
        "Retail Product Group": normalize_text(row.get("Retail Product Group")),
        "fakturadato": parse_date(row.get("fakturadato")),
        "antall": parse_number(row.get("antall")),
        "umoms": parse_number(row.get("umoms")),
        "db": parse_number(row.get("db")),
        "dg": parse_ratio(row.get("dg")),
    }


def _period_keys(date_key: int) -> dict[str, str]:
    raw = str(int(date_key))
    year = int(raw[:4])
    month = int(raw[4:6])
    day = int(raw[6:8])
    current = date(year, month, day)
    iso = current.isocalendar()
    return {
        "day": raw,
        "week": f"{iso.year}-W{iso.week:02d}",
        "month": f"{year}-{month:02d}",
        "year": str(year),
    }


def _empty_totals() -> dict[str, float]:
    return {
        "antall": 0.0,
        "umoms": 0.0,
        "db": 0.0,
    }


def _finalize_totals(totals: dict[str, float]) -> dict[str, float]:
    umoms = totals["umoms"]
    db = totals["db"]
    return {
        "antall": totals["antall"],
        "umoms": umoms,
        "db": db,
        "dg": round(db / umoms, 4) if umoms else 0.0,
    }


def _create_product_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "Item No_": row["Item No_"],
        "Description": row["Description"],
        "Item Category": row["Item Category"],
        "Retail Product Group": row["Retail Product Group"],
        "antall": 0.0,
        "umoms": 0.0,
        "db": 0.0,
    }


def _merge_metadata(target: dict[str, Any], source: dict[str, Any]) -> None:
    for key in ("Description", "Item Category", "Retail Product Group"):
        if not target.get(key) and source.get(key):
            target[key] = source[key]


def _sort_rows(rows: list[dict[str, Any]], metric: str) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            -row.get(metric, 0.0),
            row.get("Description", ""),
            row.get("Item No_", ""),
        ),
    )[:20]


def _load_base_source_rows(config: PipelineConfig) -> list[dict[str, Any]]:
    if config.product_history_base_snapshot and config.product_history_base_snapshot.exists():
        return read_json(config.product_history_base_snapshot)
    if config.product_history_publish and config.product_history_publish.exists():
        return read_json(config.product_history_publish)
    return []


def _finalize_row(row: dict[str, Any]) -> dict[str, Any]:
    umoms = row["umoms"]
    db = row["db"]
    return {
        **row,
        "dg": round(db / umoms, 4) if umoms else 0.0,
    }


def _build_summary_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    available_dates: set[int] = set()
    available_weeks: set[str] = set()
    available_months: set[str] = set()
    available_years: set[int] = set()
    period_buckets: dict[str, dict[str, dict[str, Any]]] = {
        "day": defaultdict(lambda: {"items": {}, "totals": _empty_totals()}),
        "week": defaultdict(lambda: {"items": {}, "totals": _empty_totals()}),
        "month": defaultdict(lambda: {"items": {}, "totals": _empty_totals()}),
        "year": defaultdict(lambda: {"items": {}, "totals": _empty_totals()}),
    }

    for row in rows:
        normalized = _normalize_row(row)
        date_key = normalized["fakturadato"]
        available_dates.add(date_key)

        keys = _period_keys(date_key)
        available_weeks.add(keys["week"])
        available_months.add(keys["month"])
        available_years.add(int(keys["year"]))

        for period_name, period_key in keys.items():
            bucket = period_buckets[period_name][period_key]
            bucket["totals"]["antall"] += normalized["antall"]
            bucket["totals"]["umoms"] += normalized["umoms"]
            bucket["totals"]["db"] += normalized["db"]

            item_key = normalized["Item No_"] or normalized["Description"] or "Ukjent"
            item_row = bucket["items"].get(item_key)
            if item_row is None:
                item_row = _create_product_row(normalized)
                bucket["items"][item_key] = item_row
            _merge_metadata(item_row, normalized)
            item_row["antall"] += normalized["antall"]
            item_row["umoms"] += normalized["umoms"]
            item_row["db"] += normalized["db"]

    payload_periods: dict[str, dict[str, Any]] = {}
    for period_name, period_map in period_buckets.items():
        period_payload: dict[str, Any] = {}
        for period_key, bucket in period_map.items():
            rows_for_period = [_finalize_row(row) for row in bucket["items"].values()]

            period_payload[period_key] = {
                "totals": _finalize_totals(bucket["totals"]),
                "metrics": {
                    "antall": _sort_rows(rows_for_period, "antall"),
                    "umoms": _sort_rows(rows_for_period, "umoms"),
                    "db": _sort_rows(rows_for_period, "db"),
                },
            }
        payload_periods[period_name] = period_payload

    return {
        "availableDates": sorted(available_dates, reverse=True),
        "availableWeeks": sorted(available_weeks, reverse=True),
        "availableMonths": sorted(available_months, reverse=True),
        "availableYears": sorted(available_years, reverse=True),
        "periods": payload_periods,
    }


def build_base_snapshot_rows(historical_rows: list[dict[str, Any]], *, window_start_date: int) -> list[dict[str, Any]]:
    normalized = [_normalize_row(row) for row in historical_rows]
    return filter_rows_before_date(normalized, field_name="fakturadato", start_date=window_start_date)


def build_product_day_payload(base_rows: list[dict[str, Any]], nav_rows: list[dict[str, Any]]) -> dict[str, Any]:
    merged_rows = [_normalize_row(row) for row in base_rows] + [_normalize_row(row) for row in nav_rows]
    return _build_summary_rows(merged_rows)


def run(config: PipelineConfig) -> dict[str, Any]:
    historical_rows = _load_base_source_rows(config)
    nav_rows = read_json(config.nav_product_day_raw) if config.nav_product_day_raw and config.nav_product_day_raw.exists() else []
    window_start_date = compute_window_start_date(trailing_refresh_days=config.product_refresh_days)
    base_rows = build_base_snapshot_rows(historical_rows, window_start_date=window_start_date)
    payload = build_product_day_payload(base_rows, nav_rows)
    if config.product_day_publish:
        write_json(planned_output(config), payload)
    return payload
