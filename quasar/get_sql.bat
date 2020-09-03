SET server=DB-HIB
SET user=sa
SET password=VismaVudAdmin123@
SET outputpath=D:\Scripts\GitHub\Salgstall\output\
SET inputpath=D:\Scripts\GitHub\Salgstall\input\



rem @ECHO %%~nxI

FOR %%I IN (%inputpath%*) DO (
sqlcmd -S %server% -U %user% -P %password% -i "%inputpath%%%~nxI" -y0 -o "%outputpath%%%~nxI.json"
)

py json_html.py

Powershell.exe -executionpolicy remotesigned -File  D:\Scripts\GitHub\Salgstall\utf.ps1

copy /y "D:\Scripts\GitHub\Salgstall\publish\Beste 10 Selgere.sql.json.htm" D:\Scripts\GitHub\Salgstall\publish\lor_best_publish.htm

copy D:\Scripts\GitHub\Salgstall\publish\*.* D:\Scripts\Salgstall\publish
