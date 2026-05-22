from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

DEFAULT_NAV_STORE_SOURCE = Path(r"\\PO02-HP\Salgstall\hibernian\revamp\jsons\nav_salg_fra_22.json")
DEFAULT_NAV_SELLER_SOURCE = Path(r"\\PO02-HP\Salgstall\hibernian\revamp\jsons\nav_salg_pr_selger_fra_22.json")
DEFAULT_STOCK_SOURCE = Path(r"\\PO02-HP\Salgstall\hibernian\json\lager_stock.sql.json")
DEFAULT_ORDERS_SOURCE = Path(r"\\PO02-HP\Salgstall\hibernian\json\bestillinger_stock.sql.json")


@dataclass(frozen=True)
class PipelinePaths:
    pipeline_root: Path
    config_dir: Path
    artifacts_raw_dir: Path
    artifacts_publish_dir: Path
    logs_dir: Path
    scripts_dir: Path
    sql_sales_dir: Path
    sql_stock_dir: Path
    legacy_publish_dir: Path
    legacy_json_dir: Path

    def to_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}

    @property
    def config_file(self) -> Path:
        return self.config_dir / "pipeline.json"

    @property
    def example_config_file(self) -> Path:
        return self.config_dir / "pipeline.example.json"

    def managed_directories(self) -> tuple[Path, ...]:
        return (
            self.config_dir,
            self.artifacts_raw_dir,
            self.artifacts_publish_dir,
            self.logs_dir,
            self.scripts_dir,
            self.sql_sales_dir,
            self.sql_stock_dir,
        )


@dataclass(frozen=True)
class PipelineConfig:
    paths: PipelinePaths
    bootstrap_store_source: Path
    bootstrap_seller_source: Path
    nav_store_source: Path
    nav_seller_source: Path
    stock_source: Path
    orders_source: Path
    historical_store_day: Path
    historical_seller_day: Path
    nav_store_day_raw: Path
    nav_seller_day_raw: Path
    stock_raw: Path
    orders_raw: Path
    store_day_publish: Path
    seller_day_publish: Path
    stock_publish: Path
    meta_publish: Path

    def to_dict(self) -> dict[str, object]:
        data = {"paths": self.paths.to_dict()}
        for key, value in asdict(self).items():
            if key == "paths":
                continue
            data[key] = str(value)
        return data


def _default_paths(pipeline_root: Path) -> PipelinePaths:
    repo_root = pipeline_root.parent
    legacy_root = repo_root / "legacy" / "frontend-static" / "data"
    return PipelinePaths(
        pipeline_root=pipeline_root,
        config_dir=pipeline_root / "config",
        artifacts_raw_dir=pipeline_root / "artifacts" / "raw",
        artifacts_publish_dir=pipeline_root / "artifacts" / "publish",
        logs_dir=pipeline_root / "logs",
        scripts_dir=pipeline_root / "scripts",
        sql_sales_dir=pipeline_root / "sql" / "sales",
        sql_stock_dir=pipeline_root / "sql" / "stock",
        legacy_publish_dir=legacy_root / "publish",
        legacy_json_dir=legacy_root / "json",
    )


def load_config(pipeline_root: Path) -> PipelineConfig:
    pipeline_root = pipeline_root.resolve()
    paths = _default_paths(pipeline_root)
    config_file = paths.config_file
    values: dict[str, str] = {}

    if config_file.exists():
        values = json.loads(config_file.read_text(encoding="utf-8"))

    def resolve_path(key: str, default: Path) -> Path:
        raw = values.get(key)
        if not raw:
            return default
        candidate = Path(raw)
        return candidate if candidate.is_absolute() else pipeline_root.parent / candidate

    return PipelineConfig(
        paths=paths,
        bootstrap_store_source=resolve_path(
            "bootstrap_store_source",
            paths.legacy_publish_dir / "salg_fra_22_pr_dag_med_total.json",
        ),
        bootstrap_seller_source=resolve_path(
            "bootstrap_seller_source",
            paths.legacy_publish_dir / "salg_pr_selger_fra_22_pr_dag.json",
        ),
        nav_store_source=resolve_path("nav_store_source", DEFAULT_NAV_STORE_SOURCE),
        nav_seller_source=resolve_path("nav_seller_source", DEFAULT_NAV_SELLER_SOURCE),
        stock_source=resolve_path("stock_source", DEFAULT_STOCK_SOURCE),
        orders_source=resolve_path("orders_source", DEFAULT_ORDERS_SOURCE),
        historical_store_day=resolve_path("historical_store_day", paths.artifacts_raw_dir / "historical_store_day.json"),
        historical_seller_day=resolve_path("historical_seller_day", paths.artifacts_raw_dir / "historical_seller_day.json"),
        nav_store_day_raw=resolve_path("nav_store_day_raw", paths.artifacts_raw_dir / "nav_store_day_raw.json"),
        nav_seller_day_raw=resolve_path("nav_seller_day_raw", paths.artifacts_raw_dir / "nav_seller_day_raw.json"),
        stock_raw=resolve_path("stock_raw", paths.artifacts_raw_dir / "stock_raw.json"),
        orders_raw=resolve_path("orders_raw", paths.artifacts_raw_dir / "orders_raw.json"),
        store_day_publish=resolve_path("store_day_publish", paths.artifacts_publish_dir / "store_day.json"),
        seller_day_publish=resolve_path("seller_day_publish", paths.artifacts_publish_dir / "seller_day.json"),
        stock_publish=resolve_path("stock_publish", paths.artifacts_publish_dir / "stock.json"),
        meta_publish=resolve_path("meta_publish", paths.artifacts_publish_dir / "meta.json"),
    )
