import json

# Define the file paths
json1_file = "../../json/lager_stock.sql.json"
json2_file = "../../json/bestillinger_stock.sql.json"
output_file = "../publish/merged_stock_orders.json"

# Load the data from JSON 1
with open(json1_file, "r") as file1:
    json1_data = json.load(file1)

# Load the data from JSON 2
with open(json2_file, "r") as file2:
    json2_data = json.load(file2)

# Convert json1_data to a dictionary for easier merging
json1_dict = {item["Prodno"]: item for item in json1_data}

# Merge data from json2_data into json1_dict
for item2 in json2_data:
    prodno = item2["Prodno"]
    if prodno in json1_dict:
        if "Bestilling på vei" not in json1_dict[prodno]:
            json1_dict[prodno]["Bestilling på vei"] = []
        json1_dict[prodno]["Bestilling på vei"].append({
            "Week_Year": item2["Week_Year"],
            "NoInvoAb": item2["NoInvoAb"]
        })

# Convert back to list format
merged_data = list(json1_dict.values())

# Save the merged data to a new file
with open(output_file, "w") as outfile:
    json.dump(merged_data, outfile, indent=4)

print(f"Merged data saved to {output_file}")
