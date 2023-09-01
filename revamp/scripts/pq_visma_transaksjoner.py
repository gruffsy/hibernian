import pyodbc
import csv

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
SELECT [Butikknr]
      ,[Fakturadato]
      ,[NAVnr]
      ,sum([Antall]) as Antall
      ,sum([u_mva]) as u_mva
      ,sum([m_mva]) as m_mva
      ,sum([kostnad]) as kostnad
      ,sum(u_mva - kostnad) as DB
  FROM [F0001].[dbo].[PRODUKTRANSER_ALLE]
  where 
    Transaksjonstype = 1
    and Fakturadato <> 0
    and NAVnr <> ''
Group By
    Butikknr,
    Fakturadato,
    NAVnr,
    


'''


cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("../csv/pq_visma_transaksjoner.csv", "w", newline="") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    # Write the column headers
    writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()
