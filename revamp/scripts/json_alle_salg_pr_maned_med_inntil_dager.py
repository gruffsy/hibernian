import json
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# Load the JSON file
source_file = Path("../jsons/salg_fra_22_pr_dag_med_total_no_format.json")
with source_file.open() as f:
    data = json.load(f)

# Prepare the data structure for the aggregated results
monthly_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

# Get today's date
today = datetime.now()

# Aggregate the data by month and butikk
for entry in data:
    date = str(entry["fakturadato"])
    year = date[:4]
    month = date[4:6]
    day = date[6:]
    butikk = entry["butikk"]
    klient = entry["Klient"]
    key = f"{year}-{month}"

    monthly_data[key][butikk]["mmoms"] += entry["mmoms"]
    monthly_data[key][butikk]["umoms"] += entry["umoms"]
    monthly_data[key][butikk]["db"] += entry["db"]
    monthly_data[key][butikk]["antord"] += entry["antord"]
    monthly_data[key][butikk]["Klient"] = klient

    # Update the "until_" keys if the date is within the current day of the month
    if int(day) <= today.day:
        monthly_data[key][butikk]["until_mmoms"] += entry["mmoms"]
        monthly_data[key][butikk]["until_umoms"] += entry["umoms"]
        monthly_data[key][butikk]["until_db"] += entry["db"]
        monthly_data[key][butikk]["until_antord"] += entry["antord"]

# Convert the defaultdict to a list of dicts in the requested format
result = []
for year_month, butikk_data in monthly_data.items():
    year, month = year_month.split("-")
    for butikk, values in butikk_data.items():
        mmoms = values["mmoms"]
        umoms = values["umoms"]
        db = values["db"]
        antord = values["antord"]
        dg = round(db / umoms, 2) if umoms != 0 else 0
        prord = round(mmoms / antord) if antord != 0 else 0

        result.append({
            "year": int(year),
            "month": int(month),
            "butikk": butikk,
            "mmoms": mmoms,
            "umoms": umoms,
            "db": db,
            "antord": antord,
            "Klient": values["Klient"],
            "dg": dg,
            "prord": prord,
            "until_mmoms": values["until_mmoms"],
            "until_umoms": values["until_umoms"],
            "until_db": values["until_db"],
            "until_antord": values["until_antord"]
        })

# Save the aggregated result to a new JSON file
output_file = source_file.parent / "json_alle_salg_pr_maned_med_inntil_dager.json"
with output_file.open("w") as f:
    json.dump(result, f, indent=4)
