import pyodbc

# Replace with your actual SQL Server details
server_nav = "10.0.10.41"
# database = "<database>"
username_nav = "intranett"
password_nav = "Megareader18"
# table = "<table>"

# Opprett tilkoblinger til databasene
connection_string_nav = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_nav};UID={username_nav};PWD={password_nav}"
conn_nav = pyodbc.connect(connection_string_nav)


# Replace with your actual SQL Server details
server_visma = "DB-HIB"
# database = "<database>"
username_visma = "sa"
password_visma = "VismaVudAdmin123@"
# table = "<table>"

# Opprett tilkoblinger til databasene
connection_string_visma = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_visma};UID={username_visma};PWD={password_visma}"
conn_visma = pyodbc.connect(connection_string_visma)

cursor_nav = conn_nav.cursor()
cursor_visma = conn_visma.cursor()

# Hent data fra Tabell NAV
query_nav = '''
SELECT  top 100    	
		No_ AS Nr,
		[Unit Cost] AS Kostpris,
		[Unit Price Including VAT] AS Normalpris
		--[Date Created] AS [Opprettet dato],
		-- [Last Date Modified] AS [Endret dato]
                

    FROM            MegaFlisMASTER$Item
    where No_ = '006029'



'''



cursor_nav.execute(query_nav)
rows_nav = cursor_nav.fetchall()
print(rows_nav)


for row in rows_nav:
    Nr, Kostpris, Normalpris = row
    print(row)
    # Hent den aktuelle raden fra Tabell Visma
    cursor_visma.execute("SELECT TrInf3, Free3, Free4 FROM [F0001].[dbo].Prod WHERE TrInf3 = ?", Nr)
    row_visma = cursor_visma.fetchone()
    print(row_visma)

    # Sjekk om det er forskjeller, og oppdater raden hvis det er det
    if row_visma is None or row_visma[1] != Kostpris or row_visma[2] != Normalpris:
        cursor_visma.execute("""
            UPDATE [F0001].[dbo].ProdProd 
            SET Free3 = ?, Free4 = ? 
            WHERE TrInf3 = ?
        """, Kostpris, Normalpris, Nr)
        conn_visma.commit()
    cursor_visma.execute("SELECT TrInf3, Free3, Free4 FROM [F0001].[dbo].Prod WHERE TrInf3 = ?", Nr)
    row_visma = cursor_visma.fetchone()
    