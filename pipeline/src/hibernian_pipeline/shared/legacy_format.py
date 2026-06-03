from __future__ import annotations

import re
from typing import Any

TOTAL_STORE_NAME = "Totalt"
TOTAL_CLIENT = "99"

_NUMBER_CLEANUP_RE = re.compile(r"[^\d,.\-]")


def _legacy_mojibake(text: str) -> str:
    for encoding in ("cp1252", "latin-1"):
        try:
            return text.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return text


_TEXT_FIXES = {
    "T\uFFFDnsberg": "Tønsberg",
    "TÃ¸nsberg": "Tønsberg",
    "LÃ¸rdag": "Lørdag",
    "SÃ¸ndag": "Søndag",
    "BelÃ¸p": "Beløp",
    "FrÃ¸itland": "Frøitland",
    "LillestÃ¸": "Lillestø",
}


def _repair_mojibake(text: str) -> str:
    if not any(marker in text for marker in ("\u00C3", "\u00C2")):
        return text

    for encoding in ("latin-1", "cp1252"):
        try:
            repaired = text.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if repaired != text:
            text = repaired
            break

    return text


def normalize_text(value: Any) -> str:
    text = str(value or "").strip()
    text = _repair_mojibake(text)
    for wrong, correct in _TEXT_FIXES.items():
        text = text.replace(wrong, correct)
    return " ".join(text.split())


def parse_date(value: Any) -> int:
    if value is None or value == "":
        raise ValueError("Missing fakturadato")
    if isinstance(value, int):
        return value
    digits = re.sub(r"\D", "", str(value))
    if len(digits) != 8:
        raise ValueError(f"Invalid fakturadato: {value!r}")
    return int(digits)


def parse_number(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    raw = str(value).strip()
    if not raw:
        return 0.0

    cleaned = _NUMBER_CLEANUP_RE.sub("", raw)
    if not cleaned or cleaned in {"-", ".", ","}:
        return 0.0

    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    return float(cleaned)


def parse_ratio(value: Any) -> float:
    ratio = parse_number(value)
    if isinstance(value, str) and "%" in value:
        return ratio / 100
    return ratio


def format_currency(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", " ") + " kr"


def format_integer(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", " ")


def format_percentage(value: float) -> str:
    return f"{value:.1%}"
