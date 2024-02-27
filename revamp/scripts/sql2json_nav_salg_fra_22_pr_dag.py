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
SELECT 
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
        WHEN 
        	th.[Store No_] = 'S130' 
        THEN 
        	'Sandefjord'
         WHEN 
        	th.[Store No_] = 'S140' 
        THEN 
        	'Skien'
        WHEN 
        	th.[Store No_] = 'S160' 
        THEN 
        	'Tønsberg'
             
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
			th.[Store No_] = 'S110' 
        THEN 
        	'4'
        WHEN 
			th.[Store No_] = 'S170' 
        THEN 
        	'6'    
        WHEN 
			th.[Store No_] = 'S130' 
        THEN 
        	'5'
        WHEN 
			th.[Store No_] = 'S160' 
        THEN 
        	'3'    
         WHEN 
			th.[Store No_] = 'S140' 
        THEN 
        	'0'      
    END as 'Klient'
--  , th.[Customer Name]
--  , th.[Customer No_]
--  , c.[Customer Price Group]
 ,cast(sum(th.[Gross Amount])*-1 as int) as 'mmoms'
 ,cast(sum(th.[Net Amount])*-1 as int) as 'umoms'
 ,cast(sum(th.[Net Amount])*-1-sum(th.[Cost Amount])*-1 as int) as 'db'
--  ,cast(sum(th.[Customer Account]) as int) as 'Fakturert'
 
FROM [Megaflis_AS].[dbo].[mf_transaction_header__hib] th
    left join [Hibernian Retail$Customer$437dbf0e-84ff-417a-965d-ed2bb9650972] c
    on c.No_ = th.[customer no_]
where 
th.[Transaction Type] = 2
and th.[Entry Status] in (0,2)
and th.[Receipt No_] is not NULL
and th.[Customer Account] = 0
group BY
th.[Date]
,th.[Store No_]
-- , th.[Customer Name]
--  , th.[Customer No_]
--  , c.[Customer Price Group]

 order by th.[Date]


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
