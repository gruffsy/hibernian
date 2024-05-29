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
select
[Item No_],
items.[Description],
items.[Unit Cost],
items.[Indirect Cost _],
items.[Last Direct Cost],
[Reason Code bdg],
[Posting Date],
[Location Code],
Quantity,
ile1.[Entry No_],
Positive,

[Comment bdg] as Comment,
[StaffId bdg] as StaffID
from [Hibernian Retail$Item Ledger Entry$437dbf0e-84ff-417a-965d-ed2bb9650972] ile1
inner join [Hibernian Retail$Item Ledger Entry$64848631-618b-42d9-91c4-5fffcbea6f69] ile2 on ile1.[Entry No_] = ile2.[Entry No_]
left join mf_items items on ile1.[Item No_] = items.No_
where 
[Entry Type] = 3
and [Posting Date] > '2024-05-01'
and [Entry No_] <> '678658'
"""

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("../csv/nedjustering.csv", "w", newline="") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    # Write the column headers
    writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()
