import json
import re
import json5

def clean_json_string(json_string):
    # Replace any invalid control characters with an empty string
    json_string = re.sub(r'[\x00-\x1F\x7F]', '', json_string)
    return json_string

def read_json_file(filename):
    with open(filename, "r", encoding="utf-8-sig") as file:
        content = file.read()

    # Sjekk om filen er tom
    if not content.strip():
        return []  # Returnerer en tom liste hvis filen er tom

    # Clean the JSON string from any invalid characters
    content = clean_json_string(content)

    # Use json5 for parsing, which is more tolerant
    return json5.loads(content)

def convert_to_utf8(filename, output_filename):
    """Converts a file from UTF-8 with BOM to standard UTF-8."""
    with open(filename, "r", encoding="utf-8-sig") as file:
        content = file.read()

    # Write the content back in standard UTF-8
    with open(output_filename, "w", encoding="utf-8") as outfile:
        outfile.write(content)

# Define the file paths
json1_input_file = "../../json/lager_stock.sql.json"
json2_input_file = "../../json/bestillinger_stock.sql.json"
json1_file = "../../json/lager_stock_utf8.json"
json2_file = "../../json/bestillinger_stock_utf8.json"
convert_to_utf8(json1_input_file, json1_file)
convert_to_utf8(json2_input_file, json2_file)

# Load the data from JSON 1
json1_data = read_json_file(json1_file)

# Load the data from JSON 2
json2_data = read_json_file(json2_file)

# Convert json1_data to a dictionary for easier merging
json1_dict = {item["Prodno"]: item for item in json1_data}

# Merge data from json2_data into json1_dict
for item2 in json2_data:
    prodno = item2["Prodno"]
    if prodno in json1_dict:
        if "Bestilling på vei" not in json1_dict[prodno]:
            json1_dict[prodno]["Bestilling på vei"] = []
        json1_dict[prodno]["Bestilling på vei"].append({
            "Ukenr": item2.get("Week_Year", "ukjent"),  # Bruker "ukjent" hvis 'Week_Year' ikke finnes
            "Antall": item2.get("NoInvoAb", 0)  # Bruker 0 hvis 'NoInvoAb' ikke finnes
        })

# Convert back to list format
merged_data = list(json1_dict.values())

# Define the output path
output_file = "../publish/merged_stock_orders.json"

# Save the merged data to a new file
with open(output_file, "w", encoding="utf-8") as outfile:
    json.dump(merged_data, outfile, indent=4, ensure_ascii=False)

print(f"Merged data saved to {output_file}")
