import json
from collections import defaultdict

# Define a function to format a value as a currency string


def format_currency(value):
    return f"{int(value):,}".replace(",", " ") + " kr"


def format_integer(value):
    return f"{int(value):,}".replace(",", " ")

# Read sales.json
with open("../jsons/sales_months_no_format.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sort the data by fakturadato ascending and Klient descending
data.sort(key=lambda x: (-x["fakturadato"], int(x["Klient"])))

with open("../jsons/salg_fra_22_pr_dag_med_total_no_format.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

for d in data:
    # Convert values to a currency string
    d["mmoms"] = format_currency(d["mmoms"])
    d["umoms"] = format_currency(d["umoms"])
    d["db"] = format_currency(d["db"])
    d["prord"] = format_currency(d["prord"])
    d["antord"] = format_integer(d["antord"])
    d["dg"] = "{:.1%}".format(d["dg"])

# Write the result to a new JSON file
with open("../publish/salg_fra_22_pr_dag_med_total.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
