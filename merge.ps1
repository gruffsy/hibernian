$js1 = Get-Content -Path "C:\Scripts\Salgstall\hibernian\json\idag.sql.json" -Raw |
    ConvertFrom-Json
$js2 = Get-Content -Path .\salg.json -Raw |
    ConvertFrom-Json

$js1 + $js2 |
    ConvertTo-Json -Depth 5 |
    Out-File -FilePath "C:\Scripts\Salgstall\hibernian\json\works.json"