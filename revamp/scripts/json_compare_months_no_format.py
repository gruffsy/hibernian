import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from calendar import monthrange

# Load the JSON file
file_path = Path('../jsons/sales_days_no format.json')
with file_path.open() as f:
    data = json.load(f)

# Initialize the data structure to store aggregated data
yearly_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

# Aggregate data by year and month
for record in data:
    date_str = str(record['fakturadato'])
    year = int(date_str[:4])
    month = int(date_str[4:6])
    store = record['butikk']

    # Here we're considering the fields: 'mmoms', 'umoms', 'db', 'antord', 'prord'
    # If there are more fields, add them in the list
    for field in ['mmoms', 'umoms', 'db', 'antord', 'prord']:
        yearly_data[year][month][store][field] += record[field]
        
    # For fields 'dg', we take the average.
    yearly_data[year][month][store]['dg'] = yearly_data[year][month][store].get('dg', 0) + \
                                            (record['dg'] - yearly_data[year][month][store].get('dg', 0)) / \
                                            (yearly_data[year][month][store]['antord'])

# Find the years present in the data
years = sorted(yearly_data.keys())

# Comparing the fields from each year to the previous year and creating a new record
comparison_data = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
for i in range(1, len(years)):
    current_year = years[i]
    prev_year = years[i-1]
    
    for month in range(1, 13):
        for store in yearly_data[current_year][month].keys():
            comparison_record = {}
            for field in ['mmoms', 'umoms', 'db', 'antord', 'prord', 'dg']:
                # Check if the data for the same month of the previous year exists, else take the value as 0
                prev_value = yearly_data[prev_year][month][store].get(field, 0)
                comparison_record[field] = yearly_data[current_year][month][store][field] - prev_value
            
            comparison_data[current_year][month][store] = comparison_record

# Print out the comparison data
for year, months_data in comparison_data.items():
    for month, stores_data in months_data.items():
        for store, record in stores_data.items():
            print(f'Year: {year}, Month: {month}, Store: {store}, Data: {record}')
