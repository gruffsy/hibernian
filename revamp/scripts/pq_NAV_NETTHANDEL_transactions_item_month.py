import pyodbc
import csv

# Replace with your actual SQL Server details
server = "10.0.10.41"
database = "MegaflisNAVLS2016"
username = "intranett"
password = "Megareader18"
# table = "<table>"


# Connect to the SQL Server
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};Database={database};UID={username};PWD={password}"
conn = pyodbc.connect(connection_string)

# Run the SELECT clause
query = """




SELECT
  MAX([Month]) AS [Måned],
  MAX([Year]) AS [År],
  ItemNo as Nr,
  SUM(SalesQty) AS [Antall],
  SUM(AmountExclVAT) AS [Oms. u/mva],
  SUM(GrossMargin) AS [Db. kr]
FROM (   
   
   
    select
    datepart(month,SIH.[Order Date]) as Month,
    datepart(year,SIH.[Order Date]) as Year,
    SIL.No_ AS ItemNo,
    SIL.Quantity as SalesQty,
    [Amount] as AmountExclVAT,
    [Amount] - (SIL.[Unit Cost]*SIL.[Quantity]) as GrossMargin
    from [MegaFlis Netthandel AS$Sales Invoice Line] SIL 
    inner join [MegaFlis Netthandel AS$Sales Invoice Header] SIH 
    on SIL.[Document No_]=SIH.No_
    where SIL.Type=2
    AND
    datepart(year,SIH.[Order Date]) > 2018
    UNION ALL
    select
    datepart(month,SCRMH.[Posting Date]) as Month,
    datepart(year,SCRMH.[Posting Date]) as Year,
    SCRML.No_ AS ItemNo,
    SCRML.Quantity*-1 as SalesQty, 
    -[Amount] as AmountExclVAT,
    -[Amount] - (SCRML.[Unit Cost]*SCRML.[Quantity]) as GrossMargin
    from [MegaFlis Netthandel AS$Sales Cr_Memo Line] SCRML 
    inner join [MegaFlis Netthandel AS$Sales Cr_Memo Header] SCRMH 
    on
    SCRML.[Document No_]=SCRMH.No_
    where SCRML.Type=2
    AND
    datepart(year,SCRMH.[Posting Date]) > 2018


  ) SalesDocument
GROUP BY [ItemNo],[Month], [Year] 

"""

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("../csv/pq_NAV_NETTHANDELEN_transactions_items_month.csv", "w", newline="") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    # Write the column headers
    writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()




