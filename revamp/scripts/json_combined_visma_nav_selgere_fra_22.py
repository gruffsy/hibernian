import json
from collections import defaultdict

# Define a function to format a value as a currency string


def format_currency(value):
    return f"{int(value):,}".replace(",", " ") + " kr"


def format_integer(value):
    return f"{int(value):,}".replace(",", " ")


# Combine data from File1.json and File2.json into a single list of dictionaries
with open("../jsons/visma_salg_pr_selger_fra_22.json", "r", encoding="utf-8") as f:
    file1_data = json.load(f)

with open("../jsons/nav_salg_pr_selger_fra_22.json", "r", encoding="utf-8") as f:
    file2_data = json.load(f)
combined_data = file1_data + file2_data


# Write the updated JSON string to CombinedFile.json
with open("../jsons/salg_pr_selger_fra_22_pr_dag.json", "w", encoding="utf-8" ) as f:
    json.dump(combined_data, f, indent=4, ensure_ascii=False)

# Read sales.json
with open("../jsons/salg_pr_selger_fra_22_pr_dag.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sort the data by fakturadato ascending and Klient descending
data.sort(key=lambda x: (-x["fakturadato"], int(-x["umoms"])))


with open("../jsons/salg_pr_selger_fra_22_pr_dag_no_format.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

for d in data:
    # Convert values to a currency string
    d["umoms"] = format_currency(d["umoms"])
    d["db"] = format_currency(d["db"])
    
# Write the result to a new JSON file
with open("../publish/salg_pr_selger_fra_22_pr_dag.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)
