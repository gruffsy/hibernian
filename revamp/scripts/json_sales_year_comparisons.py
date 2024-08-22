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
data.sort(key=lambda x: x["fakturadato"])
latest_date = str(data[-1]["fakturadato"])

# Get the year, month and day of the latest date
latest_year = int(latest_date[:4])
latest_month = int(latest_date[4:6])
latest_day = int(latest_date[6:])

# Initialize the data structure to store aggregated data and the days with sales
yearly_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
sales_days = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
store_clients = defaultdict(dict)  # Track 'Klient' for each store and year

# Aggregate data by year, month, and day
for record in data:
    date_str = str(record['fakturadato'])
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:])
    
    store = record['butikk']
    store_clients[year][store] = record['Klient']  # Store 'Klient' information for each store

    # Aggregating relevant fields
    for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']:
        yearly_data[year][month][store][field] += record[field]
    
    # For fields 'dg', take the average
    if 'dg' in record:
        yearly_data[year][month][store]['dg'] = yearly_data[year][month][store].get('dg', 0) + \
                                                (record['dg'] - yearly_data[year][month][store].get('dg', 0)) / \
                                                (yearly_data[year][month][store]['antord'])
                                            
    sales_days[year][month][store].add(day)

# Find the years present in the data
years = sorted(yearly_data.keys())

# Comparing the fields from each year to the previous year and creating a new record for monthly comparison
comparison_data = []
for i in range(1, len(years)):
    current_year = years[i]
    prev_year = years[i-1]

    for month in range(1, 13):
        # For the latest month, generate two comparisons
        if month == latest_month and current_year == latest_year:
            days_to_include = [latest_day, monthrange(current_year, month)[1]]
        else:
            days_to_include = [monthrange(current_year, month)[1]]

        for day in days_to_include:
            for store, current_data in yearly_data[current_year][month].items():
                # Check if the data for the same month of the previous year exists, else assume as 0
                prev_data_full_month = yearly_data[prev_year][month].get(store, {field: 0 for field in ['mmoms', 'umoms', 'db', 'antord', 'prord', 'dg']})
                
                # Scale down the data for the previous year based on the number of days included
                prev_data = {field: value * day / monthrange(prev_year, month)[1] for field, value in prev_data_full_month.items()}

                comparison_record = {
                    "butikk": store,
                    "Klient": store_clients[current_year].get(store, "Unknown"),  # Use 'Klient' from store_clients
                    "last_year": prev_year,
                    "this_year": current_year,
                    "month": month,
                    "incomplete": day != monthrange(current_year, month)[1],
                }

                for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']:
                    comparison_record[field] = current_data[field] - prev_data[field]

                # Calculate profit margin change in percentage (handling missing 'dg')
                current_dg = current_data.get('dg', 0)
                prev_dg = prev_data.get('dg', 0)
                if prev_dg != 0:
                    comparison_record['dg'] = ((current_dg - prev_dg) / prev_dg) 
                else:
                    comparison_record['dg'] = 0

                comparison_data.append(comparison_record)

# Yearly comparison
for i in range(1, len(years)):
    current_year = years[i]
    prev_year = years[i-1]

    for store in set(yearly_data[current_year][latest_month].keys()) | set(yearly_data[prev_year][latest_month].keys()):
        current_data = {
            field: sum(yearly_data[current_year][month].get(store, {}).get(field, 0) for month in range(1, 13))
            for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']
        }
        prev_data = {
            field: sum(yearly_data[prev_year][month].get(store, {}).get(field, 0) for month in range(1, 13))
            for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']
        }

        yearly_comparison_record = {
            "butikk": store,
            "Klient": store_clients[current_year].get(store, "Unknown"),  # Use 'Klient' from store_clients
            "last_year": prev_year,
            "this_year": current_year,
            "year_comparison": True
        }

        for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']:
            yearly_comparison_record[field] = current_data[field] - prev_data[field]

        # Calculate profit margin change in percentage (handling missing 'dg')
        current_dg = current_data.get('dg', 0)
        prev_dg = prev_data.get('dg', 0)
        if prev_dg != 0:
            yearly_comparison_record['dg'] = ((current_dg - prev_dg) / prev_dg) 
        else:
            yearly_comparison_record['dg'] = 0

        comparison_data.append(yearly_comparison_record)

# Save the comparison data to a new JSON file
with open(source_file.parent / "sales_comparisons_year_vs_year.json", "w") as f:
    json.dump(comparison_data, f, indent=4)
