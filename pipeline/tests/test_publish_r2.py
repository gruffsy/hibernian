from pathlib import Path

from hibernian_pipeline.publish.r2 import describe_step
from hibernian_pipeline.settings import load_config


def test_publish_r2_outputs_match_expected_remote_names() -> None:
    pipeline_root = Path(__file__).resolve().parents[1]
    config = load_config(pipeline_root)

    step = describe_step(config)

    assert step.name == "publish_r2"
    assert any(output.endswith("/latest/salg_fra_22_pr_dag_med_total.json") for output in step.outputs)
    assert any(output.endswith("/latest/salg_pr_selger_fra_22_pr_dag.json") for output in step.outputs)
    assert any(output.endswith("/latest/merged_stock_orders.json") for output in step.outputs)
    assert any(output.endswith("/latest/tid.json") for output in step.outputs)
