from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .io import read_json, write_json


@dataclass(frozen=True)
class RefreshState:
    trailing_refresh_days: int
    window_start_date: int | None = None
    last_success_at: str | None = None
    last_store_row_count: int | None = None
    last_seller_row_count: int | None = None
    last_stock_row_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_refresh_state(path: Path, *, trailing_refresh_days: int) -> RefreshState:
    if not path.exists():
        return RefreshState(trailing_refresh_days=trailing_refresh_days)

    payload = read_json(path)
    if isinstance(payload, list):
        payload = {}

    return RefreshState(
        trailing_refresh_days=int(payload.get("trailing_refresh_days", trailing_refresh_days)),
        window_start_date=_parse_int(payload.get("window_start_date")),
        last_success_at=_parse_text(payload.get("last_success_at")),
        last_store_row_count=_parse_int(payload.get("last_store_row_count")),
        last_seller_row_count=_parse_int(payload.get("last_seller_row_count")),
        last_stock_row_count=_parse_int(payload.get("last_stock_row_count")),
    )


def save_refresh_state(path: Path, state: RefreshState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path, state.to_dict())


def build_success_state(
    *,
    trailing_refresh_days: int,
    window_start_date: int,
    store_rows: int,
    seller_rows: int,
    stock_rows: int,
    finished_at: datetime | None = None,
) -> RefreshState:
    timestamp = (finished_at or datetime.now()).isoformat(timespec="seconds")
    return RefreshState(
        trailing_refresh_days=trailing_refresh_days,
        window_start_date=window_start_date,
        last_success_at=timestamp,
        last_store_row_count=store_rows,
        last_seller_row_count=seller_rows,
        last_stock_row_count=stock_rows,
    )


def _parse_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    return int(value)


def _parse_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)
