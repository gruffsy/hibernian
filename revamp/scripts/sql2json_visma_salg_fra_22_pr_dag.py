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
SELECT 
  fakturadato,
  butikk,
  Klient,
  CAST(sum(m_mva) AS INT) AS 'mmoms',
  CAST(sum(u_mva) AS INT) AS 'umoms',
  CAST(sum(u_mva - kostnad) AS INT) AS 'db',
  CAST(ROUND(sum(u_mva - kostnad)/sum(u_mva),2) AS FLOAT) as 'dg',
  count(distinct Ordrenummer) as 'antord',
  CAST((sum(m_mva)/count(distinct Ordrenummer)) AS INT) as 'prord'
FROM f0001.dbo.PRODUKTRANSER_ALLE
WHERE 
  fakturadato BETWEEN '20220101' AND convert(varchar, getdate(), 112)
  AND Fakturadato <> 0
  AND transaksjonstype = 1
  AND Ordretype = 3
  and antall <> 0
  and produktnr <> 'a1'
  and Kundeprisgruppe <> 4
GROUP BY
  fakturadato,
  butikk,
  Klient 
order by
fakturadato,
klient

'''


cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Convert rows to a list of dictionaries
result = [dict(zip(column_names, row)) for row in rows]

# Save the result as JSON
with open("../jsons/visma_salg_fra_22.json", "w", encoding="utf-8") as output_file:
    json.dump(result, output_file, default=str, indent=4, ensure_ascii=False)


# Close the connection
cursor.close()
conn.close()
