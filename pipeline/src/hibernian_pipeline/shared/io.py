from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
from typing import Any

_INVALID_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1F\x7F]")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    text = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = _INVALID_CONTROL_CHARS_RE.sub("", text)
        return json.loads(cleaned)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def copy_file(source: Path, destination: Path) -> None:
    ensure_parent(destination)
    shutil.copy2(source, destination)
