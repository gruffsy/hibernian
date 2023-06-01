import pyodbc
import json

# Replace with your actual SQL Server details
server = "DB-HIB"
# database = "<database>"
username = "sa"
password = "VismaVudAdmin123@"
# table = "<table>"

# Connect to the SQL Server
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};UID={username};PWD={password}"
conn = pyodbc.connect(connection_string)

# Run the SELECT clause
query = '''
SET DATEFIRST 1;

select
    CASE DATEPART(WEEKDAY,dato) 
            WHEN 1 THEN 'Mandag' 
            WHEN 2 THEN 'Tirsdag' 
            WHEN 3 THEN 'Onsdag' 
            WHEN 4 THEN 'Torsdag' 
            WHEN 5 THEN 'Fredag' 
            WHEN 6 THEN 'Lørdag' 
            WHEN 7 THEN 'Søndag' 
        END 'ukedag',
    selger as navn,
    cast(totalt as int) AS 'umoms',
    cast(db as int) AS 'db',
    butikk,
    CONVERT(INT, CONVERT(VARCHAR, dato, 112)) as 'fakturadato'
    
from 
    f0004.dbo.SALG_PR_SELGER
order by
    dato desc,
    totalt desc

'''


cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Convert rows to a list of dictionaries
result = [dict(zip(column_names, row)) for row in rows]

# Save the result as JSON
with open("../jsons/visma_salg_pr_selger_fra_22.json", "w") as output_file:
    json.dump(result, output_file, default=str, indent=4)

# Close the connection
cursor.close()
conn.close()
