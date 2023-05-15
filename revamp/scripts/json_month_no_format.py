import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Load the JSON file
source_file = Path("../jsons/salg_fra_22_pr_dag_med_total_no_format.json")
with source_file.open() as f:
    data = json.load(f)

# Get today's date
today = datetime.now()

# Create a dictionary to hold the aggregated data
aggregated_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

# List of keys to aggregate
aggregate_keys = ["mmoms", "umoms", "db", "antord"]

# Loop over the data
for item in data:
    # Convert fakturadato to a datetime object
    date = datetime.strptime(str(item["fakturadato"]), "%Y%m%d")

    # Add new keys for year, month, date and incomplete
    item["year"] = date.year
    item["month"] = date.month
    item["date"] = date.day

    # If it's the current year and month, and the day is greater than today,
    # set incomplete to True, otherwise set it to False
    if date.year == today.year and date.month == today.month and date.day >= today.day:
        item["incomplete"] = True
    else:
        item["incomplete"] = False

    # Aggregate the sales by month, year, and klient
    key = (item["year"], item["month"], item["Klient"])
    for k in aggregate_keys:
        if k in aggregated_data[key]:
            aggregated_data[key][k] += item[k]
        else:
            aggregated_data[key][k] = item[k]
    if "butikk" not in aggregated_data[key]:
        aggregated_data[key]["butikk"] = item["butikk"]

    # If the month is incomplete, set the 'incomplete' key to True for the whole month
    if item["incomplete"]:
        aggregated_data[key]["incomplete"] = True
    elif "incomplete" not in aggregated_data[key]:
        aggregated_data[key]["incomplete"] = False

# Convert the aggregated data to a list
result = []
for key, value in aggregated_data.items():
    year, month, klient = key
    value.update({"year": year, "month": month, "Klient": klient})
    result.append(value)

# Save the aggregated result to a new JSON file
output_file = source_file.parent / "sales_months_no_format.json"
with output_file.open("w") as f:
    json.dump(result, f, indent=4)
