import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from calendar import monthrange

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

# Aggregate data by year and month and track sales days
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
                                            (yearly_data[year][month][store]['antord'])
                                            
    sales_days[year][month][store].add(day)

# Find the years present in the data
years = sorted(yearly_data.keys())

# Comparing the fields from each year to the previous year and creating a new record
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
                    "Klient": current_data["Klient"],
                    "last_year": prev_year,
                    "this_year": current_year,
                    "month": month,
                    "incomplete": day != monthrange(current_year, month)[1],
                }

                for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']:
                    comparison_record[field] = current_data[field] - prev_data[field]

                # Calculate profit margin change in percentage
                if prev_data['dg'] != 0:
                    comparison_record['dg'] = ((current_data['dg'] - prev_data['dg']) / prev_data['dg']) 
                else:
                    comparison_record['dg'] = 0

                comparison_data.append(comparison_record)


from datetime import datetime
import pytz

# Get current time in Norway
now = datetime.now(pytz.timezone("Europe/Oslo"))

# If the current time in Norway is before 20:00, exclude the current day from the calculation
# unless it is the last day of the month or the last day is a Sunday
if now.hour < 20 and latest_day != monthrange(latest_year, latest_month)[1] and datetime(latest_year, latest_month, monthrange(latest_year, latest_month)[1]).weekday() != 6:
    latest_day -= 1

# Adding this right before saving data to the comparison JSON file
projected_records = []
if latest_day < monthrange(latest_year, latest_month)[1]:  # Only add a projection if the month is not yet complete
    for store, current_data in yearly_data[latest_year][latest_month].items():
        if current_data['antord'] == 0:  # Skip stores with no sales records for the month
            continue
        projected_record = {
            "butikk": store,
            "Klient": current_data['Klient'],
            "this_year": latest_year,
            "month": latest_month,
            "incomplete": None  # This is a projection, so it's technically incomplete
        }
        
        # Get the total number of days with sales for the current month so far (excluding Sundays)
        current_sales_days = len(sales_days[latest_year][latest_month][store])
        # Get the total number of sales days for the current month (excluding Sundays)
        projected_sales_days = sum(1 for day in range(1, monthrange(latest_year, latest_month)[1]+1) if datetime(latest_year, latest_month, day).weekday() < 6)
        
        # Project each field value based on the average daily sales
        for field in ['mmoms', 'umoms', 'db', 'antord']:
            daily_avg = current_data[field] / current_sales_days
            projected_value = daily_avg * projected_sales_days
            projected_record[field] = projected_value 
            
            #- current_data[field]
        
        # Assume the 'dg' field stays constant throughout the month
        projected_record['dg'] = projected_record['db'] / projected_record['umoms']
        projected_record['prord'] = projected_record['umoms'] / projected_record['antord']

        projected_records.append(projected_record)

comparison_data.extend(projected_records)


# Save the comparison data to a new JSON file
with open(source_file.parent / "sales_months_comparisons.json", "w") as f:
    json.dump(comparison_data, f, indent=4)
