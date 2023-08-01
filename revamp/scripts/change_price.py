import pyodbc

# Replace with your actual SQL Server details
server = "10.0.10.41"
# database = "<database>"
username = "intranett"
password = "Megareader18"
# table = "<table>"

# Opprett tilkoblinger til databasene
connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};UID={username};PWD={password}"
conn_nav = pyodbc.connect(connection_string)



# conn_visma = pyodbc.connect('DRIVER={ODBC Driver for your DB};SERVER=server_visma;DATABASE=db_visma;UID=user;PWD=passwd')

cursor_nav = conn_nav.cursor()
# cursor_visma = conn_visma.cursor()

# Hent data fra Tabell NAV
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
      	[Hibernian Retail$Trans_ Sales Entry] se
inner join [Hibernian Retail$Transaction Header] th 
on 
	th.[Store No_]=se.[Store No_] and 
   	th.[POS Terminal No_]=se.[POS Terminal No_] and 
   	th.[Transaction No_]=se.[Transaction No_] 
INNER JOIN [Hibernian Retail$Store] s 
on
	s.No_=th.[Store No_]

LEFT JOIN [Hibernian Retail$Customer] c
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



cursor_nav.execute("SELECT Item_no, cost_price, sale_price FROM Items")
rows_nav = cursor_nav.fetchall()
print(rows_nav)


# for row in rows_nav:
#     Item_no, cost_price, sale_price = row

#     # Hent den aktuelle raden fra Tabell Visma
#     cursor_visma.execute("SELECT Free3, Free4 FROM Prod WHERE TrInf3 = ?", Item_no)
#     row_visma = cursor_visma.fetchone()

#     # Sjekk om det er forskjeller, og oppdater raden hvis det er det
#     if row_visma is None or row_visma[0] != cost_price or row_visma[1] != sale_price:
#         cursor_visma.execute("""
#             UPDATE Prod 
#             SET Free3 = ?, Free4 = ? 
#             WHERE TrInf3 = ?
#         """, cost_price, sale_price, Item_no)
#         conn_visma.commit()
