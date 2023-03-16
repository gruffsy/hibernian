import json
import codecs

# Define a function to format a value as a currency string
def format_currency(value):
    return f"{int(value):,}".replace(",", " ") + " kr"


def format_integer(value):
    return f"{int(value):,}".replace(",", " ")


# Combine data from File1.json and File2.json into a single list of dictionaries
with codecs.open("json/visma.sql.json", "r", encoding="utf-8-sig") as f:
    file1_data = json.load(f)

with open("bamble.json", "r") as f:
    file2_data = json.load(f)
combined_data = file1_data + file2_data

# Calculate the total sales amount and add a total row to the list of dictionaries
total_mmoms = sum([d["mmoms"] for d in combined_data])
total_umoms = sum(d["mmoms"] / 1.25 for d in combined_data)
total_db = sum([d["db"] for d in combined_data])
total_dg = None
if total_db != 0:
    total_dg = total_db / total_umoms
total_antord = sum([d["antord"] for d in combined_data])
if total_antord != 0:
    total_prord = total_mmoms / total_antord

total_row = {
    "butikk": "Total",
    "Klient": 999,
    "mmoms": total_mmoms,
    "umoms": total_umoms,
    "db": total_db,
    "dg": total_dg,
    "antord": total_antord,
    "prord": total_prord,
}

combined_data.append(total_row)

# Loop through the list of dictionaries and convert Sales and Discount values to formatted currency strings
for d in combined_data:
    # Convert values to a currency string
    d["mmoms"] = format_currency(d["mmoms"])
    d["umoms"] = format_currency(d["umoms"])
    d["db"] = format_currency(d["db"])
    d["prord"] = format_currency(d["prord"])
    d["antord"] = format_integer(d["antord"])
    d["dg"] = "{:.1%}".format(d["dg"])
  


# Write the updated JSON string to CombinedFile.json
with open("json/kombinertSalg.json", "w") as f:
    json.dump(combined_data, f, indent=4, ensure_ascii=False)
