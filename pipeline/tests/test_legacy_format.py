from __future__ import annotations

from datetime import date
from datetime import datetime

from hibernian_pipeline.shared.legacy_format import parse_date
from hibernian_pipeline.shared.legacy_format import parse_number


def test_parse_date_accepts_datetime_and_date() -> None:
    assert parse_date(datetime(2024, 4, 10, 0, 0)) == 20240410
    assert parse_date(date(2024, 4, 10)) == 20240410
    assert parse_date("2024-04-10") == 20240410


def test_parse_number_accepts_dash_decimal() -> None:
    assert parse_number("0-18") == 0.18
    assert parse_number("1-25") == 1.25
