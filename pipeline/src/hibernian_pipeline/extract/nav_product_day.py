from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import write_json
from ..shared.legacy_format import normalize_text
from ..shared.legacy_format import parse_date
from ..shared.legacy_format import parse_number
from ..shared.legacy_format import parse_ratio
from ..shared.models import PipelineStep
from ..shared.sql import run_nav_query
from ..shared.sql import to_sql_date
from ..shared.window import compute_window_start_date


def planned_output(config: PipelineConfig) -> Path:
    return config.nav_product_day_raw


def describe_step(config: PipelineConfig) -> PipelineStep:
    return PipelineStep(
        name="extract_nav_product_day",
        description="Extract daily product sales from NAV SQL into the product refresh window.",
        inputs=(str(config.nav_product_sql_file),),
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


def run(config: PipelineConfig) -> list[dict[str, Any]]:
    window_start_date = compute_window_start_date(trailing_refresh_days=config.product_refresh_days)
    window_end_date = int((datetime.now().date() + timedelta(days=1)).strftime("%Y%m%d"))
    rows = run_nav_query(
        config,
        sql_file=config.nav_product_sql_file,
        parameters=(to_sql_date(window_start_date), to_sql_date(window_end_date)),
    )
    payload = [_normalize_row(row) for row in rows]
    write_json(planned_output(config), payload)
    return payload
