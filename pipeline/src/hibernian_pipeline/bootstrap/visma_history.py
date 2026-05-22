from __future__ import annotations

from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json, write_json
from ..shared.legacy_format import TOTAL_STORE_NAME
from ..shared.legacy_format import normalize_text
from ..shared.legacy_format import parse_date
from ..shared.legacy_format import parse_number
from ..shared.legacy_format import parse_ratio
from ..shared.models import PipelineStep


def planned_outputs(config: PipelineConfig) -> dict[str, Path]:
    return {
        "historical_store_day": config.historical_store_day,
        "historical_seller_day": config.historical_seller_day,
    }


def describe_step(config: PipelineConfig) -> PipelineStep:
    outputs = planned_outputs(config)
    return PipelineStep(
        name="bootstrap_visma_history",
        description="Seed historical store and seller data from the frozen published history baseline.",
        inputs=(str(config.bootstrap_store_source), str(config.bootstrap_seller_source)),
        outputs=tuple(str(path) for path in outputs.values()),
    )


def _normalize_store_row(row: dict[str, Any]) -> dict[str, Any] | None:
    butikk = normalize_text(row.get("butikk"))
    if butikk == TOTAL_STORE_NAME:
        return None
    return {
        "fakturadato": parse_date(row.get("fakturadato")),
        "butikk": butikk,
        "Klient": str(row.get("Klient") or "").strip(),
        "mmoms": parse_number(row.get("mmoms")),
        "umoms": parse_number(row.get("umoms")),
        "db": parse_number(row.get("db")),
        "dg": parse_ratio(row.get("dg")),
        "antord": parse_number(row.get("antord")),
        "prord": parse_number(row.get("prord")),
    }


def _normalize_seller_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ukedag": normalize_text(row.get("ukedag")),
        "navn": normalize_text(row.get("navn")),
        "umoms": parse_number(row.get("umoms")),
        "db": parse_number(row.get("db")),
        "butikk": normalize_text(row.get("butikk")),
        "fakturadato": parse_date(row.get("fakturadato")),
    }


def run(config: PipelineConfig) -> dict[str, int]:
    store_source = read_json(config.bootstrap_store_source)
    seller_source = read_json(config.bootstrap_seller_source)

    historical_store = [row for row in (_normalize_store_row(item) for item in store_source) if row is not None]
    historical_seller = [_normalize_seller_row(item) for item in seller_source]

    write_json(config.historical_store_day, historical_store)
    write_json(config.historical_seller_day, historical_seller)

    return {
        "historical_store_rows": len(historical_store),
        "historical_seller_rows": len(historical_seller),
    }
