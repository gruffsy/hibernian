from __future__ import annotations

from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json, write_json
from ..shared.legacy_format import normalize_text
from ..shared.legacy_format import parse_date
from ..shared.legacy_format import parse_number
from ..shared.models import PipelineStep


def planned_output(config: PipelineConfig) -> Path:
    return config.nav_seller_day_raw


def describe_step(config: PipelineConfig) -> PipelineStep:
    return PipelineStep(
        name="extract_nav_seller_day",
        description="Extract daily seller sales from NAV into a raw artifact.",
        inputs=(str(config.nav_seller_source),),
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


def run(config: PipelineConfig) -> list[dict[str, Any]]:
    rows = read_json(config.nav_seller_source)
    payload = [_normalize_row(row) for row in rows]
    write_json(planned_output(config), payload)
    return payload
