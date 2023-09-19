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
    i.No_,
    i.[Vendor Item No_],
    i.GTIN,
    Item2.[Description 3],
    i.[Sales Unit of Measure],
    LSCItem.[LSC Attrib 2 Code] AS 'Attrib 2 Code',
    Item2.[Dangerous chemicals],
    i2.[LSC Date Created] AS [Date Created],
    Vendor.Name as [Leverandør],
    staff.Name as [Innkjøper],
    ItemCategory.Description AS Varekategori,
    ProductGroup.Description AS Produktgruppe,
    brand.[Description] as [Brand]

-- LSCItem.[LSC Item Family Code] AS 'Item Family Code',
-- Item2.[Purchaser Code],
-- ProductGroup.Code AS 'Product Group Code',
-- ItemCategory.Code AS 'Item Category Code',
-- Vendor.No_,
-- i.[Unit Cost] AS Kostpris,
-- LSCItem.[LSC Unit Price Incl_ VAT] AS Normalpris,
-- i.[Order Multiple] AS [Kolli str],
-- ProductGroup.Description AS Varegruppe,
-- ItemCategory.Description AS Hovedgruppe,
-- Item2.[Web Item] AS WebItem,
-- i.[$systemCreatedAt] AS [Opprettet dato],
-- i.[$systemModifiedAt] AS [Endret dato]
FROM
    [MASTER$Item$437dbf0e-84ff-417a-965d-ed2bb9650972] AS i
    inner join [MASTER$Item$5ecfc871-5d82-43f1-9c54-59685e82318d] i2 on i.No_ = i2.No_
    inner JOIN
    [MASTER$Item Category$437dbf0e-84ff-417a-965d-ed2bb9650972] AS ItemCategory ON ItemCategory.Code = i.[Item Category Code]
    inner JOIN
    [MASTER$LSC Retail Product Group$5ecfc871-5d82-43f1-9c54-59685e82318d] AS ProductGroup ON ProductGroup.Code = i2.[LSC Retail Product Code]
        AND ItemCategory.Code = ProductGroup.[Item Category Code]
    INNER JOIN
    [MASTER$Vendor$437dbf0e-84ff-417a-965d-ed2bb9650972] AS Vendor ON Vendor.No_ = i.[Vendor No_]
    INNER JOIN
    [MASTER$Item$64848631-618b-42d9-91c4-5fffcbea6f69] AS Item2 on Item2.No_ = i.No_
    INNER JOIN
    [MASTER$Item$5ecfc871-5d82-43f1-9c54-59685e82318d] AS LSCItem ON LSCItem.No_ = i.No_
    INNER JOIN
    [Megaflis AS$Salesperson_Purchaser$437dbf0e-84ff-417a-965d-ed2bb9650972] staff ON staff.Code=Item2.[Purchaser Code]
    LEFT JOIN
    [MASTER$LSC Item Family$5ecfc871-5d82-43f1-9c54-59685e82318d] brand ON LSCItem.[LSC Item Family Code] = [brand].Code

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
