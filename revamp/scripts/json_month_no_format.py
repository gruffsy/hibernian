import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from calendar import monthrange

# Load the JSON file
source_file = Path("../jsons/salg_fra_22_pr_dag_med_total_no_format.json")
with source_file.open() as f:
    data = json.load(f)

# Get today's date
today = datetime.now()

# Determine whether the current month is incomplete
is_current_month_incomplete = today.day != monthrange(today.year, today.month)[1]


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

    # If the item's year and month are the same as the current year and month,
    # set 'incomplete' based on whether the current month is incomplete
    if date.year == today.year and date.month == today.month:
        item["incomplete"] = is_current_month_incomplete
    else:
        item["incomplete"] = False

    # Write the intermediate data to a new JSON file
intermediate_file = source_file.parent / "sales_days_months_no_format.json"
with intermediate_file.open("w") as f:
    json.dump(data, f, indent=4)

    # Aggregate the sales by month, year, and klient
    key = (item["year"], item["month"], item["Klient"])
    for k in aggregate_keys:
        if k in aggregated_data[key]:
            aggregated_data[key][k] += item[k]
        else:
            aggregated_data[key][k] = item[k]
    if "butikk" not in aggregated_data[key]:
        aggregated_data[key]["butikk"] = item["butikk"]

    # If the item's month is incomplete, set the 'incomplete' key to True for the whole month
    if item["incomplete"]:
        aggregated_data[key]["incomplete"] = True
    elif "incomplete" not in aggregated_data[key]:
        aggregated_data[key]["incomplete"] = False

        # After the aggregation step, loop over the aggregated data to recalculate dg and prord, and set the incomplete key
for key in aggregated_data:
    aggregated_data[key]["dg"] = (
        aggregated_data[key]["db"] / aggregated_data[key]["umoms"]
        if aggregated_data[key]["umoms"] != 0
        else 0
    )
    aggregated_data[key]["prord"] = (
        aggregated_data[key]["umoms"] / aggregated_data[key]["antord"]
        if aggregated_data[key]["umoms"] != 0
        else 0
    )


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

