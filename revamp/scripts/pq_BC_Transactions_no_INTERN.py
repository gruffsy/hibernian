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
    [Store No_]
    ,datepart(year,[Date]) as Year
    ,datepart(month,[Date]) as Month
    ,sum(-[Net Amount]) AS 'u/moms'
    ,sum(-([Net Amount]-[Cost Amount])) AS 'DB'
FROM [Megaflis_AS].[dbo].[mf_transaction_header__hib] t
    left join [Hibernian Retail$Customer$437dbf0e-84ff-417a-965d-ed2bb9650972] c
    on t.[Customer No_] = c.No_
where t.[Transaction Type] = 2
    and t.[Entry Status] in (0,2)
    and nullif(t.[Receipt No_],'') is not NULL
    and (
        c.[Customer Price Group] is null
    or
    c.[Customer Price Group] <> 'INTERNT'
        )
Group BY
    [Store No_] 
    ,datepart(year,[Date])
    ,datepart(month,[Date])

"""

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("../csv/pq_BC_Transactions_no_INTERN.csv", "w", newline="") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    # Write the column headers
    writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()
