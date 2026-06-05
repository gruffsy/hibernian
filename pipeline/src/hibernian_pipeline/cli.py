from __future__ import annotations

import argparse
import shutil
import json
from pathlib import Path

from .bootstrap.visma_history import describe_step as describe_bootstrap_visma_history
from .bootstrap.visma_history import run as run_bootstrap_visma_history
from .bootstrap.product_history import describe_step as describe_bootstrap_product_history
from .bootstrap.product_history import run as run_bootstrap_product_history
from .build.product_day import describe_step as describe_build_product_day
from .build.product_day import run as run_build_product_day
from .build.seller_day import run as run_build_seller_day
from .build.stock import run as run_build_stock
from .build.store_day import run as run_build_store_day
from .build.seller_day import describe_step as describe_build_seller_day
from .build.stock import describe_step as describe_build_stock
from .build.store_day import describe_step as describe_build_store_day
from .extract.meta import run as run_extract_meta
from .extract.meta import describe_step as describe_extract_meta
from .extract.nav_product_day import describe_step as describe_extract_nav_product_day
from .extract.nav_product_day import run as run_extract_nav_product_day
from .extract.nav_seller_day import run as run_extract_nav_seller_day
from .extract.nav_seller_day import describe_step as describe_extract_nav_seller_day
from .extract.nav_store_day import run as run_extract_nav_store_day
from .extract.nav_store_day import describe_step as describe_extract_nav_store_day
from .extract.stock import run as run_extract_stock
from .extract.stock import describe_step as describe_extract_stock
from .publish.local import publish_to_beta_static_copy
from .publish.local import publish_product_to_beta_static_copy
from .publish.local import describe_step as describe_publish_local
from .publish.r2 import publish_products_to_r2
from .publish.r2 import publish_to_r2
from .publish.r2 import describe_step as describe_publish_r2
from .settings import load_config
from .shared.models import PipelineStep
from .shared.state import build_success_state
from .shared.state import save_refresh_state
from .shared.window import compute_window_start_date


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hibernian pipeline scaffold CLI")
    parser.add_argument(
        "--pipeline-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Path to the pipeline/ directory",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("paths", help="Print resolved pipeline paths as JSON")
    subparsers.add_parser("plan", help="Print the planned pipeline steps as JSON")
    subparsers.add_parser("init-layout", help="Create the expected pipeline directory layout")
    subparsers.add_parser("write-example-config", help="Copy pipeline.example.json to pipeline.json if missing")
    subparsers.add_parser("bootstrap-visma-history", help="Seed historical store and seller artifacts from the frozen published history")
    subparsers.add_parser("bootstrap-product-history", help="Seed the product history snapshot from NAV SQL")
    subparsers.add_parser("extract-nav-store-day", help="Normalize the NAV store-day source JSON into the raw artifact")
    subparsers.add_parser("extract-nav-seller-day", help="Normalize the NAV seller-day source JSON into the raw artifact")
    subparsers.add_parser("extract-nav-product-day", help="Normalize the NAV product-day source SQL into the raw artifact")
    subparsers.add_parser("extract-stock", help="Normalize stock balances and stock orders source JSON into raw artifacts")
    subparsers.add_parser("extract-meta", help="Build the metadata artifact with the current rounded update time")
    subparsers.add_parser("build-store-day", help="Build the published daily store feed from historical and NAV raw data")
    subparsers.add_parser("build-seller-day", help="Build the published daily seller feed from historical and NAV raw data")
    subparsers.add_parser("build-product-day", help="Build the published daily product feed from historical and NAV raw data")
    subparsers.add_parser("build-stock", help="Build the published stock feed from stock and order raw data")
    subparsers.add_parser("publish-local", help="Copy publish artifacts into the beta static data folder")
    publish_r2_parser = subparsers.add_parser("publish-r2", help="Upload publish artifacts to the Cloudflare R2 bucket")
    publish_r2_parser.add_argument(
        "--include-product-history",
        action="store_true",
        help="Also upload the immutable product history snapshot to R2.",
    )
    publish_r2_products_parser = subparsers.add_parser("publish-r2-products", help="Upload only the product publish artifacts to the Cloudflare R2 bucket")
    publish_r2_products_parser.add_argument(
        "--include-product-history",
        action="store_true",
        help="Also upload the immutable product history snapshot to R2.",
    )
    subparsers.add_parser("refresh-r2", help="Run the production sales refresh before publishing to local beta data and Cloudflare R2")
    refresh_products_parser = subparsers.add_parser("refresh-products", help="Run the product refresh and publish to Cloudflare R2")
    refresh_products_parser.add_argument(
        "--skip-product-extract",
        action="store_true",
        help="Reuse the existing NAV product raw file instead of running the NAV product extract again.",
    )
    return parser


def _build_plan(config) -> list[PipelineStep]:
    return [
        describe_bootstrap_visma_history(config),
        describe_extract_nav_store_day(config),
        describe_extract_nav_seller_day(config),
        describe_extract_stock(config),
        describe_extract_meta(config),
        describe_build_store_day(config),
        describe_build_seller_day(config),
        describe_build_stock(config),
        describe_publish_local(config),
        describe_publish_r2(config),
    ]


def _init_layout(config) -> list[str]:
    created: list[str] = []
    for directory in config.paths.managed_directories():
        directory.mkdir(parents=True, exist_ok=True)
        created.append(str(directory))
    return created


def _write_example_config(config) -> Path:
    source = config.paths.example_config_file
    destination = config.paths.config_file
    if destination.exists():
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    return destination


def _run_refresh_r2_cycle(config) -> dict[str, object]:
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
        }
    )

    seller_rows = run_build_seller_day(config)
    result["steps"].append(
        {
            "name": "build-seller-day",
            "rows": len(seller_rows),
            "output_file": str(config.seller_day_publish),
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

    uploaded = publish_to_r2(config)
    result["steps"].append({"name": "publish-r2", "uploaded": uploaded})

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

    return result


def _run_refresh_products_cycle(config, *, skip_product_extract: bool = False) -> dict[str, object]:
    result: dict[str, object] = {"steps": []}
    window_start_date = compute_window_start_date(trailing_refresh_days=config.product_refresh_days)
    result["window_start_date"] = window_start_date
    include_product_history = False

    if not config.product_history_base_snapshot or not config.product_history_base_snapshot.exists():
        bootstrap_product_result = run_bootstrap_product_history(config)
        result["steps"].append({"name": "bootstrap-product-history", "result": bootstrap_product_result})
        include_product_history = True

    if skip_product_extract:
        if not config.nav_product_day_raw or not config.nav_product_day_raw.exists():
            raise RuntimeError("Missing NAV product raw file for skipped extract mode.")
        result["steps"].append(
            {
                "name": "reuse-nav-product-day",
                "rows": None,
                "output_file": str(config.nav_product_day_raw),
            }
        )
    else:
        nav_product_rows = run_extract_nav_product_day(config)
        result["steps"].append(
            {
                "name": "extract-nav-product-day",
                "rows": len(nav_product_rows),
                "output_file": str(config.nav_product_day_raw),
            }
        )

    product_rows = run_build_product_day(config)
    result["steps"].append(
        {
            "name": "build-product-day",
            "available_dates": len(product_rows.get("availableDates", [])) if isinstance(product_rows, dict) else 0,
            "output_file": str(config.product_day_publish),
        }
    )

    copied = publish_product_to_beta_static_copy(config)
    result["steps"].append({"name": "publish-local-products", "copied": copied})

    uploaded = publish_products_to_r2(config, include_product_history=include_product_history)
    result["steps"].append({"name": "publish-r2-products", "uploaded": uploaded})

    return result


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(args.pipeline_root)

    if args.command == "paths":
        print(json.dumps(config.to_dict(), indent=2))
        return 0

    if args.command == "plan":
        plan = [step.to_dict() for step in _build_plan(config)]
        print(json.dumps({"steps": plan}, indent=2))
        return 0

    if args.command == "init-layout":
        created = _init_layout(config)
        print(json.dumps({"directories": created}, indent=2))
        return 0

    if args.command == "write-example-config":
        destination = _write_example_config(config)
        print(json.dumps({"config_file": str(destination)}, indent=2))
        return 0

    if args.command == "bootstrap-visma-history":
        result = run_bootstrap_visma_history(config)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "bootstrap-product-history":
        result = run_bootstrap_product_history(config)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "extract-nav-store-day":
        payload = run_extract_nav_store_day(config)
        print(json.dumps({"rows": len(payload), "output_file": str(config.nav_store_day_raw)}, indent=2))
        return 0

    if args.command == "extract-nav-seller-day":
        payload = run_extract_nav_seller_day(config)
        print(json.dumps({"rows": len(payload), "output_file": str(config.nav_seller_day_raw)}, indent=2))
        return 0

    if args.command == "extract-nav-product-day":
        payload = run_extract_nav_product_day(config)
        print(json.dumps({"rows": len(payload), "output_file": str(config.nav_product_day_raw)}, indent=2))
        return 0

    if args.command == "extract-stock":
        result = run_extract_stock(config)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "extract-meta":
        payload = run_extract_meta(config)
        print(json.dumps({"rows": len(payload), "output_file": str(config.meta_publish)}, indent=2))
        return 0

    if args.command == "build-store-day":
        payload = run_build_store_day(config)
        print(
            json.dumps(
                {
                    "rows": len(payload),
                    "output_file": str(config.store_day_publish),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "build-seller-day":
        payload = run_build_seller_day(config)
        print(
            json.dumps(
                {
                    "rows": len(payload),
                    "output_file": str(config.seller_day_publish),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "build-product-day":
        payload = run_build_product_day(config)
        periods = payload.get("periods", {}) if isinstance(payload, dict) else {}
        print(
            json.dumps(
                {
                    "available_dates": len(payload.get("availableDates", [])) if isinstance(payload, dict) else 0,
                    "day_periods": len(periods.get("day", {})) if isinstance(periods, dict) else 0,
                    "week_periods": len(periods.get("week", {})) if isinstance(periods, dict) else 0,
                    "month_periods": len(periods.get("month", {})) if isinstance(periods, dict) else 0,
                    "year_periods": len(periods.get("year", {})) if isinstance(periods, dict) else 0,
                    "output_file": str(config.product_day_publish),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "build-stock":
        payload = run_build_stock(config)
        print(
            json.dumps(
                {
                    "rows": len(payload),
                    "output_file": str(config.stock_publish),
                },
                indent=2,
            )
        )
        return 0

    if args.command == "publish-local":
        copied = publish_to_beta_static_copy(config)
        print(json.dumps({"copied": copied}, indent=2))
        return 0

    if args.command == "publish-r2":
        uploaded = publish_to_r2(config, include_product_history=getattr(args, "include_product_history", False))
        print(json.dumps({"uploaded": uploaded}, indent=2))
        return 0

    if args.command == "publish-r2-products":
        uploaded = publish_products_to_r2(
            config,
            include_product_history=getattr(args, "include_product_history", False),
        )
        print(json.dumps({"uploaded": uploaded}, indent=2))
        return 0

    if args.command == "refresh-r2":
        result = _run_refresh_r2_cycle(config)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "refresh-products":
        result = _run_refresh_products_cycle(config, skip_product_extract=getattr(args, "skip_product_extract", False))
        print(json.dumps(result, indent=2))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
