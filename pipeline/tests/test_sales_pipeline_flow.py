from __future__ import annotations

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


def make_config(root: Path) -> PipelineConfig:
    pipeline_root = root / "pipeline"
    config_dir = pipeline_root / "config"
    raw_dir = pipeline_root / "artifacts" / "raw"
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
        historical_store_day=raw_dir / "historical_store_day.json",
        historical_seller_day=raw_dir / "historical_seller_day.json",
        nav_store_day_raw=raw_dir / "nav_store_day_raw.json",
        nav_seller_day_raw=raw_dir / "nav_seller_day_raw.json",
        stock_raw=raw_dir / "stock_raw.json",
        orders_raw=raw_dir / "orders_raw.json",
        store_day_publish=publish_dir / "store_day.json",
        seller_day_publish=publish_dir / "seller_day.json",
        stock_publish=publish_dir / "stock.json",
        meta_publish=publish_dir / "meta.json",
    )


def test_sales_pipeline_flow() -> None:
    with TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        config = make_config(root)
        config.nav_store_source.parent.mkdir(parents=True, exist_ok=True)

        write_json(
            config.bootstrap_store_source,
            [
                {
                    "fakturadato": 20220103,
                    "butikk": "TÃ¸nsberg",
                    "Klient": "3",
                    "mmoms": "100 000 kr",
                    "umoms": "80 000 kr",
                    "db": "16 000 kr",
                    "dg": "20.0%",
                    "antord": "50",
                    "prord": "2 000 kr",
                },
                {
                    "fakturadato": 20220103,
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
                    "navn": "Kemuel LillestÃ¸",
                    "umoms": "121 190 kr",
                    "db": "25 752 kr",
                    "butikk": "Arendal",
                    "fakturadato": 20260515,
                }
            ],
        )
        write_json(
            config.nav_store_source,
            [
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
                }
            ],
        )
        write_json(
            config.nav_seller_source,
            [
                {
                    "ukedag": "Fredag",
                    "navn": "Joakim Johnsen",
                    "umoms": 56410,
                    "db": 7963,
                    "butikk": "Skien",
                    "fakturadato": 20260515,
                }
            ],
        )

        bootstrap_result = run_bootstrap_visma_history(config)
        store_raw = run_extract_nav_store_day(config)
        seller_raw = run_extract_nav_seller_day(config)
        store_publish = run_build_store_day(config)
        seller_publish = run_build_seller_day(config)

        assert bootstrap_result == {"historical_store_rows": 1, "historical_seller_rows": 1}
        assert len(store_raw) == 1
        assert len(seller_raw) == 1
        assert len(store_publish) == 3
        assert len(seller_publish) == 2

        historical_store = read_json(config.historical_store_day)
        historical_seller = read_json(config.historical_seller_day)
        assert historical_store[0]["butikk"] == "Tønsberg"
        assert historical_seller[0]["navn"] == "Kemuel Lillestø"

        published_store = read_json(config.store_day_publish)
        published_seller = read_json(config.seller_day_publish)
        assert published_store[-1]["butikk"] == "Totalt"
        assert published_store[-1]["mmoms"] == "300 000 kr"
        assert published_seller[0]["navn"] == "Kemuel Lillestø"
        assert published_seller[1]["navn"] == "Joakim Johnsen"
