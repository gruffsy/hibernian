import json
from collections import defaultdict
from pathlib import Path

# Define a function to format a value as a currency string


def format_currency(value):
    return f"{int(value):,}".replace(",", " ") + " kr"


def format_integer(value):
    return f"{int(value):,}".replace(",", " ")


# Load the JSON file
source_file = Path("../jsons/sales_years_no_format.json")
with source_file.open("r", encoding="utf-8") as f:
    data = json.load(f)

for d in data:
    # Convert values to a currency string
    d["mmoms"] = format_currency(d["mmoms"])
    d["umoms"] = format_currency(d["umoms"])
    d["db"] = format_currency(d["db"])
    d["prord"] = format_currency(d["prord"])
    d["antord"] = format_integer(d["antord"])
    d["dg"] = "{:.1%}".format(d["dg"])


# Sort the data
# data = sorted(data, key=lambda x: (-x['year'], -x['month'], int(x['Klient'])))
data = sorted(data, key=lambda x: (-x['year'], int(x['Klient']) if x['Klient'] is not None else 0))



# Write the result to a new JSON file
with open("../publish/salg_fra_22_pr_aar_med_total.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
