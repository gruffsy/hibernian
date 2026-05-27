from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import Iterable

from .legacy_format import parse_date


def compute_window_start_date(*, trailing_refresh_days: int, today: date | None = None) -> int:
    current_date = today or datetime.now().date()
    days = max(int(trailing_refresh_days), 1)
    start = current_date - timedelta(days=days - 1)
    return int(start.strftime("%Y%m%d"))


def filter_rows_on_or_after_date(rows: Iterable[dict], *, field_name: str, start_date: int) -> list[dict]:
    result: list[dict] = []
    for row in rows:
        if parse_date(row.get(field_name)) >= start_date:
            result.append(row)
    return result


def filter_rows_before_date(rows: Iterable[dict], *, field_name: str, start_date: int) -> list[dict]:
    result: list[dict] = []
    for row in rows:
        if parse_date(row.get(field_name)) < start_date:
            result.append(row)
    return result
