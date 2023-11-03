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
	CONVERT(INT, CONVERT(VARCHAR, th.[Date], 112)) as 'fakturadato',
	 CASE 
    	WHEN 
        	th.[Store No_] = 'S150' 
        THEN 
        	'Kristiansand' 
        WHEN 
        	th.[Store No_] = 'S100' 
        THEN 
        	'Bamble' 
        WHEN 
        	th.[Store No_] = 'S110' 
        THEN 
        	'Arendal'
        WHEN 
        	th.[Store No_] = 'S170' 
        THEN 
        	'Larvik'
             
	END as 'butikk',
    CASE 
    	WHEN 
        	th.[Store No_] = 'S150'
        THEN 
        	'2' 
        WHEN 
			th.[Store No_] = 'S100' 
        THEN 
        	'7' 
        WHEN 
			th.[Store No_] = 'S100' 
        THEN 
        	'4'
        WHEN 
			th.[Store No_] = 'S170' 
        THEN 
        	'6'    
    END as 'Klient',
    cast(sum([Total Rounded Amt_])*-1 as int) as 'mmoms',
    cast(sum(se.[Net Amount])*-1 as int) as 'umoms',
    cast(sum(se.[Net Amount])*-1-sum(se.[Cost Amount])*-1 as int) as 'db',
    CASE 
        WHEN sum(se.[Net Amount]) = 0 THEN 0 
        ELSE CAST(ROUND(sum(se.[Net Amount] - se.[Cost Amount]) / sum(se.[Net Amount]), 2) AS FLOAT) 
    END as 'dg',
	count(distinct th.[Receipt No_]) as 'antord',
    CASE 
        WHEN count(distinct th.[Receipt No_]) = 0 THEN 0 
        ELSE cast(sum(-[Total Rounded Amt_])/count(distinct th.[Receipt No_]) as int)
    END as 'prord'
from
      	[Hibernian Retail$LSC Trans_ Sales Entry$5ecfc871-5d82-43f1-9c54-59685e82318d] se
inner join [Hibernian Retail$LSC Transaction Header$5ecfc871-5d82-43f1-9c54-59685e82318d] th 
on 
	th.[Store No_]=se.[Store No_] and 
   	th.[POS Terminal No_]=se.[POS Terminal No_] and 
   	th.[Transaction No_]=se.[Transaction No_] 
-- INNER JOIN [Hibernian Retail$Store] s 
-- on
-- 	s.No_=th.[Store No_]

LEFT JOIN [Hibernian Retail$Customer$437dbf0e-84ff-417a-965d-ed2bb9650972] c
on 
       th.[Customer No_] = c.No_ 
where 	th.[Transaction Type]=2 
	and th.[Entry Status] in (0,2)

and 
	CONVERT(INT, CONVERT(VARCHAR, th.[Date], 112)) BETWEEN 20220101 AND convert(varchar, getdate(), 112)
	and nullif(th.[Receipt No_],'') is not null

and (
        c.[Customer Price Group] is null 
        or 
        c.[Customer Price Group] <> 'INTERNT'
        )

group by
	th.[Date], 
    th.[Store No_]
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
with open("../jsons/nav_salg_fra_22.json", "w") as output_file:
    json.dump(result, output_file, default=str, indent=4)

# Close the connection
cursor.close()
conn.close()
