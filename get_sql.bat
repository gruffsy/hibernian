SET server=DB-HIB
SET user=sa
SET password=VismaVudAdmin123@
SET outputpath=D:\Scripts\Salgstall\publish\json\
SET inputpath=D:\Scripts\Salgstall\publish\input\



rem @ECHO %%~nxI

FOR %%I IN (%inputpath%*) DO (
sqlcmd -S %server% -U %user% -P %password% -i "%inputpath%%%~nxI" -y0 -o "%outputpath%%%~nxI.json" -f i:65001 -f o:65001
)
FOR %%I IN (%inputpath%*) DO (
sqlcmd -S %server% -U %user% -P %password% -i %inputpath%%%~nxI -h-1 -s ; -w 500 -o %outputpath%%%~nxI
)
call git_push.bat