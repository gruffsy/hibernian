SET server=DB-HIB
SET user=sa
SET password=VismaVudAdmin123@
SET outputpath=C:\Scripts\Salgstall\hibernian\json\
SET inputpath=C:\Scripts\Salgstall\hibernian\input\
SET csvoutputpath=C:\Scripts\Salgstall\hibernian\lagersaldo\
SET csvinputpath=DC:\Scripts\Salgstall\hibernian\inputlagersaldo\

rem @ECHO %%~nxI

FOR %%I IN (%inputpath%*) DO (
sqlcmd -S %server% -U %user% -P %password% -i "%inputpath%%%~nxI" -y0 -o "%outputpath%%%~nxI.json" -f i:65001 -f o:65001
)

rem call sqlcmd -S %server% -U %user% -P %password% -s ";" -W -i %csvinputpath%lagersaldo.sql | findstr /v /c:"-" /b > %csvoutputpath%lagersaldo.csv

rem call git_push.bat


SET server=10.0.10.41
SET user=intranett
SET password=Megareader18
SET vpnpath="c:\program files\SonicWall\Global VPN Client\"
SET sqlpath=S:\Unified_SQL\
%vpnpath%swgvc /E "Billingstad" /U "per" /P "MegaPass###"
timeout /t 10

call sqlcmd -S %server% -U %user% -P %password% -i salg.sql -y0 -s ";" -o salg.json -f i:65001 -f o:65001

Powershell.exe -executionpolicy remotesigned -File .\merge.ps1


%vpnpath%swgvc /D "Billingstad"

call git_push.bat