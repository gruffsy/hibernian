# import pyodbc
# import json

# # Replace with your actual SQL Server details
# server = "mf-ls-sql02.norwayeast.cloudapp.azure.com"
# database = "Megaflis_AS"
# username = "perarne"
# password = "AdaiQQvlq!#to43"
# # table = "<table>"


# # Connect to the SQL Server
# connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};Database={database};UID={username};PWD={password}"
# conn = pyodbc.connect(connection_string)

# # Run the SELECT clause
# query = """

# set
#     nocount on
# set
#     noexec on

# set
#     noexec off

# --  SELECT FORMAT (getdate(), 'HH:mm - dddd dd. MMMM yyyy', 'no-NO') as "oppdatert";

# SELECT FORMAT(
#   DATEADD(
#     MINUTE,
#     DATEDIFF(MINUTE, 0, GETDATE()) / 5 * 5,
#     0
#   ),
#   'HH:mm - dddd dd. MMMM yyyy',
#   'no-NO'
# ) AS "oppdatert";

# """

# cursor = conn.cursor()
# cursor.execute(query)

# # Fetch all rows and column names
# rows = cursor.fetchall()
# column_names = [column[0] for column in cursor.description]
# print(rows)
# column_names = [column[0] for column in cursor.description]

# # Convert rows to a list of dictionaries
# result = [dict(zip(column_names, row)) for row in rows]

# # Save the result as JSON
# with open("../publish/tid.json", "w") as output_file:
#     json.dump(result, output_file, default=str, indent=4)

# # Close the connection
# cursor.close()
# conn.close()


from datetime import datetime, timedelta
from babel.dates import format_datetime
import json

# Hent nåværende tid
naa = datetime.now()

# Rund ned til nærmeste 5 minutter
minutter = naa.minute - naa.minute % 5
avrundet_tid = naa.replace(minute=minutter, second=0, microsecond=0)

# Formater avrundet tid
oppdatert_format = format_datetime(avrundet_tid, "HH:mm - EEEE dd. MMMM yyyy", locale='nb_NO')

# Forbered data for JSON
data = {"oppdatert": oppdatert_format}
print(data)

# Konverter data til JSON-streng
json_data = json.dumps(data, ensure_ascii=False, indent=4)

# Skriv JSON til fil
with open('../publish/tid.json', 'w', encoding='utf-8') as f:
    f.write(json_data)

print("JSON data skrevet til filen 'oppdatert_tid.json'")
