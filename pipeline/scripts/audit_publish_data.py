from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline" / "src"))

from hibernian_pipeline.shared.legacy_format import normalize_text  # noqa: E402


def read_json(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_git_json(commit: str, relative_path: str) -> list[dict[str, Any]]:
    raw = subprocess.check_output(["git", "show", f"{commit}:{relative_path}"], cwd=ROOT, text=True)
    return json.loads(raw)


def parse_number(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    text = text.replace("kr", "").replace("%", "").replace("\xa0", " ")
    text = text.replace("−", "-").replace("–", "-")
    text = text.replace(" ", "").replace(",", ".").strip()
    return float(text) if text else 0.0


def audit_store(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_date: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_date[int(row["fakturadato"])].append(row)

    mismatches = []
    duplicate_keys = []
    for date_key, date_rows in by_date.items():
        keys = [(str(row.get("Klient")), row.get("butikk")) for row in date_rows]
        duplicates = [(key, count) for key, count in Counter(keys).items() if count > 1]
        if duplicates:
            duplicate_keys.append({"date": date_key, "duplicates": duplicates})

        totals = [row for row in date_rows if row.get("butikk") == "Totalt"]
        stores = [row for row in date_rows if row.get("butikk") != "Totalt"]
        if len(totals) != 1:
            mismatches.append({"date": date_key, "issue": "total_count", "count": len(totals)})
            continue

        total = totals[0]
        summed = {field: sum(parse_number(row[field]) for row in stores) for field in ("mmoms", "umoms", "db", "antord")}
        stated = {field: parse_number(total[field]) for field in ("mmoms", "umoms", "db", "antord")}
        diff = {field: round(summed[field] - stated[field], 2) for field in summed if abs(summed[field] - stated[field]) > 1}
        if diff:
            mismatches.append({"date": date_key, "diff": diff, "total": total})

    return {
        "name": name,
        "rows": len(rows),
        "dates": len(by_date),
        "total_mismatches": mismatches,
        "duplicate_keys": duplicate_keys,
    }


def audit_seller(name: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [(row.get("fakturadato"), row.get("butikk"), row.get("navn")) for row in rows]
    duplicates = [(key, count) for key, count in Counter(keys).items() if count > 1]
    by_date = Counter(int(row["fakturadato"]) for row in rows)
    return {
        "name": name,
        "rows": len(rows),
        "dates": len(by_date),
        "duplicate_keys": duplicates,
        "rows_per_date": dict(sorted(by_date.items(), reverse=True)),
    }


def compact_store_issue(issue: dict[str, Any]) -> dict[str, Any]:
    result = {"date": issue["date"]}
    if "issue" in issue:
        result["issue"] = issue["issue"]
        result["count"] = issue.get("count")
    if "diff" in issue:
        result["diff"] = issue["diff"]
        result["total_mmoms"] = issue["total"].get("mmoms")
    return result


def row_identity(row: dict[str, Any]) -> tuple[Any, ...]:
    if "navn" in row:
        return row.get("fakturadato"), normalize_text(row.get("butikk")), normalize_text(row.get("navn"))
    return row.get("fakturadato"), str(row.get("Klient")), normalize_text(row.get("butikk"))


def compare_historical_rows(
    *,
    name: str,
    reference_rows: list[dict[str, Any]],
    current_rows: list[dict[str, Any]],
    before_date: int,
) -> None:
    reference = {row_identity(row): row for row in reference_rows if int(row.get("fakturadato", 0)) < before_date}
    current = {row_identity(row): row for row in current_rows if int(row.get("fakturadato", 0)) < before_date}
    missing = sorted(set(reference) - set(current))
    extra = sorted(set(current) - set(reference))
    numeric_fields = ("umoms", "db") if name == "seller" else ("mmoms", "umoms", "db", "antord")
    changed = sorted(
        key
        for key in set(reference) & set(current)
        if any(abs(parse_number(reference[key].get(field)) - parse_number(current[key].get(field))) > 1 for field in numeric_fields)
    )

    print(f"\n{name}_row_drift_vs_233f7d9_before_{before_date}")
    print(f"missing={len(missing)} extra={len(extra)} changed={len(changed)}")
    if missing:
        print("first_missing", missing[:10])
    if extra:
        print("first_extra", extra[:10])
    if changed:
        print("first_changed", changed[:10])


def main() -> None:
    store_path = ROOT / "pipeline" / "artifacts" / "publish" / "store_day.json"
    seller_path = ROOT / "pipeline" / "artifacts" / "publish" / "seller_day.json"
    legacy_store_path = ROOT / "legacy" / "frontend-static" / "data" / "publish" / "salg_fra_22_pr_dag_med_total.json"
    legacy_seller_path = ROOT / "legacy" / "frontend-static" / "data" / "publish" / "salg_pr_selger_fra_22_pr_dag.json"

    datasets = [
        audit_store("pipeline_store", read_json(store_path)),
        audit_store("legacy_store", read_json(legacy_store_path)),
        audit_seller("pipeline_seller", read_json(seller_path)),
        audit_seller("legacy_seller", read_json(legacy_seller_path)),
    ]

    for dataset in datasets:
        print(f"\n{dataset['name']}")
        print(f"rows={dataset['rows']} dates={dataset['dates']}")
        if "total_mismatches" in dataset:
            mismatches = dataset["total_mismatches"]
            print(f"total_mismatches={len(mismatches)} duplicate_keys={len(dataset['duplicate_keys'])}")
            for issue in mismatches[:20]:
                print(compact_store_issue(issue))
        else:
            duplicates = dataset["duplicate_keys"]
            print(f"duplicate_keys={len(duplicates)}")
            print(f"20260515_rows={dataset['rows_per_date'].get(20260515, 0)}")

    reference_store = read_git_json("233f7d9", "legacy/frontend-static/data/publish/salg_fra_22_pr_dag_med_total.json")
    reference_seller = read_git_json("233f7d9", "legacy/frontend-static/data/publish/salg_pr_selger_fra_22_pr_dag.json")
    current_store = read_json(store_path)
    current_seller = read_json(seller_path)
    reference_by_date = defaultdict(list)
    current_by_date = defaultdict(list)
    for row in reference_store:
        reference_by_date[int(row["fakturadato"])].append(row)
    for row in current_store:
        current_by_date[int(row["fakturadato"])].append(row)

    changed_historical_dates = []
    for date_key in sorted(reference_by_date):
        if date_key >= 20260520:
            continue
        reference_total = [row for row in reference_by_date[date_key] if row.get("butikk") == "Totalt"]
        current_total = [row for row in current_by_date.get(date_key, []) if row.get("butikk") == "Totalt"]
        if reference_total != current_total:
            changed_historical_dates.append((date_key, reference_total[:1], current_total[:1]))

    print("\nhistorical_total_drift_vs_233f7d9_before_20260520")
    print(f"changed_dates={len(changed_historical_dates)}")
    for issue in changed_historical_dates[:20]:
        print(issue)

    compare_historical_rows(
        name="store",
        reference_rows=reference_store,
        current_rows=current_store,
        before_date=20260520,
    )
    compare_historical_rows(
        name="seller",
        reference_rows=reference_seller,
        current_rows=current_seller,
        before_date=20260520,
    )


if __name__ == "__main__":
    main()
