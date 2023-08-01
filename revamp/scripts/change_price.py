import pyodbc

# Sett opp tilkoblingsdetaljer for Tabell NAV
server_nav = "10.0.10.41"
username_nav = "intranett"
password_nav = "Megareader18"

# Opprett tilkobling til NAV-databasen
connection_string_nav = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_nav};UID={username_nav};PWD={password_nav}"
conn_nav = pyodbc.connect(connection_string_nav)

# Sett opp tilkoblingsdetaljer for Tabell Visma
server_visma = "DB-HIB"
username_visma = "sa"
password_visma = "VismaVudAdmin123@"

# Opprett tilkobling til Visma-databasen
connection_string_visma = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_visma};UID={username_visma};PWD={password_visma}"
conn_visma = pyodbc.connect(connection_string_visma)

cursor_nav = conn_nav.cursor()
cursor_visma = conn_visma.cursor()

# Definer SQL-spørringen for å hente data fra Tabell NAV
query_nav = '''
SELECT TOP 1100
    No_ AS Nr,
    [Unit Cost] AS Kostpris,
    [Unit Price Including VAT] AS Normalpris
FROM MegaFlisMASTER$Item
ORDER BY [Last Date Modified] DESC
'''

cursor_nav.execute(query_nav)
rows_nav = cursor_nav.fetchall()

# For hver rad i resultatet fra Tabell NAV
for row in rows_nav:
    Nr, Kostpris, Normalpris = row

    # Avrund verdiene til 6 desimaler
    Kostpris = round(Kostpris, 6)
    Normalpris = round(Normalpris, 6)
    
    # Hent den tilsvarende raden fra Tabell Visma basert på Nr/TrInf3
    cursor_visma.execute("SELECT TrInf3, Free3, Free4 FROM [F0001].[dbo].Prod WHERE TrInf3 = ?", Nr)
    row_visma = cursor_visma.fetchone()

    # Sjekk om det er forskjeller mellom de to radene
    if row_visma is not None and (row_visma[1] != Kostpris or row_visma[2] != Normalpris):
        # Hvis det er forskjeller, oppdater raden i Tabell Visma med de nye verdiene
        cursor_visma.execute("""
            UPDATE [F0001].[dbo].Prod 
            SET Free3 = ?, Free4 = ? 
            WHERE TrInf3 = ?
        """, Kostpris, Normalpris, Nr)
        conn_visma.commit()

        # Hent den oppdaterte raden fra Tabell Visma for å bekrefte endringene
        cursor_visma.execute("SELECT TrInf3, Free3, Free4 FROM [F0001].[dbo].Prod WHERE TrInf3 = ?", Nr)
        row_visma = cursor_visma.fetchone()

        # Skriv ut den opprinnelige raden fra Tabell NAV og den oppdaterte raden fra Tabell Visma
        print(Nr, Kostpris, Normalpris)
        print(row_visma)

