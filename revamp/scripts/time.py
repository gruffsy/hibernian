import pyodbc
import json

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

set
    nocount on
set
    noexec on

set
    noexec off

--  SELECT FORMAT (getdate(), 'HH:mm - dddd dd. MMMM yyyy', 'no-NO') as "oppdatert";

SELECT FORMAT(
  DATEADD(
    MINUTE,
    DATEDIFF((MINUTE, 0, GETDATE()) / 5 * 5) - 5,
    0
  ),
  'HH:mm - dddd dd. MMMM yyyy',
  'no-NO'
) AS "oppdatert";

"""

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]
print(rows)
column_names = [column[0] for column in cursor.description]

# Convert rows to a list of dictionaries
result = [dict(zip(column_names, row)) for row in rows]

# Save the result as JSON
with open("../publish/tid.json", "w") as output_file:
    json.dump(result, output_file, default=str, indent=4)

# Close the connection
cursor.close()
conn.close()

