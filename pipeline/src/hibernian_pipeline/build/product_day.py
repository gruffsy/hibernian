from __future__ import annotations

from collections import defaultdict
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
        description="Merge product history and NAV refresh rows into the published product feed.",
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


def _row_key(row: dict[str, Any]) -> tuple[int, str]:
    return row["fakturadato"], row["Item No_"]


def _sort_key(row: dict[str, Any]) -> tuple[int, float, str]:
    return (-row["fakturadato"], -row["umoms"], row["Item No_"])


def _load_base_source_rows(config: PipelineConfig) -> list[dict[str, Any]]:
    if config.product_history_base_snapshot and config.product_history_base_snapshot.exists():
        return read_json(config.product_history_base_snapshot)
    if config.product_history_publish and config.product_history_publish.exists():
        return read_json(config.product_history_publish)
    return []


def _merge_rows(historical_rows: list[dict[str, Any]], nav_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[int, str], dict[str, Any]] = {}

    for row in historical_rows:
        normalized = _normalize_row(row)
        merged[_row_key(normalized)] = normalized

    for row in nav_rows:
        normalized = _normalize_row(row)
        merged[_row_key(normalized)] = normalized

    return list(merged.values())


def build_base_snapshot_rows(historical_rows: list[dict[str, Any]], *, window_start_date: int) -> list[dict[str, Any]]:
    normalized = [_normalize_row(row) for row in historical_rows]
    return filter_rows_before_date(normalized, field_name="fakturadato", start_date=window_start_date)


def build_product_day_payload(base_rows: list[dict[str, Any]], nav_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged_rows = _merge_rows(base_rows, nav_rows)
    merged_rows.sort(key=_sort_key)
    return merged_rows


def run(config: PipelineConfig) -> list[dict[str, Any]]:
    historical_rows = _load_base_source_rows(config)
    nav_rows = read_json(config.nav_product_day_raw) if config.nav_product_day_raw and config.nav_product_day_raw.exists() else []
    window_start_date = compute_window_start_date(trailing_refresh_days=config.product_refresh_days)
    base_rows = build_base_snapshot_rows(historical_rows, window_start_date=window_start_date)
    payload = build_product_day_payload(base_rows, nav_rows)
    if config.product_day_publish:
        write_json(planned_output(config), payload)
    return payload
