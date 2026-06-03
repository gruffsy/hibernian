from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path

DEFAULT_NAV_STORE_SOURCE = Path(r"\\PO02-HP\Salgstall\hibernian\revamp\jsons\nav_salg_fra_22.json")
DEFAULT_NAV_SELLER_SOURCE = Path(r"\\PO02-HP\Salgstall\hibernian\revamp\jsons\nav_salg_pr_selger_fra_22.json")
DEFAULT_STOCK_SOURCE = Path(r"\\PO02-HP\Salgstall\hibernian\json\lager_stock.sql.json")
DEFAULT_ORDERS_SOURCE = Path(r"\\PO02-HP\Salgstall\hibernian\json\bestillinger_stock.sql.json")
DEFAULT_NAV_SQL_SERVER = "mf-ls-sql02.norwayeast.cloudapp.azure.com"
DEFAULT_NAV_SQL_DATABASE = "Megaflis_AS"
DEFAULT_NAV_SQL_DRIVER = "ODBC Driver 18 for SQL Server"
DEFAULT_CLOUDFLARE_ACCOUNT_ID = "4b045f1e830bb6bad28e4d91716a3a0c"
DEFAULT_R2_BUCKET_NAME = "hibernian-beta-data"
DEFAULT_R2_PUBLIC_BASE_URL = "https://pub-a1dbb638fdc8455c914f9f6c5f5b4564.r2.dev"
DEFAULT_R2_OBJECT_PREFIX = "latest"


@dataclass(frozen=True)
class PipelinePaths:
    pipeline_root: Path
    config_dir: Path
    artifacts_raw_dir: Path
    artifacts_state_dir: Path
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
            self.artifacts_state_dir,
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
    nav_store_sql_file: Path
    nav_seller_sql_file: Path
    stock_source: Path
    orders_source: Path
    historical_store_day: Path
    historical_seller_day: Path
    nav_store_day_raw: Path
    nav_seller_day_raw: Path
    stock_raw: Path
    orders_raw: Path
    store_day_base_snapshot: Path
    seller_day_base_snapshot: Path
    refresh_state_file: Path
    store_day_publish: Path
    seller_day_publish: Path
    stock_publish: Path
    meta_publish: Path
    nav_product_sql_file: Path | None = None
    nav_product_day_raw: Path | None = None
    product_history_base_snapshot: Path | None = None
    product_history_publish: Path | None = None
    product_day_publish: Path | None = None
    trailing_refresh_days: int = 7
    product_refresh_days: int = 2
    backfill_start_date: int | None = None
    product_backfill_start_date: int = 20250101
    nav_sql_server: str = DEFAULT_NAV_SQL_SERVER
    nav_sql_database: str = DEFAULT_NAV_SQL_DATABASE
    nav_sql_driver: str = DEFAULT_NAV_SQL_DRIVER
    nav_sql_use_snapshot_isolation: bool = True
    cloudflare_account_id: str = DEFAULT_CLOUDFLARE_ACCOUNT_ID
    r2_bucket_name: str = DEFAULT_R2_BUCKET_NAME
    r2_public_base_url: str = DEFAULT_R2_PUBLIC_BASE_URL
    r2_object_prefix: str = DEFAULT_R2_OBJECT_PREFIX

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
        artifacts_state_dir=pipeline_root / "artifacts" / "state",
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

    def resolve_bool(key: str, default: bool) -> bool:
        raw = values.get(key)
        if raw is None:
            return default
        if isinstance(raw, bool):
            return raw
        return str(raw).strip().lower() in {"1", "true", "yes", "on"}

    def resolve_optional_int(key: str) -> int | None:
        raw = os.environ.get(key)
        if raw in (None, ""):
            raw = values.get(key)
        if raw in (None, ""):
            return None
        return int(raw)

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
        nav_store_sql_file=resolve_path("nav_store_sql_file", paths.sql_sales_dir / "nav_store_day_window.sql"),
        nav_seller_sql_file=resolve_path("nav_seller_sql_file", paths.sql_sales_dir / "nav_seller_day_window.sql"),
        stock_source=resolve_path("stock_source", DEFAULT_STOCK_SOURCE),
        orders_source=resolve_path("orders_source", DEFAULT_ORDERS_SOURCE),
        historical_store_day=resolve_path("historical_store_day", paths.artifacts_raw_dir / "historical_store_day.json"),
        historical_seller_day=resolve_path("historical_seller_day", paths.artifacts_raw_dir / "historical_seller_day.json"),
        nav_store_day_raw=resolve_path("nav_store_day_raw", paths.artifacts_raw_dir / "nav_store_day_raw.json"),
        nav_seller_day_raw=resolve_path("nav_seller_day_raw", paths.artifacts_raw_dir / "nav_seller_day_raw.json"),
        stock_raw=resolve_path("stock_raw", paths.artifacts_raw_dir / "stock_raw.json"),
        orders_raw=resolve_path("orders_raw", paths.artifacts_raw_dir / "orders_raw.json"),
        store_day_base_snapshot=resolve_path(
            "store_day_base_snapshot",
            paths.artifacts_state_dir / "store_day_base_snapshot.json",
        ),
        seller_day_base_snapshot=resolve_path(
            "seller_day_base_snapshot",
            paths.artifacts_state_dir / "seller_day_base_snapshot.json",
        ),
        refresh_state_file=resolve_path(
            "refresh_state_file",
            paths.artifacts_state_dir / "refresh_state.json",
        ),
        store_day_publish=resolve_path("store_day_publish", paths.artifacts_publish_dir / "store_day.json"),
        seller_day_publish=resolve_path("seller_day_publish", paths.artifacts_publish_dir / "seller_day.json"),
        stock_publish=resolve_path("stock_publish", paths.artifacts_publish_dir / "stock.json"),
        meta_publish=resolve_path("meta_publish", paths.artifacts_publish_dir / "meta.json"),
        nav_product_sql_file=resolve_path("nav_product_sql_file", paths.sql_sales_dir / "nav_product_day_window.sql"),
        nav_product_day_raw=resolve_path("nav_product_day_raw", paths.artifacts_raw_dir / "nav_product_day_raw.json"),
        product_history_base_snapshot=resolve_path(
            "product_history_base_snapshot",
            paths.artifacts_state_dir / "product_history_base_snapshot.json",
        ),
        product_history_publish=resolve_path(
            "product_history_publish",
            paths.artifacts_publish_dir / "product_history.json",
        ),
        product_day_publish=resolve_path(
            "product_day_publish",
            paths.artifacts_publish_dir / "product_day.json",
        ),
        trailing_refresh_days=int(values.get("trailing_refresh_days", 7)),
        product_refresh_days=int(values.get("product_refresh_days", 2)),
        backfill_start_date=resolve_optional_int("backfill_start_date"),
        product_backfill_start_date=int(values.get("product_backfill_start_date", 20250101)),
        nav_sql_server=values.get("nav_sql_server", DEFAULT_NAV_SQL_SERVER),
        nav_sql_database=values.get("nav_sql_database", DEFAULT_NAV_SQL_DATABASE),
        nav_sql_driver=values.get("nav_sql_driver", DEFAULT_NAV_SQL_DRIVER),
        nav_sql_use_snapshot_isolation=resolve_bool("nav_sql_use_snapshot_isolation", True),
        cloudflare_account_id=values.get("cloudflare_account_id", DEFAULT_CLOUDFLARE_ACCOUNT_ID),
        r2_bucket_name=values.get("r2_bucket_name", DEFAULT_R2_BUCKET_NAME),
        r2_public_base_url=values.get("r2_public_base_url", DEFAULT_R2_PUBLIC_BASE_URL),
        r2_object_prefix=values.get("r2_object_prefix", DEFAULT_R2_OBJECT_PREFIX),
    )
