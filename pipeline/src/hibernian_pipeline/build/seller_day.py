from __future__ import annotations

from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json, write_json
from ..shared.legacy_format import format_currency
from ..shared.legacy_format import normalize_text
from ..shared.legacy_format import parse_date
from ..shared.legacy_format import parse_number
from ..shared.models import PipelineStep
from ..shared.window import compute_window_start_date
from ..shared.window import filter_rows_before_date


def planned_inputs(config: PipelineConfig) -> list[Path]:
    return [config.historical_seller_day, config.nav_seller_day_raw]


def planned_output(config: PipelineConfig) -> Path:
    return config.seller_day_publish


def _load_base_source_rows(config: PipelineConfig) -> list[dict[str, Any]]:
    if config.seller_day_publish.exists():
        return read_json(config.seller_day_publish)
    if config.historical_seller_day.exists():
        return read_json(config.historical_seller_day)
    return []


def describe_step(config: PipelineConfig) -> PipelineStep:
    return PipelineStep(
        name="build_seller_day",
        description="Merge historical and NAV seller sales into the published daily seller feed.",
        inputs=tuple(str(path) for path in planned_inputs(config)),
        outputs=(str(planned_output(config)),),
    )


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ukedag": normalize_text(row.get("ukedag")),
        "navn": normalize_text(row.get("navn")),
        "umoms": parse_number(row.get("umoms")),
        "db": parse_number(row.get("db")),
        "butikk": normalize_text(row.get("butikk")),
        "fakturadato": parse_date(row.get("fakturadato")),
    }


def _row_key(row: dict[str, Any]) -> tuple[int, str, str]:
    return row["fakturadato"], row["navn"], row["butikk"]


def _sort_key(row: dict[str, Any]) -> tuple[int, float, str]:
    return (-row["fakturadato"], -row["umoms"], row["navn"])


def _format_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ukedag": row["ukedag"],
        "navn": row["navn"],
        "umoms": format_currency(row["umoms"]),
        "db": format_currency(row["db"]),
        "butikk": row["butikk"],
        "fakturadato": row["fakturadato"],
    }


def build_base_snapshot_rows(
    historical_rows: list[dict[str, Any]],
    *,
    window_start_date: int,
) -> list[dict[str, Any]]:
    normalized = [_normalize_row(row) for row in historical_rows]
    return filter_rows_before_date(normalized, field_name="fakturadato", start_date=window_start_date)


def build_seller_day_payload(
    base_rows: list[dict[str, Any]],
    nav_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged: dict[tuple[int, str, str], dict[str, Any]] = {}

    for row in base_rows:
        merged[_row_key(row)] = row

    for row in nav_rows:
        normalized = _normalize_row(row)
        merged[_row_key(normalized)] = normalized

    payload = list(merged.values())
    payload.sort(key=_sort_key)
    return [_format_row(row) for row in payload]


def run(config: PipelineConfig) -> list[dict[str, Any]]:
    historical_rows = _load_base_source_rows(config)
    nav_rows = read_json(config.nav_seller_day_raw) if config.nav_seller_day_raw.exists() else []
    window_start_date = compute_window_start_date(trailing_refresh_days=config.trailing_refresh_days)
    base_rows = build_base_snapshot_rows(historical_rows, window_start_date=window_start_date)
    base_payload = [_format_row(row) for row in sorted(base_rows, key=_sort_key)]
    write_json(config.seller_day_base_snapshot, base_payload)
    payload = build_seller_day_payload(base_rows, nav_rows)
    write_json(planned_output(config), payload)
    return payload
