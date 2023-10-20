import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Load the JSON file
source_file = Path("../jsons/salg_fra_22_pr_dag_med_total_no_format.json")
with source_file.open(encoding="utf-8") as f:
    data = json.load(f)

# Get today's date
today = datetime.now()

# Create a dictionary to hold the aggregated data by year
aggregated_data_by_year = defaultdict(lambda: defaultdict(dict))

# List of keys to aggregate
aggregate_keys = ["mmoms", "umoms", "db", "antord"]

# Loop over the data
for item in data:
    # Convert fakturadato to a datetime object
    date = datetime.strptime(str(item["fakturadato"]), "%Y%m%d")
    item["year"] = date.year  # Add new key for year

    # Aggregate the sales by year and klient
    key = (item["year"], item["Klient"])
    for k in aggregate_keys:
        if k in aggregated_data_by_year[key]:
            aggregated_data_by_year[key][k] += item[k]
        else:
            aggregated_data_by_year[key][k] = item[k]
            
    if "butikk" not in aggregated_data_by_year[key]:
        aggregated_data_by_year[key]["butikk"] = item["butikk"]

    # Determine if the year is incomplete
    if item["year"] == today.year:
        aggregated_data_by_year[key]["incomplete"] = today.month != 12 or today.day != 31
    else:
        aggregated_data_by_year[key]["incomplete"] = False

# Recalculate dg and prord
for key in aggregated_data_by_year:
    aggregated_data_by_year[key]["dg"] = (
        aggregated_data_by_year[key]["db"] / aggregated_data_by_year[key]["umoms"]
        if aggregated_data_by_year[key]["umoms"] != 0
        else 0
    )
    aggregated_data_by_year[key]["prord"] = (
        aggregated_data_by_year[key]["mmoms"] / aggregated_data_by_year[key]["antord"]
        if aggregated_data_by_year[key]["mmoms"] != 0
        else 0
    )

# Convert the aggregated data to a list
result_by_year = []
for key, value in aggregated_data_by_year.items():
    year, klient = key
    value.update({"year": year, "Klient": klient})
    result_by_year.append(value)

# Save the aggregated result to a new JSON file
output_file_by_year = source_file.parent / "sales_years_no_format.json"
with output_file_by_year.open("w", encoding="utf-8") as f:
    json.dump(result_by_year, f, indent=4, ensure_ascii=False)
