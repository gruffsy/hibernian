from __future__ import annotations

from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json, write_json
from ..shared.legacy_format import normalize_text
from ..shared.legacy_format import parse_date
from ..shared.legacy_format import parse_number
from ..shared.legacy_format import parse_ratio
from ..shared.models import PipelineStep
from ..shared.sql import run_nav_query
from ..shared.sql import to_sql_date
from ..shared.window import compute_extract_start_date
from ..shared.window import filter_rows_on_or_after_date


def planned_output(config: PipelineConfig) -> Path:
    return config.nav_store_day_raw


def describe_step(config: PipelineConfig) -> PipelineStep:
    return PipelineStep(
        name="extract_nav_store_day",
        description="Extract daily store sales from NAV SQL into a trailing-window raw artifact.",
        inputs=(str(config.nav_store_sql_file),),
        outputs=(str(planned_output(config)),),
    )


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "fakturadato": parse_date(row.get("fakturadato")),
        "butikk": normalize_text(row.get("butikk")),
        "Klient": str(row.get("Klient") or "").strip(),
        "mmoms": parse_number(row.get("mmoms")),
        "umoms": parse_number(row.get("umoms")),
        "db": parse_number(row.get("db")),
        "dg": parse_ratio(row.get("dg")),
        "antord": parse_number(row.get("antord")),
        "prord": parse_number(row.get("prord")),
    }


def run(config: PipelineConfig) -> list[dict[str, Any]]:
    existing_rows = _load_existing_rows(config)
    window_start_date = compute_extract_start_date(
        trailing_refresh_days=config.trailing_refresh_days,
        existing_rows=existing_rows,
        field_name="fakturadato",
    )
    rows = _load_rows(config, window_start_date=window_start_date)
    payload = [_normalize_row(row) for row in rows]
    write_json(planned_output(config), payload)
    return payload


def _load_existing_rows(config: PipelineConfig) -> list[dict[str, Any]]:
    if config.store_day_publish.exists():
      return read_json(config.store_day_publish)
    if config.historical_store_day.exists():
      return read_json(config.historical_store_day)
    return []


def _load_rows(config: PipelineConfig, *, window_start_date: int) -> list[dict[str, Any]]:
    try:
        return run_nav_query(
            config,
            sql_file=config.nav_store_sql_file,
            parameters=(to_sql_date(window_start_date),),
        )
    except RuntimeError:
        rows = read_json(config.nav_store_source)
        return filter_rows_on_or_after_date(rows, field_name="fakturadato", start_date=window_start_date)
