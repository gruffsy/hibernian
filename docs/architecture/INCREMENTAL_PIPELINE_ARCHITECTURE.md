# Incremental Pipeline Architecture

## Hvorfor vi endrer flyten

Målingene fra `26. mai 2026` viste at den originale live-hentingen er tung fordi den leser full historikk ved hver kjøring:

- `nav_store_day`: ca. `9.1 s`
- `nav_seller_day`: ca. `22.6 s`
- `stock`: ca. `3.8 s`

I tillegg kjører databasen med:

- `READ_COMMITTED_SNAPSHOT = false`
- `SNAPSHOT ISOLATION = ON`

Det betyr at vanlige `SELECT`-spørringer fortsatt kan ta delte låser under `READ COMMITTED`, og derfor blokkere eller bli blokkert av skrivere. Den riktige måten å redusere risiko på her er ikke først og fremst å tune Cloudflare eller Python, men å redusere hvor mye SQL vi leser hver gang.

## Ny hovedidé

Historikk eldre enn siste `7` dager behandles som fast.

Ved hver oppdatering gjør vi bare dette:

1. Les inn siste `7` dager på nytt fra SQL.
2. Overskriv den bevegelige halen i lokale snapshots.
3. Bygg publiserte JSON-filer av:
   - fast base
   - fersk 7-dagers hale
4. Publiser til lokal beta og `R2`.

Det betyr at vi går fra:

- `fullhistorikk + full aggregasjon ved hver kjøring`

til:

- `frossen base + kort trailing window`

## Ny datamodell i pipeline

### Uforanderlige eller sjelden endrede filer

- `historical_store_day.json`
- `historical_seller_day.json`

Disse brukes som bootstrap og referansegrunnlag.

### Nye state- og snapshot-filer

- `store_day_base_snapshot.json`
- `seller_day_base_snapshot.json`
- `refresh_state.json`

Formål:

- `store_day_base_snapshot.json`:
  - alle butikkrader eldre enn vinduet
- `seller_day_base_snapshot.json`:
  - alle selgerrader eldre enn vinduet
- `refresh_state.json`:
  - metadata om siste vellykkede kjøring
  - hvilken `window_start_date` som var brukt
  - antall rader som ble produsert

### Bevegelig hale

Eksisterende råfiler kan fortsatt brukes, men de skal nå representere bare trailing-vinduet:

- `nav_store_day_raw.json`
- `nav_seller_day_raw.json`

Disse skal ikke lenger være “hele NAV fra 2022”, men:

- `fra i dag minus 7 dager til nå`

## Ny SQL-strategi

### Butikk per dag

Ny strategi:

- behold dagens SQL-logikk
- legg inn eksplisitt datofilter for de siste `7` dagene

Konseptuelt:

```sql
WHERE th.[Date] >= DATEADD(DAY, -7, CAST(GETDATE() AS date))
```

eller gjerne litt mer kontrollert:

```sql
WHERE th.[Date] >= @window_start
```

### Selger per dag

Samme modell:

- behold logikken
- begrens lesingen til de siste `7` dagene

### Stock

`stock` trenger ikke samme historikkstrategi.

Der er målet bare:

- full frisk henting av gjeldende lagerstatus
- full frisk henting av bestillinger

Det er akseptabelt fordi stock allerede er relativt billig sammenlignet med salgsspørringene.

## Ny byggelogikk

### Store day

Ved hver kjøring:

1. beregn `window_start_date`
2. les `store_day_base_snapshot.json`
3. les `nav_store_day_raw.json` for bare trailing-vinduet
4. slå sammen:
   - behold base-rader med dato `< window_start_date`
   - erstatt alle rader `>= window_start_date` med ferske NAV-rader
5. regn `Totalt` på nytt for alle datoer i sluttsettet
6. skriv `store_day.json`

### Seller day

Samme mønster:

1. les `seller_day_base_snapshot.json`
2. les `nav_seller_day_raw.json`
3. behold bare base-rader eldre enn vinduet
4. legg til ferske trailing-rader
5. sorter og skriv `seller_day.json`

## Hvordan base snapshots oppdateres

Vi trenger ikke å regenerere hele basen hver gang.

Basen kan oppdateres slik:

1. på første kjøring:
   - seed base fra historiske filer
2. ved senere kjøringer:
   - behold base som den er
   - trailing-vinduet bygges alltid friskt
3. valgfritt én gang per natt:
   - “rull” gårsdagen ut av trailing-vinduet og inn i base-snapshot

Det betyr at vi kan ha to nivåer:

### Enkel modell

- base snapshots bygges én gang
- trailing-vinduet kombineres bare ved publisering

Fordel:

- enklest å implementere

Ulempe:

- basefilene blir ikke gradvis oppdatert uten en ekstra jobb

### Bedre modell

- egen `roll-window-forward`-jobb nattlig
- den flytter gamle trailing-dager inn i base snapshots

Fordel:

- ryddigere og mer eksplisitt datastruktur

Anbefaling:

- start med enkel modell
- legg til nattlig “roll forward” når resten er stabilt

## Ny kjøresekvens

Ny anbefalt kjørekommando bør se slik ut:

1. `ensure-base-snapshots`
2. `extract-nav-store-window`
3. `extract-nav-seller-window`
4. `extract-stock`
5. `extract-meta`
6. `build-store-day-incremental`
7. `build-seller-day-incremental`
8. `build-stock`
9. `publish-local`
10. `publish-r2`
11. `write-refresh-state`

## Konkrete nye moduler

### `extract`

- `extract_nav_store_window.py`
- `extract_nav_seller_window.py`

Disse skal bruke:

- parameterisert `window_start_date`

### `build`

- `build_store_day_incremental.py`
- `build_seller_day_incremental.py`

### `state`

Kan ligge under `shared/` eller som egne hjelpefunksjoner:

- `load_refresh_state`
- `save_refresh_state`
- `compute_window_start_date`

## Drift og scheduler

Anbefalt oppdateringsintervall etter denne redesignen:

- start med `10` eller `15` minutter
- vurder `5` minutter senere hvis SQL-belastningen er stabil

Når bare trailing-vinduet leses, bør både kjøretid og låserisiko falle kraftig sammenlignet med dagens fullhistorikkspørringer.

## Hva vi oppnår

Med denne modellen får vi:

- mye mindre SQL-lesing per kjøring
- mindre risiko for blocking
- enklere kontroll på “hva som faktisk kan endre seg”
- samme publiserte frontend-kontrakt
- mulighet for høyere oppdateringsfrekvens uten å plage databasen like mye

## Anbefalt implementeringsrekkefølge

1. parameteriser NAV-spørringene med `window_start_date`
2. bygg base snapshots fra dagens historikk
3. bytt `build_store_day` og `build_seller_day` til incremental merge
4. legg inn `refresh_state.json`
5. test lokalt mot beta
6. flytt scheduler over til den nye refresh-kommandoen
