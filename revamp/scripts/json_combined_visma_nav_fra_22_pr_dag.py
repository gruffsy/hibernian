import json
from collections import defaultdict

# Define a function to format a value as a currency string


def format_currency(value):
    return f"{int(value):,}".replace(",", " ") + " kr"


def format_integer(value):
    return f"{int(value):,}".replace(",", " ")


# Combine data from File1.json and File2.json into a single list of dictionaries
with open("../jsons/visma_salg_fra_22.json", "r", encoding="utf-8") as f:
    file1_data = json.load(f)

with open("../jsons/nav_salg_fra_22.json", "r", encoding="utf-8") as f:
    file2_data = json.load(f)
combined_data = file1_data + file2_data


# Write the updated JSON string to CombinedFile.json
with open("../jsons/salg_fra_22_pr_dag.json", "w", encoding="utf-8" ) as f:
    json.dump(combined_data, f, indent=4, ensure_ascii=False)

# Read sales.json
with open("../jsons/salg_fra_22_pr_dag.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sum sales for each date
totals = defaultdict(lambda: {"mmoms": 0, "umoms": 0, "db": 0, "antord": 0})
for row in data:
    date = row["fakturadato"]
    totals[date]["mmoms"] += row["mmoms"]
    totals[date]["umoms"] += row["umoms"]
    totals[date]["db"] += row["db"]
    totals[date]["antord"] += row["antord"]

# Add total rows to the existing data
for date, total in totals.items():
    new_row = {
        "fakturadato": date,
        "butikk": "Totalt",
        "Klient": 99,  # set a higher Klient value so that it appears first when sorted
        "mmoms": total["mmoms"],
        "umoms": total["umoms"],
        "db": total["db"],
        "dg": total["db"] / total["umoms"] if total["umoms"] != 0 else 0,
        "antord": total["antord"],
        "prord": total["mmoms"] / total["antord"] if total["antord"] != 0 else 0,
    }
    data.append(new_row)


# Sort the data by fakturadato ascending and Klient descending
# data.sort(key=lambda x: (-x["fakturadato"], int(x["Klient"])))
data.sort(key=lambda x: (-x["fakturadato"], int(x["Klient"]) if x["Klient"] is not None else 0))


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
