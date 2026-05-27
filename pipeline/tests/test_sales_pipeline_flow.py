from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from hibernian_pipeline.bootstrap.visma_history import run as run_bootstrap_visma_history
from hibernian_pipeline.build.seller_day import run as run_build_seller_day
from hibernian_pipeline.build.store_day import run as run_build_store_day
from hibernian_pipeline.extract.nav_seller_day import run as run_extract_nav_seller_day
from hibernian_pipeline.extract.nav_store_day import run as run_extract_nav_store_day
from hibernian_pipeline.settings import PipelineConfig
from hibernian_pipeline.settings import PipelinePaths
from hibernian_pipeline.shared.io import read_json, write_json
from hibernian_pipeline.shared.state import build_success_state
from hibernian_pipeline.shared.state import save_refresh_state
from hibernian_pipeline.shared.window import compute_window_start_date


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
        stock_source=root / "source" / "stock.json",
        orders_source=root / "source" / "orders.json",
        historical_store_day=raw_dir / "historical_store_day.json",
        historical_seller_day=raw_dir / "historical_seller_day.json",
        nav_store_day_raw=raw_dir / "nav_store_day_raw.json",
        nav_seller_day_raw=raw_dir / "nav_seller_day_raw.json",
        stock_raw=raw_dir / "stock_raw.json",
        orders_raw=raw_dir / "orders_raw.json",
        store_day_base_snapshot=state_dir / "store_day_base_snapshot.json",
        seller_day_base_snapshot=state_dir / "seller_day_base_snapshot.json",
        refresh_state_file=state_dir / "refresh_state.json",
        store_day_publish=publish_dir / "store_day.json",
        seller_day_publish=publish_dir / "seller_day.json",
        stock_publish=publish_dir / "stock.json",
        meta_publish=publish_dir / "meta.json",
        trailing_refresh_days=7,
        nav_sql_server="example",
        nav_sql_database="example",
        nav_sql_driver="ODBC Driver 18 for SQL Server",
        nav_sql_use_snapshot_isolation=True,
        cloudflare_account_id="example",
        r2_bucket_name="example",
        r2_public_base_url="https://example.invalid",
        r2_object_prefix="latest",
    )


def _yyyymmdd(offset_days: int) -> int:
    target = datetime.now().date() + timedelta(days=offset_days)
    return int(target.strftime("%Y%m%d"))


def test_sales_pipeline_flow() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        config = make_config(root)
        config.nav_store_source.parent.mkdir(parents=True, exist_ok=True)

        historical_date = _yyyymmdd(-30)
        recent_date = _yyyymmdd(0)

        write_json(
            config.bootstrap_store_source,
            [
                {
                    "fakturadato": historical_date,
                    "butikk": "TÃƒÂ¸nsberg",
                    "Klient": "3",
                    "mmoms": "100 000 kr",
                    "umoms": "80 000 kr",
                    "db": "16 000 kr",
                    "dg": "20.0%",
                    "antord": "50",
                    "prord": "2 000 kr",
                },
                {
                    "fakturadato": historical_date,
                    "butikk": "Totalt",
                    "Klient": 99,
                    "mmoms": "100 000 kr",
                    "umoms": "80 000 kr",
                    "db": "16 000 kr",
                    "dg": "20.0%",
                    "antord": "50",
                    "prord": "2 000 kr",
                },
            ],
        )
        write_json(
            config.bootstrap_seller_source,
            [
                {
                    "ukedag": "Fredag",
                    "navn": "Kemuel LillestÃƒÂ¸",
                    "umoms": "121 190 kr",
                    "db": "25 752 kr",
                    "butikk": "Arendal",
                    "fakturadato": historical_date,
                }
            ],
        )
        write_json(
            config.nav_store_source,
            [
                {
                    "fakturadato": historical_date,
                    "butikk": "Bamble",
                    "Klient": "7",
                    "mmoms": 50000,
                    "umoms": 40000,
                    "db": 8000,
                    "dg": 0.2,
                    "antord": 20,
                    "prord": 2500,
                },
                {
                    "fakturadato": recent_date,
                    "butikk": "Skien",
                    "Klient": "0",
                    "mmoms": 200000,
                    "umoms": 160000,
                    "db": 32000,
                    "dg": 0.2,
                    "antord": 100,
                    "prord": 2000,
                }
            ],
        )
        write_json(
            config.nav_seller_source,
            [
                {
                    "ukedag": "Fredag",
                    "navn": "Historisk Selger",
                    "umoms": 12345,
                    "db": 2345,
                    "butikk": "Bamble",
                    "fakturadato": historical_date,
                },
                {
                    "ukedag": "Fredag",
                    "navn": "Joakim Johnsen",
                    "umoms": 56410,
                    "db": 7963,
                    "butikk": "Skien",
                    "fakturadato": recent_date,
                }
            ],
        )

        bootstrap_result = run_bootstrap_visma_history(config)
        store_raw = run_extract_nav_store_day(config)
        seller_raw = run_extract_nav_seller_day(config)
        store_publish = run_build_store_day(config)
        seller_publish = run_build_seller_day(config)

        window_start_date = compute_window_start_date(trailing_refresh_days=config.trailing_refresh_days)
        refresh_state = build_success_state(
            trailing_refresh_days=config.trailing_refresh_days,
            window_start_date=window_start_date,
            store_rows=len(store_publish),
            seller_rows=len(seller_publish),
            stock_rows=0,
        )
        save_refresh_state(config.refresh_state_file, refresh_state)

        assert bootstrap_result == {"historical_store_rows": 1, "historical_seller_rows": 1}
        assert len(store_raw) == 1
        assert len(seller_raw) == 1
        assert len(store_publish) == 4
        assert len(seller_publish) == 2

        historical_store = read_json(config.historical_store_day)
        historical_seller = read_json(config.historical_seller_day)
        assert historical_store[0]["butikk"].startswith("T")
        assert historical_store[0]["butikk"].endswith("nsberg")
        assert historical_seller[0]["navn"].startswith("Kemuel Lillest")

        base_store = read_json(config.store_day_base_snapshot)
        base_seller = read_json(config.seller_day_base_snapshot)
        assert len(base_store) == 1
        assert len(base_seller) == 1
        assert base_store[0]["fakturadato"] == historical_date
        assert base_seller[0]["fakturadato"] == historical_date

        published_store = read_json(config.store_day_publish)
        published_seller = read_json(config.seller_day_publish)
        recent_total = next(
            row
            for row in published_store
            if row["butikk"] == "Totalt" and row["fakturadato"] == recent_date
        )
        assert recent_total["mmoms"] == "200 000 kr"
        assert published_seller[0]["navn"] == "Joakim Johnsen"
        assert published_seller[1]["navn"].startswith("Kemuel Lillest")

        stored_state = read_json(config.refresh_state_file)
        assert stored_state["window_start_date"] == window_start_date
        assert stored_state["trailing_refresh_days"] == 7
