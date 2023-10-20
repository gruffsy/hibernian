import pyodbc
import json

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
        Staff.[Store No_] AS 'ButikkID',
        UPPER(Salesperson.[Job Title]) AS 'Stilling'
    FROM MegaflisNAVLS2016.dbo.[Hibernian Retail$Staff] Staff, 
        MegaflisNAVLS2016.dbo.[Hibernian Retail$Trans_ Sales Entry] SalesEntry, 
        [MegaflisNAVLS2016].[dbo].[Hibernian Retail$Salesperson_Purchaser] Salesperson
    WHERE 
        SalesEntry.[Created by Staff ID] = Staff.[Sales Person] AND 
        Salesperson.Code = Staff.[Sales Person]
    GROUP BY SalesEntry.Date, 
        SalesEntry.[Created by Staff ID], 
        Staff.[First Name], 
        Staff.[Last Name], 
        Staff.[Store No_],
        UPPER(Salesperson.[Job Title])
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
        	th.[Store No_] = 'S110' 
        THEN 
        	'Arendal' 
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
