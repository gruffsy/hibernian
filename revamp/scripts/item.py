import pyodbc
import csv

# Replace with your actual SQL Server details
server = "10.0.10.41"
# database = "<database>"
username = "intranett"
password = "Megareader18"
# table = "<table>"


# Connect to the SQL Server
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};UID={username};PWD={password}"
conn = pyodbc.connect(connection_string)

# Run the SELECT clause
query = """
with 
    items as (
        select 
            No_,
            [Description 3],
            [Sales Unit of Measure], 
            [Vendor Item No_], 
            GTIN, 
            [Item Family Code], 
            [Purchaser Code], 
            [Product Group Code], 
            [Item Category Code], 
            [Vendor No_], 
            [Dangerous chemicals], 
            [Attrib 2 Code], 
            [Date Created]
        from 
            [MegaFlisMASTER$Item]
            --where [No_] = '019441' --debugging
        -- where [Exclude from Replenishment] = 0
    ),
    categories as (
        select 
            ic.Code as [Varekategorikode], 
            ic.Description as [Varekategori], 
            pg.Code as [Produktgruppekode], 
            pg.Description as [Produktgruppe]
        from 
            [MegaFlisMASTER$Product Group] pg 
            inner join [MegaFlisMASTER$Item Category] ic on pg.[Item Category Code] = ic.Code),
            staff as (select Code, Name
            from [MegaFlisMASTER$Salesperson_Purchaser]),
            brands as (select Code, Description
            from [MegaFlisMASTER$Item Family]
    ),
    vendors as (
        select 
            No_, 
            Name

        from 
            [MegaFlisMASTER$Vendor]
    )
    select 
        items.No_, 
        items.[Vendor Item No_],
        items.GTIN, 
        items.[Description 3], 
        items.[Sales Unit of Measure], 
        items.[Attrib 2 Code], 
        items.[Dangerous chemicals], 
        items.[Date Created],
        vendors.Name as [Leverandør],
        staff.Name as [Innkjøper],
        categories.Varekategori, 
        categories.Produktgruppe,
        brands.Description as [Brand]
    from 
        items
            inner join 
                categories on categories.Produktgruppekode = items.[Product Group Code] 
                and categories.Varekategorikode = items.[Item Category Code]
            left outer join 
                staff on items.[Purchaser Code] = staff.[Code]
            left outer join 
            brands on brands.Code = items.[Item Family Code]
            left outer join vendors on vendors.No_ = items.[Vendor No_]

"""

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("../csv/item.csv", "w", newline="") as output_file:
    writer = csv.writer(output_file, delimiter=";")
    # Write the column headers
    writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()
