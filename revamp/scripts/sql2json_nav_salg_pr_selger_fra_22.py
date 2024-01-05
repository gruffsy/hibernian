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
SET DATEFIRST 1;

WITH Sales AS (
    SELECT 
        SalesEntry.[Date] AS 'Dato', 
        SalesEntry.[Created by Staff ID] AS 'Selger', 
        CASE DATEPART(WEEKDAY,SalesEntry.[Date]) 
            WHEN 1 THEN 'Mandag' 
            WHEN 2 THEN 'Tirsdag' 
            WHEN 3 THEN 'Onsdag' 
            WHEN 4 THEN 'Torsdag' 
            WHEN 5 THEN 'Fredag' 
            WHEN 6 THEN 'Lørdag' 
            WHEN 7 THEN 'Søndag' 
        END 'ukedag',
        -(Sum(SalesEntry.[Net Amount])) AS 'Beløp inkl. mva', 
        -(Sum(SalesEntry.[Net Amount])-Sum(SalesEntry.[Cost Amount])) AS 'Db.kr', 
        Staff.[First Name] AS 'Fornavn', 
        Staff.[Last Name] AS 'Etternavn', 
        Staff.[Store No_] AS 'ButikkID'
     --   ,UPPER(Salesperson.[Job Title]) AS 'Stilling'
    FROM [Hibernian Retail$LSC Staff$5ecfc871-5d82-43f1-9c54-59685e82318d] Staff, 
        [Megaflis_AS].[dbo].[mf_trans_sales_entry__hib] SalesEntry
        
    inner join [Hibernian Retail$LSC Transaction Header$5ecfc871-5d82-43f1-9c54-59685e82318d] th 
on 
	th.[Store No_]=SalesEntry.[Store No_] and 
   	th.[POS Terminal No_]=SalesEntry.[POS Terminal No_] and 
   	th.[Transaction No_]=SalesEntry.[Transaction No_] 


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
     and SalesEntry.[Created by Staff ID] = Staff.[Sales Person]

       
         --AND        Salesperson.Code = Staff.[Sales Person]

    GROUP BY SalesEntry.Date, 
        SalesEntry.[Created by Staff ID], 
        Staff.[First Name], 
        Staff.[Last Name], 
        Staff.[Store No_]
        --,UPPER(Salesperson.[Job Title])
    HAVING (SalesEntry.[Created by Staff ID]<>'')
)

SELECT 
    ukedag,
	[Fornavn] + ' ' +[Etternavn] AS [navn],
    cast([Beløp inkl. mva] as int) as [umoms],
    cast([Db.kr] as int) as [db],
    CASE 
    	WHEN 
        	ButikkID = 'S150' 
        THEN 
        	'Kristiansand' 
        WHEN 
        	ButikkID = 'S100' 
        THEN 
        	'Bamble' 
        WHEN 
        	ButikkID = 'S110' 
        THEN 
        	'Arendal'
            WHEN 
        	ButikkID = 'S130' 
        THEN 
        	'Sandefjord'
        WHEN 
        	ButikkID = 'S170' 
        THEN 
        	'Larvik' 
	END as 'butikk',
    CONVERT(INT, CONVERT(VARCHAR, Dato, 112)) as 'fakturadato'
    
    
FROM Sales


'''


cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Convert rows to a list of dictionaries
result = [dict(zip(column_names, row)) for row in rows]

# Save the result as JSON
with open("../jsons/nav_salg_pr_selger_fra_22.json", "w") as output_file:
    json.dump(result, output_file, default=str, indent=4)

# Close the connection
cursor.close()
conn.close()
