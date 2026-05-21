# Access And Publish Architecture

Per 18. mai 2026 er dette anbefalt tilgangs- og publiseringsoppsett for Hibernian.

## Beslutning

- `Render` beholdes for frontend
- `Cloudflare R2` brukes for publiserte JSON-filer
- `Cloudflare Access` beskytter datatilgangen
- `Microsoft Entra ID` brukes for SSO med eksisterende Microsoft 365-kontoer
- en liten `Cloudflare Worker` anbefales mellom frontend og `R2`

## Hvorfor

Dette oppsettet gir oss:

- fortsatt enkel statisk frontend
- mye bedre sikkerhet for sensitive bedriftsdata
- mindre Git-ballast
- enklere vei til flere sensitive funksjoner senere

## Hovedflyt

```text
Lokal SQL / batch / Python
        ->
Lokal pipeline
        ->
Private publish JSON i Cloudflare R2
        ->
Cloudflare Access + Microsoft Entra ID
        ->
Cloudflare Worker / protected endpoint
        ->
Render frontend
```

## Ansvarsdeling

### Lokal server

- kjorer SQL
- bygger JSON
- publiserer artifacts

### R2

- lagrer publiserte filer privat
- ikke offentlig bucket for sensitive filer

### Access

- krever innlogging
- kan senere bruke grupper for tilgangsstyring

### Worker

- returnerer bare data til autoriserte brukere
- kan bli stedet for enkel rollelogikk senere

### Render

- hoster bare frontend
- ingen sensitive JSON-filer i offentlig deploy

## Minimum Sikker Versjon

Dette er den minste sikre versjonen vi bor sikte mot:

1. statisk frontend pa `Render`
2. privat `R2`-bucket
3. `Cloudflare Access` koblet mot `Microsoft Entra ID`
4. ett beskyttet endepunkt som returnerer de nyeste JSON-filene

## Ikke Anbefalt

Dette bor vi unnga:

- offentlig bucket
- apne JSON-URL-er
- bare frontend-login uten beskyttet datatilgang
- varig bruk av `presigned URLs` som hovedlosning for intern bedriftsdata

## Mulig Stegvis Innforing

### Fase 1

- behold `Render`
- behold lokal pipeline
- publiser JSON til nytt privat datamal

### Fase 2

- koble `Cloudflare Access` til `Microsoft Entra ID`
- beskytte data-endepunktet

### Fase 3

- la frontend lese bare fra nytt beskyttet endepunkt
- fjerne avhengighet til offentlige statiske datafiler

### Fase 4

- innfore grupper eller roller hvis ulike brukere skal se ulike data

## Aapne Designvalg Senere

Disse tingene trenger ikke avklares for a starte:

- om Worker bare skal proxye filer eller ogsa lage et lite API
- om vi vil beholde faste filnavn eller bruke et manifest
- om roller skal inn i fase 1 eller fase 2
