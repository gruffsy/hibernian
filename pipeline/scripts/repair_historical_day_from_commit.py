from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


DATASETS = [
    {
        "name": "store_day",
        "reference_path": "legacy/frontend-static/data/publish/salg_fra_22_pr_dag_med_total.json",
        "targets": [
            ROOT / "pipeline" / "artifacts" / "publish" / "store_day.json",
            ROOT / "legacy" / "frontend-static" / "data" / "publish" / "salg_fra_22_pr_dag_med_total.json",
        ],
    },
    {
        "name": "seller_day",
        "reference_path": "legacy/frontend-static/data/publish/salg_pr_selger_fra_22_pr_dag.json",
        "targets": [
            ROOT / "pipeline" / "artifacts" / "publish" / "seller_day.json",
            ROOT / "legacy" / "frontend-static" / "data" / "publish" / "salg_pr_selger_fra_22_pr_dag.json",
        ],
    },
]


def read_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_reference(commit: str, relative_path: str) -> list[dict[str, Any]]:
    raw = subprocess.check_output(["git", "show", f"{commit}:{relative_path}"], cwd=ROOT, text=True)
    return json.loads(raw)


def replace_day(rows: list[dict[str, Any]], replacements: list[dict[str, Any]], date_key: int) -> list[dict[str, Any]]:
    return [row for row in rows if int(row.get("fakturadato", 0)) != date_key] + replacements


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", default="233f7d9")
    parser.add_argument("--date", type=int, required=True)
    args = parser.parse_args()

    for dataset in DATASETS:
        reference_rows = read_reference(args.commit, dataset["reference_path"])
        replacements = [row for row in reference_rows if int(row.get("fakturadato", 0)) == args.date]
        if not replacements:
            raise SystemExit(f"No {dataset['name']} rows found for {args.date} in {args.commit}")

        print(f"{dataset['name']}: replacement_rows={len(replacements)}")
        for target in dataset["targets"]:
            current_rows = read_json(target)
            fixed_rows = replace_day(current_rows, replacements, args.date)
            write_json(target, fixed_rows)
            print(f"wrote {target}")


if __name__ == "__main__":
    main()
