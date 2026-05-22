from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from ..settings import PipelineConfig
from ..shared.io import write_json
from ..shared.models import PipelineStep

OSLO_TZ = ZoneInfo("Europe/Oslo")
WEEKDAY_NAMES = {
    0: "mandag",
    1: "tirsdag",
    2: "onsdag",
    3: "torsdag",
    4: "fredag",
    5: "lørdag",
    6: "søndag",
}
MONTH_NAMES = {
    1: "januar",
    2: "februar",
    3: "mars",
    4: "april",
    5: "mai",
    6: "juni",
    7: "juli",
    8: "august",
    9: "september",
    10: "oktober",
    11: "november",
    12: "desember",
}


def planned_output(config: PipelineConfig) -> Path:
    return config.meta_publish


def describe_step(config: PipelineConfig) -> PipelineStep:
    return PipelineStep(
        name="extract_meta",
        description="Build metadata for last successful update.",
        outputs=(str(planned_output(config)),),
    )


def format_update_timestamp(moment: datetime) -> str:
    rounded_minute = (moment.minute // 5) * 5
    rounded = moment.replace(minute=rounded_minute, second=0, microsecond=0)
    weekday = WEEKDAY_NAMES[rounded.weekday()]
    month = MONTH_NAMES[rounded.month]
    return f"{rounded:%H:%M} - {weekday} {rounded.day}. {month} {rounded.year}"


def build_meta_payload(moment: datetime | None = None) -> list[dict[str, str]]:
    current = moment.astimezone(OSLO_TZ) if moment else datetime.now(OSLO_TZ)
    return [{"oppdatert": format_update_timestamp(current)}]


def run(config: PipelineConfig) -> list[dict[str, str]]:
    payload = build_meta_payload()
    write_json(planned_output(config), payload)
    return payload
