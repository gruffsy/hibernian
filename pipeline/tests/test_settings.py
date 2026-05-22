from pathlib import Path

from hibernian_pipeline.settings import load_config


def test_load_config_defaults() -> None:
    pipeline_root = Path(__file__).resolve().parents[1]
    config = load_config(pipeline_root)
    assert config.store_day_publish.name == "store_day.json"
    assert config.bootstrap_store_source.name == "salg_fra_22_pr_dag_med_total.json"
    assert config.bootstrap_seller_source.name == "salg_pr_selger_fra_22_pr_dag.json"
    assert config.nav_store_source.name == "nav_salg_fra_22.json"
    assert config.nav_seller_source.name == "nav_salg_pr_selger_fra_22.json"
    assert config.stock_source.name == "lager_stock.sql.json"
    assert config.orders_source.name == "bestillinger_stock.sql.json"
    assert config.paths.legacy_publish_dir.name == "publish"
    assert config.paths.config_file.name == "pipeline.json"
    assert config.paths.example_config_file.name == "pipeline.example.json"
    assert config.paths.artifacts_raw_dir in config.paths.managed_directories()
