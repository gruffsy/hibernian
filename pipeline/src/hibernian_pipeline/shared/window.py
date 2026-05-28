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


def shift_date_key(date_key: int, *, days: int) -> int:
    parsed = datetime.strptime(str(int(date_key)), "%Y%m%d").date()
    shifted = parsed + timedelta(days=days)
    return int(shifted.strftime("%Y%m%d"))


def compute_extract_start_date(
    *,
    trailing_refresh_days: int,
    existing_rows: Iterable[dict],
    field_name: str,
    today: date | None = None,
) -> int:
    window_start_date = compute_window_start_date(trailing_refresh_days=trailing_refresh_days, today=today)
    existing_dates = [parse_date(row.get(field_name)) for row in existing_rows]
    latest_existing_before_window = max((date_key for date_key in existing_dates if date_key < window_start_date), default=None)
    if latest_existing_before_window is None:
        return window_start_date

    gap_fill_start = shift_date_key(latest_existing_before_window, days=0)
    return min(window_start_date, gap_fill_start)


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
