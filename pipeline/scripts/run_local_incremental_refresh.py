from __future__ import annotations

import json
from pathlib import Path

from hibernian_pipeline.bootstrap.visma_history import run as run_bootstrap_visma_history
from hibernian_pipeline.build.seller_day import run as run_build_seller_day
from hibernian_pipeline.build.stock import run as run_build_stock
from hibernian_pipeline.build.store_day import run as run_build_store_day
from hibernian_pipeline.extract.meta import run as run_extract_meta
from hibernian_pipeline.extract.nav_seller_day import run as run_extract_nav_seller_day
from hibernian_pipeline.extract.nav_store_day import run as run_extract_nav_store_day
from hibernian_pipeline.extract.stock import run as run_extract_stock
from hibernian_pipeline.publish.local import publish_to_beta_static_copy
from hibernian_pipeline.settings import load_config
from hibernian_pipeline.shared.state import build_success_state
from hibernian_pipeline.shared.state import save_refresh_state
from hibernian_pipeline.shared.window import compute_window_start_date


def main() -> int:
    config = load_config(Path("."))
    result: dict[str, object] = {"steps": []}
    window_start_date = compute_window_start_date(trailing_refresh_days=config.trailing_refresh_days)
    result["window_start_date"] = window_start_date

    if not config.historical_store_day.exists() or not config.historical_seller_day.exists():
        bootstrap_result = run_bootstrap_visma_history(config)
        result["steps"].append({"name": "bootstrap-visma-history", "result": bootstrap_result})

    nav_store_rows = run_extract_nav_store_day(config)
    result["steps"].append(
        {
            "name": "extract-nav-store-day",
            "rows": len(nav_store_rows),
            "output_file": str(config.nav_store_day_raw),
        }
    )

    nav_seller_rows = run_extract_nav_seller_day(config)
    result["steps"].append(
        {
            "name": "extract-nav-seller-day",
            "rows": len(nav_seller_rows),
            "output_file": str(config.nav_seller_day_raw),
        }
    )

    stock_result = run_extract_stock(config)
    result["steps"].append({"name": "extract-stock", "result": stock_result})

    meta_rows = run_extract_meta(config)
    result["steps"].append(
        {
            "name": "extract-meta",
            "rows": len(meta_rows),
            "output_file": str(config.meta_publish),
        }
    )

    store_rows = run_build_store_day(config)
    result["steps"].append(
        {
            "name": "build-store-day",
            "rows": len(store_rows),
            "output_file": str(config.store_day_publish),
            "base_snapshot_file": str(config.store_day_base_snapshot),
        }
    )

    seller_rows = run_build_seller_day(config)
    result["steps"].append(
        {
            "name": "build-seller-day",
            "rows": len(seller_rows),
            "output_file": str(config.seller_day_publish),
            "base_snapshot_file": str(config.seller_day_base_snapshot),
        }
    )

    stock_rows = run_build_stock(config)
    result["steps"].append(
        {
            "name": "build-stock",
            "rows": len(stock_rows),
            "output_file": str(config.stock_publish),
        }
    )

    copied = publish_to_beta_static_copy(config)
    result["steps"].append({"name": "publish-local", "copied": copied})

    refresh_state = build_success_state(
        trailing_refresh_days=config.trailing_refresh_days,
        window_start_date=window_start_date,
        store_rows=len(store_rows),
        seller_rows=len(seller_rows),
        stock_rows=len(stock_rows),
    )
    save_refresh_state(config.refresh_state_file, refresh_state)
    result["steps"].append(
        {
            "name": "write-refresh-state",
            "output_file": str(config.refresh_state_file),
            "state": refresh_state.to_dict(),
        }
    )

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
