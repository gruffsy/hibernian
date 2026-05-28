# Pipeline

Dette er hjemmet til den nye lokale datapipelinen for Hibernian-beta.

Mål:

- hente data lokalt fra SQL
- bygge publish-klare JSON-filer
- publisere uten Git

## Scaffold som nå er på plass

Strukturen er gjort om til en enkel Python-pakke under:

- `pipeline/src/hibernian_pipeline`

Den er delt i:

- `bootstrap`
- `extract`
- `build`
- `publish`
- `shared`

## Viktige mapper

- `config/`
- `artifacts/raw/`
- `artifacts/state/`
- `artifacts/publish/`
- `sql/sales/`
- `sql/stock/`
- `logs/`

`artifacts/` og `logs/` er scaffoldet for lokale kjøringer, men selve innholdet spores ikke i Git.

## Viktige filer

- `pyproject.toml`
- `config/pipeline.example.json`
- `src/hibernian_pipeline/settings.py`
- `src/hibernian_pipeline/cli.py`
- `src/hibernian_pipeline/publish/local.py`
- `src/hibernian_pipeline/publish/r2.py`

## Hva scaffoldet gjør nå

Foreløpig gir scaffoldet oss:

- en tydelig konfigurasjonsmodell
- faste artifact-paths
- en lokal publish-mapping mot betaens `legacy/frontend-static/data/publish`
- CLI-kommandoer for å inspisere paths, skrive eksempelkonfig og opprette mappestruktur

## Nyttige kommandoer

Fra `pipeline/`-mappen:

```powershell
$env:PYTHONPATH = "src"
python -m hibernian_pipeline.cli paths
python -m hibernian_pipeline.cli plan
python -m hibernian_pipeline.cli init-layout
python -m hibernian_pipeline.cli write-example-config
python -m hibernian_pipeline.cli bootstrap-visma-history
python -m hibernian_pipeline.cli extract-nav-store-day
python -m hibernian_pipeline.cli extract-nav-seller-day
python -m hibernian_pipeline.cli extract-stock
python -m hibernian_pipeline.cli extract-meta
python -m hibernian_pipeline.cli build-store-day
python -m hibernian_pipeline.cli build-seller-day
python -m hibernian_pipeline.cli build-stock
python -m hibernian_pipeline.cli publish-local
python -m hibernian_pipeline.cli publish-r2
python -m hibernian_pipeline.cli refresh-r2
```

`publish-r2` bruker helst R2 access keys fra miljøvariabler:

```powershell
$env:HIBERNIAN_R2_ACCESS_KEY_ID = "..."
$env:HIBERNIAN_R2_SECRET_ACCESS_KEY = "..."
python -m hibernian_pipeline.cli publish-r2
```

Hvis du heller vil bruke Cloudflare API-token, støttes også:

```powershell
$env:HIBERNIAN_CLOUDFLARE_API_TOKEN = "..."
python -m hibernian_pipeline.cli publish-r2
```

Den publiserer disse fire filene til R2 under `latest/`:

- `salg_fra_22_pr_dag_med_total.json`
- `salg_pr_selger_fra_22_pr_dag.json`
- `merged_stock_orders.json`
- `tid.json`

For scheduleren er `refresh-r2` den viktigste kommandoen. Den kjører hele løypa i riktig rekkefølge:

1. bootstrap historikk ved behov
2. extract fra NAV og stock-kilder
3. build av nye publish-artifacts
4. `publish-local`
5. `publish-r2`

## Hva som fortsatt mangler

Foreløpig er dette fortsatt et strukturert utgangspunkt.

Neste implementasjonssteg er:

1. faktisk NAV-ekstraksjon
2. historisk Visma-bootstrap
3. build-logikk for `butikk_dag`, `selger_dag` og `stock`
4. senere ny publish-mekanisme uten Git

## Neste pipeline-retning

Den nÃ¥vÃ¦rende pipelinen fungerer, men den neste store forbedringen er Ã¥ gjÃ¸re SQL-lesingen inkrementell.

Ny modell:

- historikk eldre enn `7` dager behandles som base
- bare siste `7` dager leses pÃ¥ nytt fra SQL
- base og trailing-vindu slÃ¥s sammen i build-steget

Det er scaffoldet egne steder for dette nÃ¥:

- `artifacts/state/`
- `store_day_base_snapshot.json`
- `seller_day_base_snapshot.json`
- `refresh_state.json`

Se [INCREMENTAL_PIPELINE_ARCHITECTURE.md](/C:/Users/una/Documents/New%20project/hibernian-beta-copy/docs/architecture/INCREMENTAL_PIPELINE_ARCHITECTURE.md).

## SQL-first refresh

`refresh-r2` bruker na den nye SQL-baserte innlesingen som standard for butikk- og selgerdata.

Det vil si:

- SQL leses direkte med `7` dagers trailing-vindu
- build-steget bruker `base + hale`
- `refresh_state.json` skrives etter vellykket kjoring

Miljovariabler som trengs for direkte NAV-SQL:

```powershell
$env:HIBERNIAN_NAV_SQL_USERNAME = "..."
$env:HIBERNIAN_NAV_SQL_PASSWORD = "..."
```

Hvis disse ikke finnes, faller extract-modulene tilbake til de gamle lokale NAV JSON-kildene. Det gjor overgangen tryggere mens den nye losningen fases inn.

For a tvinge en historisk backfill av en enkelt dato, for eksempel `20260515`, kan du sette:

```powershell
$env:HIBERNIAN_BACKFILL_START_DATE = "20260515"
python -m hibernian_pipeline.cli refresh-r2
```

Det gjor at extract-steget leser fra denne datoen og fremover for den kjoringen, men vanlig drift fortsetter som vanlig nar variabelen ikke er satt.
