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
    [Item No_] as ItemNo,
    se.[Store No_] as Store,
    datepart(year,th.[Date]) as Year,
    datepart(month,th.[Date]) as Month,
    SUM(Quantity)*-1 as SalesQty,
    sum(se.[Cost Amount])*-1 as CostAmount,
    sum([Total Rounded Amt_])*-1 as SalesAmountInclVat,
    sum(se.[Net Amount])*-1 as SalesAmountExclVat,
    sum(se.[Net Amount])*-1-sum(se.[Cost Amount])*-1 as BF
from
    [Hibernian Retail$LSC Trans_ Sales Entry$5ecfc871-5d82-43f1-9c54-59685e82318d] se
    inner join
    [Hibernian Retail$LSC Transaction Header$5ecfc871-5d82-43f1-9c54-59685e82318d] th on
        th.[Store No_]=se.[Store No_]
        and th.[POS Terminal No_]=se.[POS Terminal No_]
        and th.[Transaction No_]=se.[Transaction No_]
    LEFT JOIN
    [Hibernian Retail$Customer$437dbf0e-84ff-417a-965d-ed2bb9650972] c on 
        th.[Customer No_] = c.No_
where 
    th.[Transaction Type] = 2
    and th.[Entry Status] in (0,2)
    and CONVERT(INT, CONVERT(VARCHAR, th.[Date], 112)) BETWEEN 20220101 AND convert(varchar, getdate(), 112)
    and nullif(th.[Receipt No_],'') is not null

    and (
        c.[Customer Price Group] is null
    or
    c.[Customer Price Group] <> 'INTERNT'
        )
group by
    [Item No_],
    se.[Store No_],
    datepart(year,th.[Date]),
    datepart(month,th.[Date]) 

"""

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("../csv/pq_nav_transaksjoner.csv", "w", newline="") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    # Write the column headers
    writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()
