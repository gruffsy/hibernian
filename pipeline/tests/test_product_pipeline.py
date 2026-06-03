from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from hibernian_pipeline.bootstrap.product_history import run as run_bootstrap_product_history
from hibernian_pipeline.build.product_day import build_product_day_payload
from hibernian_pipeline.build.product_day import run as run_build_product_day
from hibernian_pipeline.extract.nav_product_day import run as run_extract_nav_product_day
from hibernian_pipeline.settings import PipelineConfig
from hibernian_pipeline.settings import PipelinePaths
from hibernian_pipeline.shared.io import read_json
from hibernian_pipeline.shared.io import write_json


def make_config(root: Path) -> PipelineConfig:
    pipeline_root = root / "pipeline"
    config_dir = pipeline_root / "config"
    raw_dir = pipeline_root / "artifacts" / "raw"
    state_dir = pipeline_root / "artifacts" / "state"
    publish_dir = pipeline_root / "artifacts" / "publish"
    logs_dir = pipeline_root / "logs"
    scripts_dir = pipeline_root / "scripts"
    sql_sales_dir = pipeline_root / "sql" / "sales"
    sql_stock_dir = pipeline_root / "sql" / "stock"
    legacy_publish_dir = root / "legacy" / "frontend-static" / "data" / "publish"
    legacy_json_dir = root / "legacy" / "frontend-static" / "data" / "json"

    for directory in (
        config_dir,
        raw_dir,
        state_dir,
        publish_dir,
        logs_dir,
        scripts_dir,
        sql_sales_dir,
        sql_stock_dir,
        legacy_publish_dir,
        legacy_json_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    paths = PipelinePaths(
        pipeline_root=pipeline_root,
        config_dir=config_dir,
        artifacts_raw_dir=raw_dir,
        artifacts_state_dir=state_dir,
        artifacts_publish_dir=publish_dir,
        logs_dir=logs_dir,
        scripts_dir=scripts_dir,
        sql_sales_dir=sql_sales_dir,
        sql_stock_dir=sql_stock_dir,
        legacy_publish_dir=legacy_publish_dir,
        legacy_json_dir=legacy_json_dir,
    )

    return PipelineConfig(
        paths=paths,
        bootstrap_store_source=legacy_publish_dir / "salg_fra_22_pr_dag_med_total.json",
        bootstrap_seller_source=legacy_publish_dir / "salg_pr_selger_fra_22_pr_dag.json",
        nav_store_source=root / "source" / "nav_salg_fra_22.json",
        nav_seller_source=root / "source" / "nav_salg_pr_selger_fra_22.json",
        nav_store_sql_file=pipeline_root / "sql" / "sales" / "nav_store_day_window.sql",
        nav_seller_sql_file=pipeline_root / "sql" / "sales" / "nav_seller_day_window.sql",
        nav_product_sql_file=pipeline_root / "sql" / "sales" / "nav_product_day_window.sql",
        stock_source=root / "source" / "stock.json",
        orders_source=root / "source" / "orders.json",
        historical_store_day=raw_dir / "historical_store_day.json",
        historical_seller_day=raw_dir / "historical_seller_day.json",
        nav_store_day_raw=raw_dir / "nav_store_day_raw.json",
        nav_seller_day_raw=raw_dir / "nav_seller_day_raw.json",
        nav_product_day_raw=raw_dir / "nav_product_day_raw.json",
        stock_raw=raw_dir / "stock_raw.json",
        orders_raw=raw_dir / "orders_raw.json",
        store_day_base_snapshot=state_dir / "store_day_base_snapshot.json",
        seller_day_base_snapshot=state_dir / "seller_day_base_snapshot.json",
        product_history_base_snapshot=state_dir / "product_history_base_snapshot.json",
        refresh_state_file=state_dir / "refresh_state.json",
        store_day_publish=publish_dir / "store_day.json",
        seller_day_publish=publish_dir / "seller_day.json",
        product_history_publish=publish_dir / "product_history.json",
        product_day_publish=state_dir / "product_summary.json",
        stock_publish=publish_dir / "stock.json",
        meta_publish=publish_dir / "meta.json",
        trailing_refresh_days=7,
        product_refresh_days=2,
        backfill_start_date=None,
        product_backfill_start_date=20250101,
        nav_sql_server="example",
        nav_sql_database="example",
        nav_sql_driver="ODBC Driver 18 for SQL Server",
        nav_sql_use_snapshot_isolation=True,
        cloudflare_account_id="example",
        r2_bucket_name="example",
        r2_public_base_url="https://example.invalid",
        r2_object_prefix="latest",
    )


def test_product_bootstrap_extract_and_build_payload() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        config = make_config(root)

        historical_rows = [
            {
                "Item No_": "1001",
                "Description": "Historisk flis",
                "Item Category": "Flis",
                "Retail Product Group": "Keramikk",
                "fakturadato": datetime(2025, 1, 2),
                "antall": 3,
                "umoms": 300,
                "db": 90,
                "dg": 0.3,
            },
            {
                "Item No_": "1002",
                "Description": "Historisk bad",
                "Item Category": "Baderom",
                "Retail Product Group": "Inventar",
                "fakturadato": datetime(2025, 1, 2),
                "antall": 1,
                "umoms": 150,
                "db": 30,
                "dg": 0.2,
            },
        ]

        with patch("hibernian_pipeline.bootstrap.product_history.run_nav_query", return_value=historical_rows):
            bootstrap_result = run_bootstrap_product_history(config)

        assert bootstrap_result["status"] == "bootstrapped"
        assert bootstrap_result["product_rows"] == 2
        assert config.product_history_base_snapshot.exists()
        assert config.product_history_publish.exists()

        nav_rows = [
            {
                "Item No_": "2001",
                "Description": "Ny vare",
                "Item Category": "Flis",
                "Retail Product Group": "Kampanje",
                "fakturadato": datetime(2026, 6, 2),
                "antall": "5",
                "umoms": "500",
                "db": "125",
                "dg": 0.25,
            }
        ]
        write_json(config.nav_product_day_raw, nav_rows)

        payload = run_build_product_day(config)
        assert payload["availableDates"][0] == 20260602
        assert payload["periods"]["day"][20260602]["totals"]["umoms"] == 500
        assert payload["periods"]["day"][20260602]["metrics"]["umoms"][0]["Item No_"] == "2001"
        assert payload["periods"]["month"]["2025-01"]["totals"]["umoms"] == 450
        assert payload["periods"]["month"]["2025-01"]["metrics"]["umoms"][0]["Item No_"] == "1001"
        assert config.product_day_publish.exists()


def test_product_extract_normalizes_rows() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        config = make_config(root)
        rows = [
            {
                "Item No_": "3001",
                "Description": "TÃƒÂ¸nsberg sett",
                "Item Category": "KÃƒÂ¸kken",
                "Retail Product Group": "Spesial",
                "fakturadato": datetime(2026, 6, 2),
                "antall": "0-18",
                "umoms": "1 250",
                "db": "250",
                "dg": "20%",
            }
        ]

        with patch("hibernian_pipeline.extract.nav_product_day.run_nav_query", return_value=rows):
            payload = run_extract_nav_product_day(config)

        assert len(payload) == 1
        assert payload[0]["Description"].startswith("T")
        assert payload[0]["antall"] == 0.18
        assert payload[0]["dg"] == 0.2
        assert read_json(config.nav_product_day_raw)[0]["Item No_"] == "3001"


def test_build_product_day_payload_aggregates_and_limits_top_20() -> None:
    base_rows = [
        {
            "Item No_": "1001",
            "Description": "Base vare",
            "Item Category": "Flis",
            "Retail Product Group": "Keramikk",
            "fakturadato": 20250530,
            "antall": 3,
            "umoms": 300,
            "db": 90,
            "dg": 0.3,
        }
    ]
    for index in range(2, 24):
        base_rows.append(
            {
                "Item No_": f"{1000 + index}",
                "Description": f"Produkt {index}",
                "Item Category": "Kategori",
                "Retail Product Group": "Gruppe",
                "fakturadato": 20250530,
                "antall": index,
                "umoms": index * 100,
                "db": index * 25,
                "dg": 0.25,
            }
        )

    nav_rows = [
        {
            "Item No_": "1001",
            "Description": "Base vare",
            "Item Category": "Flis",
            "Retail Product Group": "Keramikk",
            "fakturadato": 20250530,
            "antall": 4,
            "umoms": 400,
            "db": 120,
            "dg": 0.3,
        },
        {
            "Item No_": "1002",
            "Description": "Ny vare",
            "Item Category": "Kjøkken",
            "Retail Product Group": "Kampanje",
            "fakturadato": 20250531,
            "antall": 2,
            "umoms": 200,
            "db": 50,
            "dg": 0.25,
        },
    ]

    payload = build_product_day_payload(base_rows, nav_rows)

    assert payload["periods"]["day"][20250530]["totals"]["umoms"] == 7000
    assert payload["periods"]["day"][20250530]["totals"]["db"] == 1745
    assert payload["periods"]["day"][20250530]["totals"]["dg"] == 0.2493
    assert len(payload["periods"]["day"][20250530]["metrics"]["umoms"]) == 20
    assert payload["periods"]["day"][20250530]["metrics"]["umoms"][0]["Item No_"] == "1023"
    assert payload["periods"]["day"][20250530]["metrics"]["umoms"][-1]["Item No_"] == "1005"
    assert payload["periods"]["day"][20250531]["totals"]["umoms"] == 200
    assert payload["periods"]["day"][20250531]["metrics"]["umoms"][0]["Item No_"] == "1002"
