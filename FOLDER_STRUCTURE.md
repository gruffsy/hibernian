# Proposed Folder Structure

Dette er foreslaatt ny struktur for beta-prosjektet. Vi oppretter den side om side med dagens filer for a unnga a bryte lokal preview eller live-logikk.

## Prinsipper

- `frontend/` inneholder bare webapp-kode
- `pipeline/` inneholder lokal dataflyt
- `docs/` inneholder beslutninger og planer
- `legacy/` brukes som midlertidig landingsplass for gammel kode vi ikke vil miste, men heller ikke viderefore uendret

## Tree

```text
hibernian-beta-copy/
├── docs/
│   ├── architecture/
│   └── migration/
├── frontend/
│   ├── public/
│   │   └── mock-data/
│   ├── scripts/
│   └── src/
│       ├── app/
│       ├── components/
│       ├── composables/
│       ├── lib/
│       ├── styles/
│       └── views/
├── legacy/
│   ├── frontend-static/
│   ├── scripts/
│   └── sql/
├── pipeline/
│   ├── artifacts/
│   │   ├── publish/
│   │   └── raw/
│   ├── config/
│   ├── logs/
│   ├── scripts/
│   ├── sql/
│   │   ├── sales/
│   │   └── stock/
│   ├── src/
│   │   └── hibernian_pipeline/
│   │       ├── build/
│   │       ├── extract/
│   │       ├── publish/
│   │       └── shared/
│   └── tests/
├── README.md
├── TARGET_ARCHITECTURE.md
└── dagens beta-filer i rot inntil vi flytter dem kontrollert
```

## Hva som skal inn hvor

### `docs/`

- arkitekturvalg
- migreringsplan
- notater om dataformater

### `frontend/`

Her bygger vi den nye appen.

- `public/mock-data/`
  - lokale eksempeldata for UI-utvikling
- `src/views/`
  - Dag, Måned, År, Selgere, Stock
- `src/components/`
  - tabeller, kort, filtre, statusfelt
- `src/composables/`
  - datahenting, caching, formatering
- `src/lib/`
  - api-klient, hjelpefunksjoner, domeneformattering
- `src/styles/`
  - globale stiler og design tokens
- `scripts/`
  - små hjelpekommandoer for frontend-utvikling

### `pipeline/`

Her bygger vi den nye lokale dataflyten.

- `sql/sales/`
  - SQL for salg, sammenligning og selgere
- `sql/stock/`
  - SQL for lager, bestillinger og produktrelatert data
- `src/hibernian_pipeline/extract/`
  - henter data fra SQL og skriver råfiler
- `src/hibernian_pipeline/build/`
  - bygger views og publish-klare datasett
- `src/hibernian_pipeline/publish/`
  - publiserer ferdige JSON-filer til valgt mål
- `src/hibernian_pipeline/shared/`
  - konfig, databasekobling, logging, felles utils
- `artifacts/raw/`
  - mellomfiler som ikke skal inn i Git
- `artifacts/publish/`
  - ferdige JSON-filer for beta/frontend
- `config/`
  - miljøspesifikk konfigurasjon uten hardkodede secrets
- `scripts/`
  - entrypoints som `run_pipeline.ps1`
- `tests/`
  - validering av transforms og output

### `legacy/`

Her legger vi gammel kode som referanse nar vi begynner a flytte ting kontrollert.

- `frontend-static/`
  - dagens `index.htm` og `quasarapp.js`
- `scripts/`
  - gamle Python- og batch-skript
- `sql/`
  - gamle SQL-filer som beholdes som referanse

## Anbefalt flytting i praksis

Vi bor flytte i denne rekkefolgen:

1. Opprett ny struktur.
2. Kopier inn relevant SQL til `pipeline/sql/`.
3. Lag nye pipeline-moduler i `pipeline/src/hibernian_pipeline/`.
4. La gammel frontend ligge i rot mens ny frontend bygges i `frontend/`.
5. Flytt gammel frontend til `legacy/frontend-static/` nar ny frontend kan previewes trygt.

## Praktisk anbefaling for neste steg

Neste gode steg er a:

1. scaffold-e denne strukturen
2. lage en liten `pipeline/README.md`
3. lage en liten `frontend/README.md`
4. starte med `pipeline/src/hibernian_pipeline/shared/` og `extract/`

## Oppdatert Infra-Retning Per 18. Mai 2026

Etter senere avklaringer er infrastrukturen na tenkt slik:

- `Render` beholdes for frontend
- publiserte data skal ikke hostes offentlig fra repoet
- `Cloudflare R2` er aktuell publish-destinasjon
- `Cloudflare Access` + `Microsoft Entra ID` er aktuell tilgangsmodell
- en liten `Worker` eller proxy bor inn mellom frontend og lagring

Det betyr at `pipeline/publish/` bor designes for mer enn bare "skriv JSON til mappe". Den bor senere kunne:

- laste opp artifacts til privat datamal
- oppdatere metadata/manifest
- publisere til beskyttet runtime-endepunkt
