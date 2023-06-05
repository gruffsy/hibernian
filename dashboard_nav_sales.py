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
query = '''
select
    CASE 
    	WHEN 
        	th.[Store No_] = 'S150' 
        THEN 
        	'Kristiansand' 
        WHEN 
        	th.[Store No_] = 'S100' 
        THEN 
        	'Bamble' 
	END as 'butikk',
	convert(varchar, th.[Date], 112) as Dato, 
	CASE 
    	WHEN 
        	th.[Store No_] = 'S150'
        THEN 
        	'2' 
        WHEN 
			th.[Store No_] = 'S100' 
        THEN 
        	'7' 
    END as 'Klient',
    sum([Total Rounded Amt_])*-1 as mmoms,
    sum(se.[Net Amount])*-1 as umoms,
    sum(se.[Net Amount])*-1-sum(se.[Cost Amount])*-1 as db,
	count(distinct th.[Receipt No_]) as antord,
    [Customer Account]/1.25 as kreditt
from
      	[Hibernian Retail$Trans_ Sales Entry] se 
inner join [Hibernian Retail$Transaction Header] th 
on 
	th.[Store No_]=se.[Store No_] and 
   	th.[POS Terminal No_]=se.[POS Terminal No_] and 
   	th.[Transaction No_]=se.[Transaction No_] 
INNER JOIN [Hibernian Retail$Store] s 
on
	s.No_=th.[Store No_]

LEFT JOIN [Hibernian Retail$Customer] c
on 
       th.[Customer No_] = c.No_ 
where 	th.[Transaction Type]=2 
	and th.[Entry Status] in (0,2)
	and nullif(th.[Receipt No_],'') is not null

and (
        c.[Customer Price Group] is null 
        or 
        c.[Customer Price Group] <> 'INTERNT'
        )
group by
	th.[Date],
    [Customer Account],
    th.[Store No_]
order by
	th.[Date]

'''

cursor = conn.cursor()
cursor.execute(query)

# Fetch all rows and column names
rows = cursor.fetchall()
column_names = [column[0] for column in cursor.description]

# Save the result as CSV
with open("salg2.csv", "w", newline='') as output_file:
    writer = csv.writer(output_file, delimiter=';')
    # Write the column headers
    # writer.writerow(column_names)
    # Write the rows
    for row in rows:
        writer.writerow(row)

# Close the connection
cursor.close()
conn.close()

