SET server=DB-HIB
SET user=sa
SET password=VismaVudAdmin123@
SET outputpath=D:\Scripts\Salgstall\publish\json\
SET inputpath=D:\Scripts\Salgstall\publish\input\
SET csvoutputpath=D:\Scripts\Salgstall\publish\lagersaldo\
SET csvinputpath=D:\Scripts\Salgstall\publish\inputlagersaldo\


rem @ECHO %%~nxI

FOR %%I IN (%inputpath%*) DO (
sqlcmd -S %server% -U %user% -P %password% -i "%inputpath%%%~nxI" -y0 -o "%outputpath%%%~nxI.json" -f i:65001 -f o:65001
)


call sqlcmd -S %server% -U %user% -P %password% -s ";" -W -i %csvinputpath%lagersaldo.sql | findstr /v /c:"-" /b > %csvoutputpath%lagersaldo.csv

call git_push.bat
