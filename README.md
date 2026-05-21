# Hibernian Beta

Dette er en slank arbeidskopi av Hibernian-appen for trygg videreutvikling.

## Innhold

- `index.htm` og `quasarapp.js` driver UI-et
- `revamp/publish/*.json` er hoveddatasettet som dagens faner leser
- `json/lager_stock.sql.json` brukes av stock-visningen

## Lokal preview

Kjor fra denne mappen:

```powershell
.\start-preview.ps1
```

Da starter en enkel statisk server pa `http://127.0.0.1:4173`.

Hvis du vil bruke en annen port:

```powershell
.\start-preview.ps1 -Port 8080
```

## Viktig

- Dette repoet er en beta-kopi, ikke live-kilden
- Endringer skal gjores her, ikke i `master` eller nettverkskilden
- Datafilene i denne kopien er bare et lokalt grunnlag for utvikling og testing
