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
query = '''
select
	datename(WEEKDAY, th.[Date]) as butikk, 
	7 as Klient,
    FORMAT(sum([Total Rounded Amt_])*-1, '### ### ##0 kr') as mmoms,
    FORMAT(sum(se.[Net Amount])*-1, '### ### ##0 kr') as umoms,
    FORMAT(sum(se.[Net Amount])*-1-sum(se.[Cost Amount])*-1, '### ### ##0 kr') as db,
	FORMAT(sum(se.[Net Amount]-se.[Cost Amount])/sum(se.[Net Amount]), 'P1') as dg,
	count(distinct th.[Receipt No_]) as antord,
    FORMAT(sum(-[Total Rounded Amt_])/count(distinct th.[Receipt No_]), '### ### ##0 kr') as prord
from
      	[Hibernian Retail$LSC Trans_ Sales Entry$5ecfc871-5d82-43f1-9c54-59685e82318d] se
inner join [Hibernian Retail$LSC Transaction Header$5ecfc871-5d82-43f1-9c54-59685e82318d] th 
on  
	th.[Store No_]=se.[Store No_] and 
   	th.[POS Terminal No_]=se.[POS Terminal No_] and 
   	th.[Transaction No_]=se.[Transaction No_] 
-- INNER JOIN [Hibernian Retail$Store] s 
-- on
	-- s.No_=th.[Store No_]

LEFT JOIN [Hibernian Retail$Customer$437dbf0e-84ff-417a-965d-ed2bb9650972] c
on 
       th.[Customer No_] = c.No_ 
where 	th.[Transaction Type]=2 
	and th.[Entry Status] in (0,2)
	and th.[Date] >= convert(varchar, getdate()-6, 112)
	and nullif(th.[Receipt No_],'') is not null

and (
        c.[Customer Price Group] is null 
        or 
        c.[Customer Price Group] <> 'INTERNT'
        )
	--and [Customer Account] = 0
group by
	th.[Date]
order by
	th.[Date]

'''


cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Convert rows to a list of dictionaries
result = [dict(zip(column_names, row)) for row in rows]

# Save the result as JSON
with open("salg.json", "w") as output_file:
    json.dump(result, output_file, default=str, indent=4)

# Close the connection
cursor.close()
conn.close()
