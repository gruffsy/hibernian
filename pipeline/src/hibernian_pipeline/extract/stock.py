from __future__ import annotations

from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json, write_json
from ..shared.legacy_format import normalize_text
from ..shared.models import PipelineStep


def planned_outputs(config: PipelineConfig) -> dict[str, Path]:
    return {
        "stock_raw": config.stock_raw,
        "orders_raw": config.orders_raw,
    }


def describe_step(config: PipelineConfig) -> PipelineStep:
    outputs = planned_outputs(config)
    return PipelineStep(
        name="extract_stock",
        description="Extract raw stock balances and inbound orders.",
        inputs=(str(config.stock_source), str(config.orders_source)),
        outputs=tuple(str(path) for path in outputs.values()),
    )


def _normalize_stock_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "Prodno": normalize_text(row.get("Prodno")),
        "Beskrivelse": normalize_text(row.get("Beskrivelse")),
        "antall på lager": row.get("antall på lager", 0),
        "antall pr pall": row.get("antall pr pall", 0),
        "Paller på lager": row.get("Paller på lager", 0),
        "Paller på vei": row.get("Paller på vei", 0),
    }


def _normalize_order_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "Prodno": normalize_text(row.get("Prodno")),
        "Descr": normalize_text(row.get("Descr")),
        "NoInvoAb": row.get("NoInvoAb", 0),
        "Week_Year": normalize_text(row.get("Week_Year")),
    }


def run(config: PipelineConfig) -> dict[str, int]:
    stock_rows = read_json(config.stock_source)
    order_rows = read_json(config.orders_source)

    normalized_stock = [_normalize_stock_row(row) for row in stock_rows]
    normalized_orders = [_normalize_order_row(row) for row in order_rows]

    write_json(config.stock_raw, normalized_stock)
    write_json(config.orders_raw, normalized_orders)

    return {
        "stock_rows": len(normalized_stock),
        "orders_rows": len(normalized_orders),
    }
