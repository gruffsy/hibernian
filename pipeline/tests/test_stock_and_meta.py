from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from hibernian_pipeline.build.stock import build_stock_payload
from hibernian_pipeline.extract.meta import build_meta_payload
from hibernian_pipeline.extract.meta import format_update_timestamp


def test_build_stock_payload_merges_orders() -> None:
    stock_rows = [
        {
            "Prodno": "ABC",
            "Beskrivelse": "Produkt A",
            "antall på lager": 100.0,
            "antall pr pall": 50.0,
            "Paller på lager": 2,
            "Paller på vei": 1,
        }
    ]
    order_rows = [
        {
            "Prodno": "ABC",
            "Descr": "Produkt A",
            "NoInvoAb": 25.5,
            "Week_Year": "28/2026",
        }
    ]

    payload = build_stock_payload(stock_rows, order_rows)

    assert len(payload) == 1
    assert payload[0]["Prodno"] == "ABC"
    assert payload[0]["Beskrivelse"] == "Produkt A"
    assert payload[0]["Bestilling på vei"] == [{"Ukenr": "28/2026", "Antall": 25.5}]


def test_format_update_timestamp_rounds_down_to_five_minutes() -> None:
    moment = datetime(2026, 5, 22, 12, 43, 18, tzinfo=ZoneInfo("Europe/Oslo"))
    assert format_update_timestamp(moment) == "12:40 - fredag 22. mai 2026"


def test_build_meta_payload() -> None:
    moment = datetime(2026, 5, 22, 12, 43, 18, tzinfo=ZoneInfo("Europe/Oslo"))
    assert build_meta_payload(moment) == [{"oppdatert": "12:40 - fredag 22. mai 2026"}]
