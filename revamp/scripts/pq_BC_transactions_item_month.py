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
  MAX([Month]) AS [Måned],
  MAX([Year]) AS [År],
  itemNo as Nr,
  SUM(SalesQty) AS [Antall],
  SUM(AmountExclVAT) AS [Oms. u/mva],
  SUM(GrossMargin) AS [Db. kr]
FROM (


SELECT 
	  DATEPART(month,[TransHeader].[Date]) AS [Month],
	  DATEPART(Year,[TransHeader].[Date]) AS [Year],
      [Item No_] as ItemNo,
      -Quantity As SalesQty,
	  -[SalesEntry].[Net Amount] AS AmountExclVAT,
	  -[SalesEntry].[Net Amount] + SalesEntry.[Cost Amount] AS GrossMargin
	FROM 
    mf_trans_sales_entry__hib SalesEntry
    inner join    
    [mf_transaction_header__hib] TransHeader ON
    TransHeader.[Store No_] = SalesEntry.[Store No_]
    And TransHeader.[POS Terminal No_]=SalesEntry.[POS Terminal No_]
    and TransHeader.[Transaction No_] = SalesEntry.[Transaction No_] 
	 WHERE [Entry Status] IN (0,2) AND [No_ of Items] <> 0 and [TransHeader].[Date] >= dateadd(year,datediff(year,0,getdate())-4,0) -- First Day two years ago.
 
 Union All
 
SELECT 
 	  DATEPART(month,[TransHeader].[Date]) AS [Month],
	  DATEPART(Year,[TransHeader].[Date]) AS [Year],
      [Item No_] as ItemNo,
      -Quantity As SalesQty,
	 -[SalesEntry].[Net Amount] AS AmountExclVAT,
	  -[SalesEntry].[Net Amount] + SalesEntry.[Cost Amount] AS GrossMargin
	FROM 
    mf_trans_sales_entry__mfas SalesEntry
    inner join    
    [mf_transaction_header__mfas] TransHeader ON
    TransHeader.[Store No_] = SalesEntry.[Store No_]
    And TransHeader.[POS Terminal No_]=SalesEntry.[POS Terminal No_]
    and TransHeader.[Transaction No_] = SalesEntry.[Transaction No_] 

	WHERE [Entry Status] IN (0,2) AND [No_ of Items] <> 0 and [TransHeader].[Date] >= dateadd(year,datediff(year,0,getdate())-4,0) -- First Day two years ago.
 
 
 
 
  ) SalesDocument
GROUP BY [itemNo],[Month], [Year] 

"""

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("../csv/pq_bc_transactions_items_month.csv", "w", newline="") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    # Write the column headers
    writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()
