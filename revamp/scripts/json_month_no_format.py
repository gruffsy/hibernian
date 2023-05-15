import json
from datetime import datetime
from pathlib import Path

# Load the JSON file
source_file = Path("../jsons/salg_fra_22_pr_dag_med_total_no_format.json")
with source_file.open() as f:
    data = json.load(f)

# Get today's date
today = datetime.now()

# Create a new list to hold the result
result = []

# Loop over the data
for item in data:
    # Convert fakturadato to a datetime object
    date = datetime.strptime(str(item['fakturadato']), '%Y%m%d')
    
    # Add new keys for year, month, date and incomplete
    item['year'] = date.year
    item['month'] = date.month
    item['date'] = date.day

    # If it's the current year and month, and the day is greater than today, 
    # set incomplete to True, otherwise set it to False
    if date.year == today.year and date.month == today.month and date.day >= today.day:
        item['incomplete'] = True
    else:
        item['incomplete'] = False

    # Append the item to the result
    result.append(item)


# Save the aggregated result to a new JSON file
output_file = source_file.parent / "sales_months_no_format.json"
with output_file.open("w") as f:
    json.dump(result, f, indent=4)
