import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from calendar import monthrange
import pytz

# Load the JSON file
source_file = Path("../jsons/salg_fra_22_pr_dag_med_total_no_format.json")
with source_file.open(encoding="utf-8") as f:
    data = json.load(f)

# Sort data by date to find the latest date
data.sort(key=lambda x: x['fakturadato'])
latest_date = str(data[-1]['fakturadato'])

# Get the year, month and day of the latest date
latest_year = int(latest_date[:4])
latest_month = int(latest_date[4:6])
latest_day = int(latest_date[6:])

# Get current time in Norway
now = datetime.now(pytz.timezone("Europe/Oslo"))

# If the current time in Norway is before 20:00, exclude the current day from the calculation
# unless it is the last day of the month or the last day is a Sunday
if now.hour < 20 and latest_day != monthrange(latest_year, latest_month)[1] and datetime(latest_year, latest_month, monthrange(latest_year, latest_month)[1]).weekday() != 6:
    latest_day -= 1

# Initialize the data structure to store aggregated data
yearly_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
sales_days = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))

# Aggregate data by year and month
for record in data:
    date_str = str(record['fakturadato'])
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:])
    
    store = record['butikk']

    # Here we're considering the fields: 'mmoms', 'umoms', 'db', 'antord', 'prord'
    # If there are more fields, add them in the list
    for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']:
        yearly_data[year][month][store][field] += record[field]
    
    # For fields 'dg', we take the average.
    yearly_data[year][month][store]['dg'] = yearly_data[year][month][store].get('dg', 0) + \
                                            (record['dg'] - yearly_data[year][month][store].get('dg', 0)) / \
                                            (yearly_data[year][month][store]['antord'] if yearly_data[year][month][store]['antord'] != 0 else 1)

    # Keep track of sales days
    sales_days[year][month][store].add(day)

# Get the total number of days in the latest month (excluding Sundays)
total_days = len([day for day in range(1, monthrange(latest_year, latest_month)[1] + 1) if datetime(latest_year, latest_month, day).weekday() != 6])

# Create the projection for the current month
sales_projection_data = []
for store, current_data in yearly_data[latest_year][latest_month].items():
    current_sales_days = len(sales_days[latest_year][latest_month][store])
    remaining_days = total_days - current_sales_days
    projection_record = {
        "butikk": store,
        "Klient": current_data["Klient"],
        "year": latest_year,
        "month": latest_month,
        "incomplete": True
    }
    for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']:
        daily_avg = current_data[field] / current_sales_days if current_sales_days != 0 else 0
        projection_record[field] = current_data[field] + daily_avg * remaining_days
    
    # Calculate profit margin projection
    projection_record['dg'] = projection_record['db'] / projection_record['mmoms'] if projection_record['mmoms'] != 0 else 0

    sales_projection_data.append(projection_record)

# Find the years present in the data
years = sorted(yearly_data.keys())

# Comparing the fields from each year to the previous year and creating a new record
comparison_data = []
for i in range(1, len(years)):
    current_year = years[i]
    prev_year = years[i - 1]

    for month in range(1, 13):
        for is_partial_month in [True, False]:
            if is_partial_month and (current_year != latest_year or month != latest_month):
                continue
            for store, current_data in yearly_data[current_year][month].items():
                days_to_compare = latest_day if is_partial_month else monthrange(current_year, month)[1]
                prev_data = yearly_data[prev_year][month].get(store, {field: 0 for field in ['mmoms', 'umoms', 'db', 'antord', 'prord', 'dg']})

                comparison_record = {
                    "butikk": store,
                    "Klient": current_data["Klient"],
                    "last_year": prev_year,
                    "this_year": current_year,
                    "month": month,
                    "incomplete": is_partial_month
                }

                for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']:
                    comparison_record[field] = current_data[field] - prev_data[field]

                # Calculate profit margin change in percentage
                if prev_data["dg"] != 0:
                    comparison_record["dg"] = (current_data["dg"] - prev_data["dg"]) / prev_data["dg"]
                else:
                    comparison_record["dg"] = 0

                comparison_data.append(comparison_record)


# Save the comparison data to a new JSON file
with open(source_file.parent / "sales_months_comparisons.json", "w") as f:
    json.dump(comparison_data, f, indent=4)
