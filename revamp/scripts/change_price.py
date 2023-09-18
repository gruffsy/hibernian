import pyodbc
import logging
from datetime import datetime

# Set up the logging
logging.basicConfig(
    filename="../logs/log_file.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
)

# Sett opp tilkoblingsdetaljer for Tabell BC
server_nav = "mf-ls-sql02.norwayeast.cloudapp.azure.com"
username_nav = "perarne"
password_nav = "AdaiQQvlq!#to43"

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
query_nav = """
  SELECT
  -- top 1000
    i.[No_] AS Nr,
    i.[Unit Cost] AS Kostpris,
    i2.[LSC Unit Price Incl_ VAT] AS Normalpris
FROM [Megaflis_AS].[dbo].[MASTER$Item$437dbf0e-84ff-417a-965d-ed2bb9650972] i
INNER JOIN [Megaflis_AS].[dbo].[MASTER$Item$5ecfc871-5d82-43f1-9c54-59685e82318d] i2 
ON  i.No_=i2.No_
ORDER BY i.[Last Date Modified] DESC
"""

cursor_nav.execute(query_nav)
rows_nav = cursor_nav.fetchall()

# For hver rad i resultatet fra Tabell NAV
for row in rows_nav:
    Nr, Kostpris, Normalpris = row

    # Avrund verdiene til 6 desimaler
    Kostpris = round(Kostpris, 6)
    Normalpris = round(Normalpris, 6)

    # Hent den tilsvarende raden fra Tabell Visma basert på Nr/TrInf3
    cursor_visma.execute(
        "SELECT TrInf3, Free3, Free4 FROM [F0001].[dbo].Prod WHERE TrInf3 = ?", Nr
    )
    row_visma = cursor_visma.fetchone()

    # Sjekk om det er forskjeller mellom de to radene
    if row_visma is not None and (
        row_visma[1] != Kostpris or row_visma[2] != Normalpris
    ):
        # Hvis det er forskjeller, oppdater raden i Tabell Visma med de nye verdiene
        cursor_visma.execute(
            """
            UPDATE [F0001].[dbo].Prod 
            SET Free3 = ?, Free4 = ? 
            WHERE TrInf3 = ?
        """,
            Kostpris,
            Normalpris,
            Nr,
        )
        conn_visma.commit()

        # Hent den oppdaterte raden fra Tabell Visma for å bekrefte endringene
        cursor_visma.execute(
            "SELECT TrInf3, Free3, Free4, ProdNo FROM [F0001].[dbo].Prod WHERE TrInf3 = ?",
            Nr,
        )
        row_visma_updated = cursor_visma.fetchone()

        # Skriv ut den opprinnelige raden fra Tabell NAV og den oppdaterte raden fra Tabell Visma
        print(row)
        print(row_visma_updated)
        logging.info(row)
        logging.info(row_visma_updated)

        # Hvis raden i Tabell Visma ble oppdatert, oppdater den tilsvarende raden i PrDcMat
        if row_visma != row_visma_updated:
            cursor_visma.execute(
                """
                UPDATE [F0001].[dbo].PrDcMat
                SET PurcPr = ?, CstPr = ?
                WHERE ProdNo = ?
            """,
                Kostpris,
                Kostpris,
                row_visma_updated[3],
            )  # Assuming ProdNo is at index 3
            conn_visma.commit()

            # Oppdater SalePr og SugPr for rader som oppfyller de spesifiserte betingelsene
            cursor_visma.execute(
                """
                UPDATE [F0001].[dbo].PrDcMat
                SET SalePr = ?, SugPr = ?
                WHERE ProdNo = ? AND CustPrGr <= 1 AND ToDt = 0
            """,
                Normalpris,
                Normalpris,
                row_visma_updated[3],
            )  # Assuming ProdNo is at index 3
            conn_visma.commit()

print("OKIDOKI")
logging.info("Ferdig")
