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

## Hva som fortsatt mangler

Foreløpig er dette fortsatt et strukturert utgangspunkt.

Neste implementasjonssteg er:

1. faktisk NAV-ekstraksjon
2. historisk Visma-bootstrap
3. build-logikk for `butikk_dag`, `selger_dag` og `stock`
4. senere ny publish-mekanisme uten Git
