import pyodbc
import csv

# Replace with your actual SQL Server details
server = "mf-ls-sql02.norwayeast.cloudapp.azure.com"
database = "Megaflis_AS"
username = "perarne"
password = "AdaiQQvlq!#to43"
# table = "<table>"


# Connect to the SQL Server
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};Database={database};UID={username};PWD={password}"
conn = pyodbc.connect(connection_string)

# Run the SELECT clause
query = """
SELECT
    ilt.[Item No_] AS No_,
    il.[Location],
    il.[Phys_ Inventory] AS Inventory,
    ilt.[Saleable Quantity]
FROM [Hibernian Retail$LSC Inventory Lookup Table$5ecfc871-5d82-43f1-9c54-59685e82318d] il
    inner join
    [Hibernian Retail$LSC Inventory Lookup Table$64848631-618b-42d9-91c4-5fffcbea6f69] ilt
    on il.[Item No_] = ilt.[Item No_]
        and il.[Store No_]= ilt.[Store No_]
"""

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("../csv/stock.csv", "w", newline="") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    # Write the column headers
    writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()
