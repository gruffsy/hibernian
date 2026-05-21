# JSON Reduction Map

## Oppdatert Status Per 18. Mai 2026

Betaen er na videre enn da dette dokumentet ble skrevet forste gang.

Ny status i [frontend/app.js](/C:/Users/una/Documents/New%20project/hibernian-beta-copy/frontend/app.js):

- `dag`, `uke`, `maaned` og `aar` bygges fra `salg_fra_22_pr_dag_med_total.json`
- `selgere` bygges fra `salg_pr_selger_fra_22_pr_dag.json`
- `stock` bygges fra `merged_stock_orders.json`
- `tid.json` brukes fortsatt for sist oppdatert
- `salg_fra_22_pr_mnd_med_total_og_sammenligning.json` beholdes forelopig bare for prognosekortet i maanedsvisningen

Det betyr at betaen na i praksis bruker dette som kjerne:

- `butikk_dag.json`
- `selger_dag.json`
- `stock.json`
- `meta.json`
- eventuelt en egen `month_compare/prognose`-fil midlertidig

## Ny Anbefalt Minimalpakke

Hvis vi tar utgangspunkt i den faktiske beta-appen vi har na, bor ny pipeline sikte mot:

### Kjernefiler

- `butikk_dag.json`
- `selger_dag.json`
- `stock.json`
- `meta.json`

### Midlertidig tilleggsfil

- `month_compare.json`
  - bare hvis vi vil beholde dagens prognosekort

## Oppdatert Lagerkonklusjon

Den nye stock-visningen tyder pa at vi kan forenkle lagerdelen mer enn antatt tidligere.

I stedet for:

- `lager_stock.json`
- `lager_orders.json`

kan malbildet bli:

- `stock.json`

der stock-feed allerede inneholder:

- beholdning
- paller pa lager
- paller pa vei
- bestillinger pa vei per uke

## Oppdatert Filvurdering

### Kan fases ut i ny beta-arkitektur

- `salg_fra_22_pr_mnd_med_total.json`
- `salg_fra_22_pr_aar_med_total.json`
- `salg_pr_selger_fra_22_pr_måned.json`
- `salg_pr_selger_fra_22_pr_år.json`

### Kan trolig fases ut senere

- `lager_stock.sql.json`
  - hvis `merged_stock_orders.json` eller en ny normalisert stock-feed dekker hele behovet

### Beholdes forelopig

- `salg_fra_22_pr_mnd_med_total_og_sammenligning.json`
  - bare for prognose i maaned

## Viktig For Sikkerhetsretningen

Siden ny retning na er `Render + privat R2 + Access + Entra ID`, bor publiserte filer designes som runtime artifacts, ikke som Git-filer.

Det styrker anbefalingen om a holde antallet filer sa lavt som mulig.

Per 18. mai 2026 bruker prosjektet disse JSON-filene i `legacy/frontend-static/data/publish` og `legacy/frontend-static/data/json`.

## Nåværende filer

| Fil | Størrelse | Brukes av | Formål |
|---|---:|---|---|
| `salg_fra_22_pr_dag_med_total.json` | ca. 2.9 MB | beta + classic | butikksalg per dag |
| `salg_fra_22_pr_mnd_med_total.json` | ca. 137 KB | beta + classic | butikksalg per måned |
| `salg_fra_22_pr_mnd_med_total_og_sammenligning.json` | ca. 120 KB | beta + classic | månedssammenligning og prognose |
| `salg_fra_22_pr_aar_med_total.json` | ca. 13 KB | beta + classic | butikksalg per år |
| `salg_pr_selger_fra_22_pr_dag.json` | ca. 17.4 MB | beta + classic | selgersalg per dag |
| `salg_pr_selger_fra_22_pr_måned.json` | ca. 1.1 MB | beta + classic | selgersalg per måned |
| `salg_pr_selger_fra_22_pr_år.json` | ca. 126 KB | beta + classic | selgersalg per år |
| `merged_stock_orders.json` | ca. 66 KB | beta + classic | innkommende lagerordre og stock-feed |
| `lager_stock.sql.json` | ca. 39 KB | classic | lagersaldo, trolig overflodig for beta |
| `tid.json` | 70 B | beta + classic | sist oppdatert |

## Betaen Bruker I Dag

Beta-appen i [frontend/app.js](/C:/Users/una/Documents/New%20project/hibernian-beta-copy/frontend/app.js) leser akkurat nå:

- `salg_fra_22_pr_dag_med_total.json`
- `salg_fra_22_pr_mnd_med_total_og_sammenligning.json`
- `salg_pr_selger_fra_22_pr_dag.json`
- `merged_stock_orders.json`
- `tid.json`

Den leser ikke lenger:

- `salg_fra_22_pr_mnd_med_total.json`
- `salg_fra_22_pr_aar_med_total.json`
- `salg_pr_selger_fra_22_pr_måned.json`
- `salg_pr_selger_fra_22_pr_år.json`

Den bruker heller ikke `lager_stock.sql.json` i betaen per nå.

## Hva Som Egentlig Er Nødvendig For Ny Beta

Hvis vi ser bort fra classic-siden og bare tenker ny beta, kan vi i praksis komme ned til dette:

### Må beholdes

- `butikk_dag.json`
  - dagens `salg_fra_22_pr_dag_med_total.json`
  - dette er nok til å bygge:
    - dag
    - uke
    - måned
    - år
    - hittil samme dag
    - hittil samme ukedag
    - hittil samme dato
    - butikkvise sammenligninger

- `selger_dag.json`
  - dagens `salg_pr_selger_fra_22_pr_dag.json`
  - dette er nok til å bygge:
    - selger dag
    - selger uke
    - selger måned
    - selger år
    - topp 10 og søk

- `stock.json`
  - kan bygges fra dagens `merged_stock_orders.json`
  - dekker beholdning, paller pa lager, paller pa vei og bestillinger pa vei

- `meta.json`
  - dagens `tid.json`
  - kan beholdes som egen fil, eller senere bygges inn i et samlet metadata-endepunkt

## Filer Som Blir Overflødige Etter Rydding

Disse kan fases ut i ny beta når vi er ferdige med å regne dem ut fra dagsfiler i frontend eller ny pipeline:

- `salg_fra_22_pr_mnd_med_total.json`
- `salg_fra_22_pr_aar_med_total.json`
- `salg_pr_selger_fra_22_pr_måned.json`
- `salg_pr_selger_fra_22_pr_år.json`

Begrunnelse:

- måned og år for butikk kan utledes fra `butikk_dag.json`
- måned og år for selgere kan utledes fra `selger_dag.json`
- uke finnes ikke som egen fil i dag, men bygges allerede fra dagsdata

## Fil Som Er Valgfri Etter Rydding

`salg_fra_22_pr_mnd_med_total_og_sammenligning.json` er ikke strengt nødvendig for den nye betaen.

Betaen bruker den i dag bare for å vise månedsprognose og tidligere ferdigberegnede sammenligningsverdier. Selve sammenligningene regnes allerede i stor grad fra dagsdata.

Vi kan derfor velge mellom:

1. Beholde den midlertidig
   - enkelt
   - fortsatt støtte for dagens prognosevisning

2. Fjerne den senere
   - hvis prognose flyttes til egen logikk eller droppes
   - hvis vi vil ha færre spesialfiler

## Praktisk Konklusjon

### Minimal butikk/selger-pakke for ny beta

- `butikk_dag.json`
- `selger_dag.json`
- `meta.json`

### Minimal full pakke hvis lager skal være med

- `butikk_dag.json`
- `selger_dag.json`
- `lager_stock.json`
- `lager_orders.json`
- `meta.json`

## Viktig For Overgangsplan

Så lenge classic-versjonen fortsatt skal kunne åpnes fra betaen, kan vi ikke slette de gamle måned- og årsfilene ennå. De er fortsatt i bruk av [legacy/frontend-static/quasarapp.js](/C:/Users/una/Documents/New%20project/hibernian-beta-copy/legacy/frontend-static/quasarapp.js).

Det betyr:

- classic beholdes: behold alle gamle filer
- ny beta alene: vi kan redusere til noen få dagsbaserte filer

## Anbefalt Neste Steg

1. La live/classic fortsette som nå midlertidig.
2. La ny beta gradvis bruke bare dagsfiler for butikk og selger.
3. Når classic ikke lenger trengs, fjern måned- og årsfilene fra ny pipeline.
4. Vurder om prognose skal ha egen logikk, eller om `salg_fra_22_pr_mnd_med_total_og_sammenligning.json` også kan bort.
