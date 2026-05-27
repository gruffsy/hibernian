from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Iterable

import pyodbc

from ..settings import PipelineConfig


def read_sql_file(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def load_nav_sql_credentials() -> tuple[str, str]:
    username = os.getenv("HIBERNIAN_NAV_SQL_USERNAME") or os.getenv("NAV_SQL_USERNAME")
    password = os.getenv("HIBERNIAN_NAV_SQL_PASSWORD") or os.getenv("NAV_SQL_PASSWORD")
    if not username or not password:
        raise RuntimeError(
            "Missing NAV SQL credentials. Set HIBERNIAN_NAV_SQL_USERNAME and HIBERNIAN_NAV_SQL_PASSWORD."
        )
    return username, password


def run_nav_query(
    config: PipelineConfig,
    *,
    sql_file: Path,
    parameters: Iterable[Any],
) -> list[dict[str, Any]]:
    username, password = load_nav_sql_credentials()
    connection_string = (
        f"DRIVER={{{config.nav_sql_driver}}};"
        f"SERVER={config.nav_sql_server};"
        f"DATABASE={config.nav_sql_database};"
        f"UID={username};PWD={password};"
        "Encrypt=yes;TrustServerCertificate=yes"
    )

    sql_text = read_sql_file(sql_file)
    with pyodbc.connect(connection_string, autocommit=True) as connection:
        cursor = connection.cursor()
        if config.nav_sql_use_snapshot_isolation:
            cursor.execute("SET TRANSACTION ISOLATION LEVEL SNAPSHOT;")
        cursor.execute(sql_text, tuple(parameters))
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

    return [dict(zip(columns, row)) for row in rows]


def to_sql_date(yyyymmdd: int) -> str:
    return datetime.strptime(str(yyyymmdd), "%Y%m%d").strftime("%Y-%m-%d")
