# Pipeline Plan

## Oppdatert premiss per 21. mai 2026

## Oppdatert premiss per 26. mai 2026

Etter måling av de opprinnelige live-spørringene mot `Megaflis_AS` er det tydelig at neste steg må være en inkrementell pipeline:

- `nav_store_day`: ca. `9.1 s`
- `nav_seller_day`: ca. `22.6 s`
- `stock`: ca. `3.8 s`

I tillegg står databasen med:

- `READ_COMMITTED_SNAPSHOT = false`
- `SNAPSHOT ISOLATION = ON`

Det betyr at fullhistorikkspørringene ikke bare er trege; de øker også risikoen for blocking fordi vanlige `SELECT`-spørringer fortsatt kan ta delte låser under `READ COMMITTED`.

Ny anbefaling er derfor:

- frys historikk eldre enn trailing-vinduet
- les bare siste `7` dager på nytt ved hver kjøring
- bygg publiserte filer av:
  - fast base
  - fersk trailing-hale

Se også [INCREMENTAL_PIPELINE_ARCHITECTURE.md](/C:/Users/una/Documents/New%20project/hibernian-beta-copy/docs/architecture/INCREMENTAL_PIPELINE_ARCHITECTURE.md).

Dette dokumentet erstatter den tidligere antakelsen om at `Visma` fortsatt er en aktiv datakilde.

Ny, viktig avklaring:

- `NAV` er aktiv kilde for løpende oppdateringer
- `Visma` er bare historisk datagrunnlag
- ny pipeline skal derfor ikke kjøre `Visma` som en del av vanlig oppdateringsjobb

Det betyr at vi kan skille tydelig mellom:

1. historisk seed-data
2. løpende oppdateringer
3. publiserte JSON-filer til beta/frontend

## Mål

Bygge en ny pipeline som:

- kjører lokalt på din server
- bruker `NAV` som eneste aktive salgskilde
- bruker eksisterende lagerkilder for `stock`
- publiserer et lite sett med JSON-filer
- kan erstatte dagens Git-baserte publisering senere

## Kildene vi har i dag

### Aktiv kilde

- `sql2json_nav_salg_fra_22_pr_dag.py`
- `sql2json_nav_salg_pr_selger_fra_22.py`
- `stock.py`
- `time.py`

### Historisk kilde

- `sql2json_visma_salg_fra_22_pr_dag.py`
- `sql2json_visma_salg_pr_selger_fra_22.py`

### Dagens merge-/byggeledd

- `json_combined_visma_nav_fra_22_pr_dag.py`
- `json_combined_visma_nav_selgere_fra_22.py`
- `merge_stock_orders.py`

## Ny datamodell

Ny pipeline bør sikte mot disse publiserte filene:

- `butikk_dag.json`
- `selger_dag.json`
- `stock.json`
- `meta.json`

Beskrivelse:

- `butikk_dag.json`: én samlet daglig butikkfeed som brukes av frontend til `dag`, `uke`, `måned` og `år`
- `selger_dag.json`: én samlet daglig selgerfeed som brukes av frontend til `selgere`
- `stock.json`: normalisert lagerfeed med beholdning og bestillinger
- `meta.json`: sist oppdatert

## Visma-strategi

### Anbefalt modell

`Visma` skal behandles som historisk bootstrap, ikke som live-kilde.

Det betyr:

1. Kjør en kontrollert engangsimport av `Visma`-data inn i nye historiske basisfiler.
2. Frys dette datagrunnlaget.
3. Kjør bare `NAV` i løpende drift.
4. Slå sammen historisk grunnlag og nye `NAV`-oppdateringer i publisert output.

### Praktisk konsekvens

Ny pipeline trenger ikke:

- løpende `Visma`-SQL-kall
- løpende `Visma`-feilhåndtering
- daglig merge mellom to aktive salgssystemer

## Anbefalt pipeline i faser

### Fase 1: Historisk seed

Formål:

- etablere historikk uten å avhenge av `Visma` videre

Steg:

1. Les eksisterende `Visma` butikkdata
2. Les eksisterende `Visma` selgerdata
3. Normaliser feltnavn og datatyper
4. Lagre som:
   - `historical_store_day.json`
   - `historical_seller_day.json`

Dette kan være:

- generert fra gamle skript én gang
- eller bygget direkte fra dagens publish-filer hvis de er komplette nok

### Fase 2: Aktiv NAV-ekstraksjon

Formål:

- hente bare nye og løpende data

Steg:

1. Kjør `NAV` butikkspørring
2. Kjør `NAV` selgerspørring
3. Normaliser output til samme skjema som historikkfilene

Outputs:

- `nav_store_day_raw.json`
- `nav_seller_day_raw.json`

### Fase 3: Sammenstilling

Formål:

- lage én stabil feed per domene

Steg for butikk:

1. Last historisk butikkfeed
2. Last ny `NAV` butikkfeed
3. Slå sammen og dedupliser på:
   - `fakturadato`
   - `butikk`
4. Regn inn `Totalt` per dag
5. Lag `butikk_dag.json`

Steg for selgere:

1. Last historisk selgerfeed
2. Last ny `NAV` selgerfeed
3. Slå sammen og dedupliser på:
   - `fakturadato`
   - `navn`
   - `butikk`
4. Sorter for frontend-bruk
5. Lag `selger_dag.json`

### Fase 4: Lager

Formål:

- bygge én samlet lagerfeed

Steg:

1. Hent rå lagerdata
2. Hent bestillingsdata
3. Slå dem sammen
4. Lag `stock.json`

Her er dagens `merge_stock_orders.py` tydelig relevant som utgangspunkt.

### Fase 5: Metadata

Formål:

- enkel frontend-status

Steg:

1. Kjør oppdatert-tid-spørring
2. Lag `meta.json`

## Konkrete nye steg i ny struktur

Disse modulene er et godt minimum:

### `extract`

- `extract_nav_store_day.py`
- `extract_nav_seller_day.py`
- `extract_stock.py`
- `extract_meta.py`

### `bootstrap`

- `bootstrap_visma_store_history.py`
- `bootstrap_visma_seller_history.py`

Disse kjøres bare ved behov, ikke i normal drift.

### `build`

- `build_store_day.py`
- `build_seller_day.py`
- `build_stock.py`

### `publish`

- `publish_local.py`
- senere eventuelt `publish_r2.py`

## Hvilke gamle skript som dekker hva

### Butikk dag

Gamle skript:

- `sql2json_nav_salg_fra_22_pr_dag.py`
- `sql2json_visma_salg_fra_22_pr_dag.py`
- `json_combined_visma_nav_fra_22_pr_dag.py`

Ny retning:

- behold logikken
- fjern løpende Visma-kjøring
- bruk Visma bare til seed

### Selger dag

Gamle skript:

- `sql2json_nav_salg_pr_selger_fra_22.py`
- `sql2json_visma_salg_pr_selger_fra_22.py`
- `json_combined_visma_nav_selgere_fra_22.py`

Ny retning:

- behold logikken
- fjern løpende Visma-kjøring
- bruk Visma bare til seed

### Stock

Gamle skript:

- `stock.py`
- `merge_stock_orders.py`

Ny retning:

- behold som modell
- normaliser til én sluttfil

### Meta

Gammelt skript:

- `time.py`

Ny retning:

- kan nesten beholdes som konsept, men med bedre konfigurasjon

## Hva vi kan forenkle med en gang

Disse tingene bør bort i ny pipeline:

- hardkodede SQL-credentials i Python-filer
- formattering til `kr` og visningstekst tidlig i pipeline
- løpende `Visma`-kall
- mange små mellomfiler som ikke er nødvendige for frontend

## Ny minimumskjøring i drift

Når historisk seed er på plass, bør normal kjøring være:

1. `extract_nav_store_day`
2. `extract_nav_seller_day`
3. `extract_stock`
4. `extract_meta`
5. `build_store_day`
6. `build_seller_day`
7. `build_stock`
8. `publish`

## Publiseringsmål for beta

På kort sikt kan publish fortsatt bety:

- oppdatere data i arbeidskopi/testmiljø

Senere skal publish bety:

- laste opp JSON-artifacts til privat lagring

## Anbefalt implementasjonsrekkefølge

1. Dokumenter og frys `Visma` som historisk kilde.
2. Lag ny `butikk_dag`-bygger.
3. Lag ny `selger_dag`-bygger.
4. Lag ny `stock`-bygger.
5. Lag ny `meta`-bygger.
6. Test at betaen kan lese bare disse filene.
7. Bytt ut gammel publiseringsrutine.

## Praktisk konklusjon

Det viktigste grepet er dette:

- `Visma` ut av driftspipeline
- `NAV` inn som eneste løpende salgskilde
- behold én samlet historikk
- publiser få, stabile JSON-filer

Det gjør løsningen:

- enklere å drifte
- enklere å forstå
- mindre sårbar
- lettere å sikre senere
