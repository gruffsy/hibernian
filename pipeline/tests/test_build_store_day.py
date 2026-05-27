from hibernian_pipeline.build.store_day import build_base_snapshot_rows
from hibernian_pipeline.build.store_day import build_store_day_payload


def test_build_store_day_payload_formats_and_adds_totals() -> None:
    base_rows = [
        {
            "fakturadato": 20220103,
            "butikk": "TÃƒÂ¸nsberg",
            "Klient": "3",
            "mmoms": "100 000 kr",
            "umoms": "80 000 kr",
            "db": "16 000 kr",
            "dg": "20.0%",
            "antord": "50",
            "prord": "2 000 kr",
        }
    ]
    nav_rows = [
        {
            "fakturadato": 20220103,
            "butikk": "TÃ¸nsberg",
            "Klient": "3",
            "mmoms": 120000,
            "umoms": 96000,
            "db": 24000,
            "dg": 0.25,
            "antord": 60,
            "prord": 2000,
        },
        {
            "fakturadato": 20220103,
            "butikk": "Skien",
            "Klient": "0",
            "mmoms": 200000,
            "umoms": 160000,
            "db": 32000,
            "dg": 0.2,
            "antord": 100,
            "prord": 2000,
        },
    ]

    payload = build_store_day_payload(base_rows, nav_rows)

    assert len(payload) == 3
    assert payload[0]["butikk"] == "Skien"
    assert payload[1]["butikk"].startswith("T")
    assert payload[1]["butikk"].endswith("nsberg")
    assert payload[1]["mmoms"] == "120 000 kr"
    assert payload[2]["butikk"] == "Totalt"
    assert payload[2]["Klient"] == 99
    assert payload[2]["mmoms"] == "320 000 kr"
    assert payload[2]["umoms"] == "256 000 kr"
    assert payload[2]["db"] == "56 000 kr"
    assert payload[2]["antord"] == "160"
    assert payload[2]["prord"] == "2 000 kr"
    assert payload[2]["dg"] == "21.9%"


def test_build_base_snapshot_rows_excludes_trailing_window() -> None:
    historical_rows = [
        {"fakturadato": 20260510, "butikk": "Skien", "Klient": "0"},
        {"fakturadato": 20260520, "butikk": "Bamble", "Klient": "7"},
        {"fakturadato": 20260521, "butikk": "Totalt", "Klient": 99},
    ]

    base_rows = build_base_snapshot_rows(historical_rows, window_start_date=20260520)

    assert len(base_rows) == 1
    assert base_rows[0]["butikk"] == "Skien"
    assert base_rows[0]["fakturadato"] == 20260510
