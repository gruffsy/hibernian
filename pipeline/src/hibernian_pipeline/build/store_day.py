from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from ..settings import PipelineConfig
from ..shared.io import read_json, write_json
from ..shared.legacy_format import TOTAL_CLIENT
from ..shared.legacy_format import TOTAL_STORE_NAME
from ..shared.legacy_format import format_currency
from ..shared.legacy_format import format_integer
from ..shared.legacy_format import format_percentage
from ..shared.legacy_format import normalize_text
from ..shared.legacy_format import parse_date
from ..shared.legacy_format import parse_number
from ..shared.legacy_format import parse_ratio
from ..shared.models import PipelineStep
from ..shared.window import compute_window_start_date
from ..shared.window import filter_rows_before_date


def planned_inputs(config: PipelineConfig) -> list[Path]:
    return [config.historical_store_day, config.nav_store_day_raw]


def planned_output(config: PipelineConfig) -> Path:
    return config.store_day_publish


def _load_base_source_rows(config: PipelineConfig) -> list[dict[str, Any]]:
    if config.store_day_publish.exists():
        return read_json(config.store_day_publish)
    if config.historical_store_day.exists():
        return read_json(config.historical_store_day)
    return []


def describe_step(config: PipelineConfig) -> PipelineStep:
    return PipelineStep(
        name="build_store_day",
        description="Merge historical and NAV store sales into the published daily store feed.",
        inputs=tuple(str(path) for path in planned_inputs(config)),
        outputs=(str(planned_output(config)),),
    )


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    fakturadato = parse_date(row.get("fakturadato"))
    butikk = normalize_text(row.get("butikk"))
    klient = str(row.get("Klient") or "").strip()

    mmoms = parse_number(row.get("mmoms"))
    umoms = parse_number(row.get("umoms"))
    db = parse_number(row.get("db"))
    dg = parse_ratio(row.get("dg"))
    antord = parse_number(row.get("antord"))
    prord = parse_number(row.get("prord"))

    if not dg and umoms:
        dg = db / umoms
    if not prord and antord:
        prord = mmoms / antord

    return {
        "fakturadato": fakturadato,
        "butikk": butikk,
        "Klient": klient,
        "mmoms": mmoms,
        "umoms": umoms,
        "db": db,
        "dg": dg,
        "antord": antord,
        "prord": prord,
    }


def _row_key(row: dict[str, Any]) -> tuple[int, str]:
    client = str(row.get("Klient") or "").strip()
    store = normalize_text(row.get("butikk"))
    identity = client or store
    return row["fakturadato"], identity


def _sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
    client = str(row.get("Klient") or "0").strip()
    client_value = int(client) if client.isdigit() else 999
    return (-row["fakturadato"], client_value, row["butikk"])


def _merge_rows(historical_rows: list[dict[str, Any]], nav_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[tuple[int, str], dict[str, Any]] = {}

    for row in historical_rows:
        normalized = _normalize_row(row)
        if normalized["butikk"] == TOTAL_STORE_NAME:
            continue
        merged[_row_key(normalized)] = normalized

    for row in nav_rows:
        normalized = _normalize_row(row)
        if normalized["butikk"] == TOTAL_STORE_NAME:
            continue
        merged[_row_key(normalized)] = normalized

    return list(merged.values())


def _append_totals(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    totals_by_date: dict[int, dict[str, float]] = defaultdict(
        lambda: {"mmoms": 0.0, "umoms": 0.0, "db": 0.0, "antord": 0.0}
    )

    for row in rows:
        bucket = totals_by_date[row["fakturadato"]]
        bucket["mmoms"] += row["mmoms"]
        bucket["umoms"] += row["umoms"]
        bucket["db"] += row["db"]
        bucket["antord"] += row["antord"]

    with_totals = list(rows)
    for fakturadato, totals in totals_by_date.items():
        antord = totals["antord"]
        umoms = totals["umoms"]
        mmoms = totals["mmoms"]
        db = totals["db"]
        with_totals.append(
            {
                "fakturadato": fakturadato,
                "butikk": TOTAL_STORE_NAME,
                "Klient": TOTAL_CLIENT,
                "mmoms": mmoms,
                "umoms": umoms,
                "db": db,
                "dg": (db / umoms) if umoms else 0.0,
                "antord": antord,
                "prord": (mmoms / antord) if antord else 0.0,
            }
        )

    return with_totals


def _format_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "fakturadato": row["fakturadato"],
        "butikk": row["butikk"],
        "Klient": int(row["Klient"]) if row["butikk"] == TOTAL_STORE_NAME and str(row["Klient"]).isdigit() else row["Klient"],
        "mmoms": format_currency(row["mmoms"]),
        "umoms": format_currency(row["umoms"]),
        "db": format_currency(row["db"]),
        "dg": format_percentage(row["dg"]),
        "antord": format_integer(row["antord"]),
        "prord": format_currency(row["prord"]),
    }


def build_base_snapshot_rows(
    historical_rows: list[dict[str, Any]],
    *,
    window_start_date: int,
) -> list[dict[str, Any]]:
    normalized = [_normalize_row(row) for row in historical_rows]
    normalized = [row for row in normalized if row["butikk"] != TOTAL_STORE_NAME]
    return filter_rows_before_date(normalized, field_name="fakturadato", start_date=window_start_date)


def build_store_day_payload(
    base_rows: list[dict[str, Any]],
    nav_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged_rows = _merge_rows(base_rows, nav_rows)
    rows_with_totals = _append_totals(merged_rows)
    rows_with_totals.sort(key=_sort_key)
    return [_format_row(row) for row in rows_with_totals]


def run(config: PipelineConfig) -> list[dict[str, Any]]:
    historical_rows = _load_base_source_rows(config)
    nav_rows = read_json(config.nav_store_day_raw) if config.nav_store_day_raw.exists() else []
    window_start_date = compute_window_start_date(trailing_refresh_days=config.trailing_refresh_days)
    base_rows = build_base_snapshot_rows(historical_rows, window_start_date=window_start_date)
    write_json(config.store_day_base_snapshot, [_format_row(row) for row in sorted(base_rows, key=_sort_key)])
    payload = build_store_day_payload(base_rows, nav_rows)
    write_json(planned_output(config), payload)
    return payload
