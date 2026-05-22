from __future__ import annotations

import argparse
import shutil
import json
from pathlib import Path

from .bootstrap.visma_history import describe_step as describe_bootstrap_visma_history
from .bootstrap.visma_history import run as run_bootstrap_visma_history
from .build.seller_day import run as run_build_seller_day
from .build.stock import run as run_build_stock
from .build.store_day import run as run_build_store_day
from .build.seller_day import describe_step as describe_build_seller_day
from .build.stock import describe_step as describe_build_stock
from .build.store_day import describe_step as describe_build_store_day
from .extract.meta import run as run_extract_meta
from .extract.meta import describe_step as describe_extract_meta
from .extract.nav_seller_day import run as run_extract_nav_seller_day
from .extract.nav_seller_day import describe_step as describe_extract_nav_seller_day
from .extract.nav_store_day import run as run_extract_nav_store_day
from .extract.nav_store_day import describe_step as describe_extract_nav_store_day
from .extract.stock import run as run_extract_stock
from .extract.stock import describe_step as describe_extract_stock
from .publish.local import publish_to_beta_static_copy
from .publish.local import describe_step as describe_publish_local
from .settings import load_config
from .shared.models import PipelineStep


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
    subparsers.add_parser("extract-nav-store-day", help="Normalize the NAV store-day source JSON into the raw artifact")
    subparsers.add_parser("extract-nav-seller-day", help="Normalize the NAV seller-day source JSON into the raw artifact")
    subparsers.add_parser("extract-stock", help="Normalize stock balances and stock orders source JSON into raw artifacts")
    subparsers.add_parser("extract-meta", help="Build the metadata artifact with the current rounded update time")
    subparsers.add_parser("build-store-day", help="Build the published daily store feed from historical and NAV raw data")
    subparsers.add_parser("build-seller-day", help="Build the published daily seller feed from historical and NAV raw data")
    subparsers.add_parser("build-stock", help="Build the published stock feed from stock and order raw data")
    subparsers.add_parser("publish-local", help="Copy publish artifacts into the beta static data folder")
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

    if args.command == "extract-nav-store-day":
        payload = run_extract_nav_store_day(config)
        print(json.dumps({"rows": len(payload), "output_file": str(config.nav_store_day_raw)}, indent=2))
        return 0

    if args.command == "extract-nav-seller-day":
        payload = run_extract_nav_seller_day(config)
        print(json.dumps({"rows": len(payload), "output_file": str(config.nav_seller_day_raw)}, indent=2))
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

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
