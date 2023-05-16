import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from calendar import monthrange

# Load the JSON file
source_file = Path("../jsons/salg_fra_22_pr_dag_med_total_no_format.json")
with source_file.open(encoding="utf-8") as f:
    data = json.load(f)


# Get today's date
today = datetime.now()

# Determine whether the current month is incomplete
is_current_month_incomplete = today.day != monthrange(today.year, today.month)[1]


# Create a dictionary to hold the aggregated data
aggregated_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

# List of keys to aggregate
aggregate_keys = ["mmoms", "umoms", "db", "antord"]

# Create a new list to hold the data before aggregation
before_aggregation = []

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

    # Append the item to the list before aggregation
    before_aggregation.append(item)

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

# After the loop, write the list to the file
before_aggregate_file = source_file.parent / "sales_days_no format.json"
with before_aggregate_file.open("w") as f:
    json.dump(before_aggregation, f, indent=4)

# Convert the aggregated data to a list
result = []
for key, value in aggregated_data.items():
    year, month, klient = key
    value.update({"year": year, "month": month, "Klient": klient})
    result.append(value)

# Save the aggregated result to a new JSON file
output_file = source_file.parent / "sales_months_no_format.json"
with output_file.open("w", encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

# Get the current year
this_year = datetime.now().year
# Define last year as the current year minus 1
last_year = this_year - 1

# Split the data into last year and this year
data_last_year = [item for item in result if item['year'] == last_year]
data_this_year = [item for item in result if item['year'] == this_year]

# Create a dictionary for easy access to last year's data
data_last_year_dict = {(item['month'], item['Klient']): item for item in data_last_year}

# Initialize the results list
comparison_results = []

# Loop over this year's data
for item_this_year in data_this_year:
    # Find the corresponding last year's data
    key = (item_this_year['month'], item_this_year['Klient'])
    if key in data_last_year_dict:
        item_last_year = data_last_year_dict[key]
        
        # Initialize a new dictionary to hold the comparison results
        comparison = {'year': this_year, 'month': item_this_year['month'], 'Klient': item_this_year['Klient'], 'butikk': item_this_year['butikk'], 'incomplete': item_this_year['incomplete']}
        
        # Calculate the difference for each key and store in the comparison dictionary
        for k in aggregate_keys + ['dg', 'prord']:
            comparison[k] = item_this_year[k] - item_last_year.get(k, 0)
        
        # Append the comparison to the results list
        comparison_results.append(comparison)

# Save the comparison results to a new JSON file
comparison_file = source_file.parent / "sales_comparison_full_month_no_format.json"
with comparison_file.open("w") as f:
    json.dump(comparison_results, f, indent=4)

