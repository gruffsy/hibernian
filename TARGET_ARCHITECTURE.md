# Hibernian Target Architecture

## Oppdatert Retning Per 18. Mai 2026

Dette dokumentet er oppdatert etter at vi har:

- bygget ny beta for `dag`, `uke`, `maaned`, `aar`, `selgere` og `stock`
- redusert betaen til i hovedsak dagsbaserte filer
- besluttet at `Render` skal beholdes for frontend
- vurdert sikkerhet for sensitive bedriftsdata og SSO via eksisterende Microsoft 365-kontoer
- avklart at `Visma` ikke lenger oppdateres og derfor bare er historisk datagrunnlag

De viktigste beslutningene na er:

1. `Render` beholdes som host for frontend.
2. Sensitive JSON-filer skal ikke ligge offentlig i Git eller som apne statiske filer.
3. Ny publiseringsretning er:
   - lokal SQL og lokal pipeline
   - publisering til privat objektlagring
   - beskyttet datatilgang med `Cloudflare Access`
   - innlogging med `Microsoft Entra ID` fra eksisterende Microsoft 365-tenant
4. Frontend skal fortsatt vaere en statisk app, men data skal hentes fra et beskyttet endepunkt, ikke fra apne filer.

## Oppdatert Malbilde

Den nye flyten bor na se slik ut:

1. Lokal scheduler starter pipelinejobben pa din server.
2. Pipelinejobben henter data lokalt fra SQL.
3. Pipelinejobben bygger et lite sett med publiserte JSON-artifacts.
4. Pipelinejobben laster disse opp til en privat `Cloudflare R2`-bucket.
5. `Cloudflare Access` beskytter tilgang til data med `Microsoft Entra ID`.
6. En `Cloudflare Worker` eller tilsvarende beskyttet proxy eksponerer JSON til frontend.
7. Frontend pa `Render` leser data fra det beskyttede endepunktet.

## Sikkerhetsmodell

For denne losningen er det viktig a skille mellom:

- innlogging i selve appen
- beskyttelse av de faktiske datafilene

Det er ikke nok a bare ha login i frontend hvis JSON-filene fortsatt kan lastes direkte fra en offentlig URL.

Minimum anbefalt sikkerhetsniva er derfor:

1. `Render` hoster bare frontend-koden.
2. Data publiseres til privat `R2`.
3. `r2.dev` og annen offentlig bucket-eksponering brukes ikke for sensitive filer.
4. Tilgang styres med `Cloudflare Access`.
5. `Cloudflare Access` kobles til `Microsoft Entra ID`.
6. Gjerne bruk Entra-grupper for ulike innsynsnivaer senere.

## Anbefalt Produksjonsoppsett

### `Render`

Ansvar:

- hoste statisk frontend
- ingen sensitive runtime-filer i repo eller deploy bundle

### `Cloudflare R2`

Ansvar:

- lagre publiserte JSON-filer privat
- vaere datalager for beta og senere produksjon

### `Cloudflare Access`

Ansvar:

- beskytte datadomenet
- kreve innlogging med organisasjonens Microsoft 365-brukere

### `Microsoft Entra ID`

Ansvar:

- identitet og SSO
- eventuelt gruppestyrt autorisasjon

### `Cloudflare Worker`

Ansvar:

- vaere et kontrollert data-endepunkt mellom frontend og R2
- hente ut rett JSON for innlogget bruker
- gi oss et senere sted for:
  - enkel autorisasjon
  - logging
  - versjonering
  - eventuell masking av felter

## Oppdatert Publiseringsstrategi

Publisering bor na designes for dette malbildet:

1. Bygg ferdige JSON-filer lokalt.
2. Valider dem lokalt.
3. Last dem opp til privat `R2`.
4. Oppdater `meta.json` eller et lite manifest til slutt.
5. Frontend leser alltid fra beskyttet data-endepunkt.

Dette betyr i praksis at vi erstatter:

- `git push` som live transport

med:

- `local pipeline -> R2 -> Access/Worker -> Render frontend`

## Oppdatert Vurdering Av Datafiler

Etter arbeidet i betaen ser det na ut som malbildet kan forenkles enda mer:

- butikkvisningene kan bygges fra `butikk_dag.json`
- selgervisningene kan bygges fra `selger_dag.json`
- stock kan i praksis bygges fra en normalisert stock-feed
- `meta.json` beholdes for sist oppdatert

Det betyr at ny pipeline sannsynligvis bor sikte mot et veldig lite sett publiserte filer.

En viktig presisering er at ny pipeline ikke bor bygges rundt to aktive salgskilder.

- `NAV` er aktiv kilde for nye oppdateringer
- `Visma` bor behandles som historisk seed-data

Se ogsa [docs/architecture/PIPELINE_PLAN.md](/C:/Users/una/Documents/New%20project/hibernian-beta-copy/docs/architecture/PIPELINE_PLAN.md).

## Maal

Lage en renere og mer moderne versjon av Hibernian der:

- SQL fortsatt kjorer lokalt pa din server
- Render fortsatt bare hoster en statisk frontend
- data kan oppdateres nesten live
- Git ikke lenger brukes som transportmekanisme for runtime-data
- frontend og datapipeline blir tydelig adskilt

## Dagens flyt

Forenklet ser dagens flyt slik ut:

1. Batch-jobber kobler opp VPN og kjorer SQL.
2. Noen SQL-kall skriver JSON direkte.
3. Noen SQL-kall skriver CSV som deretter leses av Python.
4. Flere Python-skript bygger mellomfiler og ferdige publish-filer.
5. `git_push.bat` committer alle endringer til `master`.
6. Render deployer statisk side fra repoet.

## Anbefalt maalbilde

Den nye flyten bor se slik ut:

1. En lokal scheduler starter en tydelig pipelinejobb.
2. Pipelinejobben henter data lokalt fra SQL.
3. Pipelinejobben transformerer data til et lite sett med stabile JSON-artifacts.
4. Pipelinejobben publiserer disse JSON-filene til et statisk datamal uten Git.
5. Frontend pa Render leser JSON direkte fra publisert datakilde.
6. Frontend deployes separat fra dataoppdateringene.

## Anbefalt struktur

Prosjektet deles logisk i to:

### 1. `frontend`

Ansvar:

- UI
- filtrering
- visning
- presentasjonsformatering
- eventuell klient-side cache

Skal inneholde:

- HTML/CSS/JS eller ny Vue 3/Vite-app
- ingen SQL
- ingen batch-jobber
- ingen publish-jobber
- ingen tunge mellomfiler

### 2. `pipeline`

Ansvar:

- SQL-ekstraksjon
- transformasjon
- validering
- generering av publish-klare JSON-filer
- publisering til statisk datamal

Skal inneholde:

- SQL-sporringer
- Python-kode
- konfigurasjon
- logging
- validering av output

## Hva vi beholder

Disse konseptene bor beholdes:

- lokal SQL-kjoring
- JSON som output til frontend
- skillet mellom salgsdata og lager/bestillingsdata
- tidsstempel for siste oppdatering
- egne datafiler for dag, maned, ar, selgere og stock dersom det gir rask frontend

Disse filene/typene er gode kandidater for videre bruk:

- SQL-filer i `input/` og `inputlagersaldo/`
- sentrale transforms i `revamp/scripts/`
- domenelogikk for:
  - dagssalg
  - maanedssammenligning
  - aarssammenligning
  - selgerdata
  - stock og bestillinger

## Hva vi ikke bor viderefore direkte

Disse delene bor fases ut:

- `git_push.bat`
- commit til `master` for hver dataoppdatering
- blanding av gamle og nye pipelines i samme jobb
- mange sma Python-skript som bare leser en fil og skriver en ny fil uten felles struktur
- formatering til sluttbrukertekst tidlig i pipeline, som `12 345 kr`
- hardkodede credentials i `.bat` og `.py`

## Hvilke gamle skript vi bor beholde

### Behold logikken, men ikke nodvendigvis filene som de er

Disse ser ut til a inneholde nyttig domenelogikk:

- `revamp/scripts/sql2json_nav_salg_fra_22_pr_dag.py`
- `revamp/scripts/sql2json_nav_salg_pr_selger_fra_22.py`
- `revamp/scripts/json_combined_visma_nav_fra_22_pr_dag.py`
- `revamp/scripts/json_combined_visma_nav_selgere_fra_22.py`
- `revamp/scripts/json_month_no_format.py`
- `revamp/scripts/json_compare_months_no_format.py`
- `revamp/scripts/json_year_no_format.py`
- `revamp/scripts/json_sales_months.py`
- `revamp/scripts/json_sales_months_comparisons.py`
- `revamp/scripts/json_sales_years.py`
- `revamp/scripts/json_selgere_maned_ar_fra_22.py`
- `revamp/scripts/merge_stock_orders.py`
- `revamp/scripts/time.py`

### Behold som referanse eller kilde, men ikke som ny hovedflyt

- `get_sql.bat`
- `get_sql_daglig.bat`
- `dashboard_nav_sales.py`
- eldre `backup/*.sql`
- gamle toppnivaa-skript som `salg.py`

## Hvilke skript vi bor sla sammen

Maalet bor vaere noen faa tydelige steg i stedet for mange sma:

### A. `extract_sales.py`

Samler SQL-henting for:

- NAV salg
- Visma salg
- NAV selger
- Visma selger

Output:

- raadata i JSON eller CSV i en egen `artifacts/raw/`-mappe

### B. `extract_stock.py`

Samler SQL-henting for:

- lagerstatus
- bestillinger pa vei
- eventuelle produktmetadata

Output:

- raadata i `artifacts/raw/`

### C. `build_sales_views.py`

Samler dagens logikk fra flere scripts:

- kombinasjon av kilder
- totalrader
- dag
- maned
- ar
- sammenligninger
- selgeraggregeringer

Output:

- `artifacts/publish/sales_daily.json`
- `artifacts/publish/sales_monthly.json`
- `artifacts/publish/sales_monthly_compare.json`
- `artifacts/publish/sales_yearly.json`
- `artifacts/publish/sales_people_daily.json`
- `artifacts/publish/sales_people_monthly.json`
- `artifacts/publish/sales_people_yearly.json`

### D. `build_stock_views.py`

Samler:

- stock
- bestillinger pa vei
- merge-logikk

Output:

- `artifacts/publish/stock.json`

### E. `build_metadata.py`

Samler:

- sist oppdatert
- eventuelt versjon
- eventuelt kildeinfo

Output:

- `artifacts/publish/meta.json`

### F. `publish.py`

Ansvar:

- laste opp ferdige JSON-filer
- oppdatere `latest`-filer atomisk sa frontend ikke leser halvferdige filer
- skrive publiseringslogg

## Anbefalt dataformat

Frontend bor helst fa data i et mer nøytralt format:

- bruk tall som tall, ikke formatterte tekstverdier
- formatter valuta og prosent i frontend
- bruk ISO-datoer eller tydelige datonokler
- hold samme feltnavn mellom views der det er mulig

Eksempel:

I stedet for:

- `"mmoms": "12 345 kr"`

Bruk:

- `"gross_amount": 12345`

Da blir det enklere a:

- filtrere
- sortere
- endre valutaformat
- gjenbruke data i nye widgets

## Hvordan publisering kan gjores uten Git

Publisering bor bli et eget steg etter at alle filer er bygget ferdig.

Prinsipp:

1. Bygg alle publish-filer lokalt.
2. Valider at alle nodvendige filer finnes og har gyldig innhold.
3. Last opp til datamaal.
4. Oppdater en liten manifest- eller metadatafil til slutt.

Frontend leser alltid:

- `meta.json`
- datafiler som `meta.json` peker til

Dette gjor at du senere kan bruke:

- self-hosted filserver
- object storage
- annen statisk hosting

uten a maatte endre frontend mye.

## Hvordan frontend bor lese dataene

Frontend bor ikke lenger anta at data ligger i samme repo som appen.

Den bor heller:

1. Lese en konfigurasjon eller base-URL.
2. Hente `meta.json`.
3. Hente de datafilene som trengs for aktiv visning.
4. Formatere tall og datoer i klienten.

Anbefalt frontend-retning:

- beholde Vue som retning hvis du fortsatt liker det
- oppgradere til Vue 3 + Vite i beta
- bruke en liten composable/service for datahenting
- holde datamodell og presentasjon adskilt

## Stegvis migreringsplan

Dette er anbefalt rekkefolge uten a forstyrre live-losningen.

### Fase 1. Kartlegging og frysing

- behold live-jobbene urort
- dokumenter hvilke JSON-filer dagens app faktisk bruker
- dokumenter hvilke SQL-kilder som mater hvilke visninger
- opprett ny pipeline-mapstruktur i beta-prosjektet

### Fase 2. Ny lokal pipeline side om side

- lag en ny lokal pipeline som skriver til en egen `artifacts/`-mappe
- ikke endre dagens batch-jobber ennå
- sammenlign output fra ny pipeline mot dagens publish-filer

Suksesskriterium:

- ny pipeline genererer samme eller bedre data som dagens løsning

### Fase 3. Frontend kobles til ny lokal output

- la beta-frontend lese fra ny `artifacts/publish/`
- behold live-frontend urort
- test nye dataformat og ny struktur i beta

Suksesskriterium:

- beta viser samme tall som live for kjente perioder

### Fase 4. Ny publiseringsmekanisme

- erstatt `git_push.bat` med `publish.py`
- publiser JSON til valgt datamaal
- behold gammel Git-publish som fallback en periode

Suksesskriterium:

- data kan oppdateres uten commits til GitHub

### Fase 5. Frontend leser ekstern datakilde

- beta-frontend leser publiserte JSON-filer via URL
- test cache, feilhandtering og "sist oppdatert"

Suksesskriterium:

- Render-frontend fungerer uten at datafilene ligger i repoet

### Fase 6. Produksjonsovergang

- stopp Git-basert dataflyt
- behold kode-repo kun for frontend og pipeline-kode
- bruk ny publish-flyt som eneste datakanal

## Konkrete anbefalinger for dette prosjektet

Hvis vi skal vaere pragmatiske, ville jeg gjort dette:

1. Lage ny pipeline i Python med 4-6 tydelige steg.
2. Beholde SQL lokalt, men sentralisere all tilkobling og config.
3. Slutte a formatere tall til tekst i pipeline.
4. Modernisere frontend i beta uten a kreve backend pa Render.
5. Erstatte Git-publish med en opplastingsjobb nar betaen er klar.

## Neste steg

Anbefalt neste arbeidspakke er:

1. definere ny mappe- og filstruktur for `pipeline/`
2. velge hvilke av dagens skript som blir kilde for hver nye modul
3. lage et lite manifest for publish-filene
4. begynne med `extract_sales.py` og `build_sales_views.py`
