from __future__ import annotations

from pathlib import Path

from ..settings import PipelineConfig
from ..shared.io import copy_file
from ..shared.models import PipelineStep


def _publish_targets(config: PipelineConfig) -> dict[Path, Path]:
    return {
        config.store_day_publish: config.paths.legacy_publish_dir / "salg_fra_22_pr_dag_med_total.json",
        config.seller_day_publish: config.paths.legacy_publish_dir / "salg_pr_selger_fra_22_pr_dag.json",
        config.stock_publish: config.paths.legacy_publish_dir / "merged_stock_orders.json",
        config.meta_publish: config.paths.legacy_publish_dir / "tid.json",
    }


def publish_to_beta_static_copy(config: PipelineConfig) -> list[str]:
    copied: list[str] = []
    for source, destination in _publish_targets(config).items():
        if not source.exists():
            continue
        copy_file(source, destination)
        copied.append(f"{source} -> {destination}")
    return copied


def describe_step(config: PipelineConfig) -> PipelineStep:
    targets = _publish_targets(config)
    return PipelineStep(
        name="publish_local",
        description="Copy publish artifacts into the beta app's local static data folder.",
        inputs=tuple(str(source) for source in targets),
        outputs=tuple(str(destination) for destination in targets.values()),
    )
