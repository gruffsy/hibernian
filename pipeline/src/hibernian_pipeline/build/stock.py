from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json, write_json
from ..shared.legacy_format import normalize_text
from ..shared.models import PipelineStep


def planned_inputs(config: PipelineConfig) -> list[Path]:
    return [config.stock_raw, config.orders_raw]


def planned_output(config: PipelineConfig) -> Path:
    return config.stock_publish


def describe_step(config: PipelineConfig) -> PipelineStep:
    return PipelineStep(
        name="build_stock",
        description="Merge stock balances and inbound orders into the published stock feed.",
        inputs=tuple(str(path) for path in planned_inputs(config)),
        outputs=(str(planned_output(config)),),
    )


def _normalize_stock_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "Prodno": normalize_text(row.get("Prodno")),
        "Beskrivelse": normalize_text(row.get("Beskrivelse")),
        "antall på lager": row.get("antall på lager", row.get("antall pÃ¥ lager", 0)),
        "antall pr pall": row.get("antall pr pall", 0),
        "Paller på lager": row.get("Paller på lager", row.get("Paller pÃ¥ lager", 0)),
        "Paller på vei": row.get("Paller på vei", row.get("Paller pÃ¥ vei", 0)),
    }


def _normalize_order_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "Prodno": normalize_text(row.get("Prodno")),
        "Descr": normalize_text(row.get("Descr")),
        "NoInvoAb": row.get("NoInvoAb", 0),
        "Week_Year": normalize_text(row.get("Week_Year")),
    }


def build_stock_payload(
    stock_rows: list[dict[str, Any]],
    order_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged = {normalize_text(row.get("Prodno")): _normalize_stock_row(row) for row in stock_rows}
    orders_by_prodno: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in order_rows:
        normalized = _normalize_order_row(row)
        orders_by_prodno[normalized["Prodno"]].append(
            {
                "Ukenr": normalized["Week_Year"] or "ukjent",
                "Antall": normalized["NoInvoAb"] or 0,
            }
        )

    payload: list[dict[str, Any]] = []
    for prodno in sorted(merged):
        row = dict(merged[prodno])
        orders = orders_by_prodno.get(prodno)
        if orders:
            row["Bestilling på vei"] = orders
        payload.append(row)

    return payload


def run(config: PipelineConfig) -> list[dict[str, Any]]:
    stock_rows = read_json(config.stock_raw) if config.stock_raw.exists() else []
    order_rows = read_json(config.orders_raw) if config.orders_raw.exists() else []
    payload = build_stock_payload(stock_rows, order_rows)
    write_json(planned_output(config), payload)
    return payload
