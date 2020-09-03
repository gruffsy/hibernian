SET server=DB-HIB
SET user=sa
SET password=VismaVudAdmin123@
SET outputpath=S:\Salgstall\publish\quasar\
SET inputpath=S:\Salgstall\publish\quasar\input\



rem @ECHO %%~nxI

FOR %%I IN (%inputpath%*) DO (
sqlcmd -S %server% -U %user% -P %password% -i "%inputpath%%%~nxI" -y0 -o "%outputpath%%%~nxI.json" -f i:65001 -f o:65001
)

pause