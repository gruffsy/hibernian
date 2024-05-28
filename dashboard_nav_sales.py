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
        WHEN 
        	th.[Store No_] = 'S110' 
        THEN 
        	'Arendal'
        WHEN 
        	th.[Store No_] = 'S170' 
        THEN 
        	'Larvik'
        WHEN 
        	th.[Store No_] = 'S140' 
        THEN 
        	'Skien'
        WHEN 
        	th.[Store No_] = 'S130' 
        THEN 
        	'Sandefjord'
        WHEN 
        	th.[Store No_] = 'S160' 
        THEN 
        	'Tønsberg'
             
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
			th.[Store No_] = 'S140' 
        THEN 
        	'0'     
        WHEN 
			th.[Store No_] = 'S160' 
        THEN 
        	'3'    
    END as 'Klient'
     ,sum(th.[Gross Amount])*-1  as mmoms
 ,sum(th.[Net Amount])*-1 as umoms
 ,sum(th.[Net Amount])*-1-sum(th.[Cost Amount])*-1 as db

 ,count(distinct th.[Receipt No_]) as antord
    ,sum(th.[Customer Account]/1.25) as kreditt

      	FROM [Megaflis_AS].[dbo].[mf_transaction_header__hib] th





    left join [Hibernian Retail$Customer$437dbf0e-84ff-417a-965d-ed2bb9650972] c
    on c.No_ = th.[customer no_]
where 
th.[Transaction Type] IN (0,2)


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
  th.[Customer Account],
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

