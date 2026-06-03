from __future__ import annotations

from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json
from ..shared.io import write_json
from ..shared.legacy_format import normalize_text
from ..shared.legacy_format import parse_date
from ..shared.legacy_format import parse_number
from ..shared.legacy_format import parse_ratio
from ..shared.models import PipelineStep
from ..shared.sql import run_nav_query
from ..shared.sql import to_sql_date
from ..shared.window import compute_window_start_date


def planned_outputs(config: PipelineConfig) -> dict[str, Path]:
    return {
        "product_history_base_snapshot": config.product_history_base_snapshot,
        "product_history_publish": config.product_history_publish,
    }


def describe_step(config: PipelineConfig) -> PipelineStep:
    outputs = planned_outputs(config)
    return PipelineStep(
        name="bootstrap_product_history",
        description="Seed the product history snapshot from NAV SQL starting at 2025-01-01.",
        inputs=(str(config.nav_product_sql_file),),
        outputs=tuple(str(path) for path in outputs.values()),
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


def _load_existing_rows(config: PipelineConfig) -> list[dict[str, Any]]:
    if config.product_history_base_snapshot and config.product_history_base_snapshot.exists():
        return read_json(config.product_history_base_snapshot)
    if config.product_history_publish and config.product_history_publish.exists():
        return read_json(config.product_history_publish)
    return []


def _query_bootstrap_rows(config: PipelineConfig, *, window_start_date: int) -> list[dict[str, Any]]:
    return run_nav_query(
        config,
        sql_file=config.nav_product_sql_file,
        parameters=(to_sql_date(config.product_backfill_start_date), to_sql_date(window_start_date)),
    )


def run(config: PipelineConfig) -> dict[str, Any]:
    existing_rows = _load_existing_rows(config)
    if existing_rows:
        if config.product_history_base_snapshot and not config.product_history_base_snapshot.exists():
            write_json(config.product_history_base_snapshot, existing_rows)
        if config.product_history_publish and not config.product_history_publish.exists():
            write_json(config.product_history_publish, existing_rows)
        return {
            "status": "skipped",
            "product_rows": len(existing_rows),
            "window_start_date": compute_window_start_date(trailing_refresh_days=config.product_refresh_days),
        }

    window_start_date = compute_window_start_date(trailing_refresh_days=config.product_refresh_days)
    rows = _query_bootstrap_rows(config, window_start_date=window_start_date)
    payload = [_normalize_row(row) for row in rows]

    if config.product_history_base_snapshot:
        write_json(config.product_history_base_snapshot, payload)
    if config.product_history_publish:
        write_json(config.product_history_publish, payload)

    return {
        "status": "bootstrapped",
        "product_rows": len(payload),
        "window_start_date": window_start_date,
        "source_start_date": config.product_backfill_start_date,
    }
