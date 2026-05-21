# Frontend Page Plan

## Hensikt

Dette dokumentet beskriver hvordan den nye frontend-en bor utvikles med utgangspunkt i dagens losning, dagens data og dagens bruksmønster.

Maalet er ikke a lage en helt ny app som bryter med alt folk kjenner. Maalet er a:

- bevare det som fungerer
- modernisere presentasjonen
- gjore mobilopplevelsen mye bedre
- legge til mer dynamikk der brukerne faktisk trenger det

## Grunnprinsipper

### 1. Ikke bryt gjenkjennelse

Den klassiske losningen er kjent i organisasjonen. Sarlig pa dagssiden er:

- butikkrekkefolge
- totalrad
- hvilke tall som vises
- enkel lesbar tabellstruktur

en del av arbeidsvanene til brukerne.

Derfor bor vi:

- beholde samme butikkrekkefolge som standard
- beholde de viktigste kolonnene
- modernisere layout uten a endre logikken unodvendig

### 2. Mobil og desktop skal ikke bare vaere samme tabell i ulik bredde

Brukerne er delt:

- butikkene bruker mest desktop og trenger detaljvisning
- kontoret bruker mye mobil og trenger rask oversikt

Derfor bor vi:

- ha tettere tabeller pa desktop
- ha mer oppsummerte kort og seksjoner pa mobil
- prioritere hva som vises forst forskjellig per enhet

### 3. Ny UI bygges side om side med klassisk versjon

Klassisk visning beholdes som fallback.

Det betyr:

- ny UI kan vaere tydeligere og mer moderne
- gamle brukere skal alltid kunne bytte tilbake
- versjonsvalg lagres i `localStorage`

## Global struktur

Ny frontend bor ha dette overordnede skallet:

- toppnavigasjon med de fem hovedvisningene
- tydelig statuslinje for siste oppdatering
- versjonsbryter mellom `Beta` og `Klassisk`
- konsekvent filteromrade for sider som trenger det
- konsekvent mobilmønster for oppsummering forst, detaljer etterpa

## Side 1: Dag

### Hva som er bra i dag

- den er direkte og rask a lese
- dagens tall kommer tydelig frem
- tidligere dager ligger tett pa og er raske a sammenligne
- butikkrekkefolgen virker innarbeidet
- totalrad gir rask samlet oversikt

### Hva som bor bevares

- butikkrekkefolge som standard
- dagens salg som hovedfokus
- nabolagret logikk med gardsdag og forgarsdag
- kalender for valg av dato
- totalrad
- de viktigste feltene:
  - belop m/moms
  - belop u/moms
  - DB
  - DG
  - antall kunder
  - per kunde

### Hva som bor forbedres

- mobilvisning ma bli mye lettere a lese
- dagens side bor vise tydeligere hva som er valgt dato
- tidligere dager bor kunne komprimeres eller foldes inn
- totalsammendrag kan ligge som et eget oversiktskort pa topp

### Ny desktop-retning

Desktop bor ligne dagens losning, men strammere:

- tabell fortsatt som primarvisning
- litt bedre typografisk hierarki
- sticky header eller tydeligere kolonneoverskrifter
- tydeligere markering av `Totalt`
- kalender og datovalg bor ligge mer ryddig

### Ny mobil-retning

Mobil bor ikke vise full bred tabell som standard.

I stedet:

- ett sammendragskort for valgt dag
- en liste med butikk-kort eller kompakte rader
- hver butikk viser de 3-4 viktigste tallene med mulighet for ekspandering
- tidligere dager som foldbare seksjoner

### Konkret beta-mal

For `Dag` bor vi bygge:

1. `Selected day summary`
2. `Store list`
3. `Previous days accordion`
4. `Calendar picker`

## Side 2: Måned

### Hva som er bra i dag

- siden viser tydelig flere relevante sammenligninger
- den er nyttig som styringsbilde
- den er enkel a skanne pa desktop

### Hva som er svakt i dag

- den er for statisk
- bruker kan ikke velge tidligere maneder fleksibelt
- sammenligning er i praksis hardkodet til naa og i fjor
- det er vanskelig a utforske andre naturlige sammenligninger

### Hva som bor bevares

- sammenligning mot tilsvarende maned i fjor
- fokus pa `hittil i maneden`
- totalrad og butikkvisning

### Hva som bor legges til

- valg av maned
- valg av sammenligningsperiode
- sammenlign med:
  - samme maned i fjor
  - forrige maned
  - hittil i valgt maned mot hittil i annen valgt maned
- tydelig prosent- og belopsdifferanse

### Ny desktop-retning

Desktop bor deles i to lag:

1. filterrad
2. flere visningsblokker

Eksempel:

- toppkort med totaler og differanser
- butikk-tabell for valgt maned
- sammenligningstabell
- eventuell liten trendgraf

### Ny mobil-retning

Mobil bor forenkles til:

- totalstatus for valgt maned
- én primar sammenligning av gangen
- butikkoversikt som kort eller kompakt liste

### Konkret beta-mal

For `Måned` bor vi bygge:

1. `Month selector`
2. `Compare against selector`
3. `Summary cards`
4. `Store comparison table`
5. `Optional trend strip`

## Side 3: År

### Hva som er bra i dag

- den gir rask aarsoversikt
- enkel sammenligning mellom hittil i ar og fjor

### Hva som er svakt i dag

- sammenligningen er for grov
- det er ikke tydelig nok hva som er `YTD` mot helaar
- brukeren far lite hjelp til a tolke utviklingen

### Hva som bor bevares

- butikkniva
- totalrad
- enkel lesbarhet

### Hva som bor forbedres

- tydelig skille mellom:
  - hittil i ar
  - hittil samme dato i fjor
  - eventuelt hele fjor
- bedre forklaring av hva man sammenligner mot
- valgmulighet for ar

### Ny retning

`År` bor bli mer analytisk enn dagens variant, men fortsatt enkel:

- ett oversiktsomrade med hovedtall
- en sammenligning pa butikkniva
- en egen visning av differanse
- eventuelt en enkel trend per maned hittil i ar

### Konkret beta-mal

For `År` bor vi bygge:

1. `Year selector`
2. `Comparison mode selector`
3. `Summary cards`
4. `Store comparison table`
5. `YTD difference table`

## Side 4: Selgere

### Hva som er bra i dag

- dataene er allerede nyttige
- sok og datovalg finnes
- ranking pa salg fungerer som et grunnlag

### Hva som er svakt i dag

- visningen er for enkel
- det er for mye ra tabell og for lite analyse
- selgere kan ikke enkelt sammenligne seg med seg selv over tid
- ledelse far for lite innsikt utover ren sortering

### Hva som bor bevares

- enkel tabellvisning som fallback
- sortering pa salg
- sok
- datoavgrensning

### Hva som bor legges til

- periodevalg:
  - dag
  - maned
  - ar
- sammenligning mot:
  - forrige periode
  - samme periode i fjor
- filter pa butikk
- fokus pa egen utvikling

### Ny desktop-retning

Desktop bor ha:

- filterbar oversikt
- rangeringstabell
- detaljpanel for valgt selger

Detaljpanel kan vise:

- salg i valgt periode
- DB
- rangering
- utvikling mot tidligere perioder

### Ny mobil-retning

Mobil bor vise:

- topp 10 eller valgt butikk
- kortvisning per selger
- enkel bytteknapp for sorteringsmal

### Konkret beta-mal

For `Selgere` bor vi bygge:

1. `Period selector`
2. `Store filter`
3. `Ranking table`
4. `Selected salesperson detail card`
5. `Comparison summary`

## Side 5: Stock Supply

### Hva som er bra i dag

- siden fungerer
- sok er nyttig
- ekspanderbare rader for bestilling pa vei er riktig modell

### Hva som bor bevares

- sok
- lagerkolonner
- ekspandering av linjer
- fokus pa faktisk nytte fremfor pynt

### Hva som bor forbedres

- tydeligere sokefelt
- strammere layout
- bedre lesbarhet pa mindre skjermer
- tydeligere visning av bestilling pa vei

### Ny retning

Dette er den siden vi bor endre minst funksjonelt.

Betaen bor fokusere pa:

- bedre visuell struktur
- tydeligere sok
- mer ryddig detaljvisning

## Felles komponenter vi bor bygge tidlig

For a holde ny frontend konsekvent bor vi bygge disse tidlig:

- `TopNav`
- `VersionToggle`
- `LastUpdatedBadge`
- `SummaryCard`
- `StoreTable`
- `ResponsiveStoreList`
- `DateSelector`
- `CompareSelector`
- `SearchInput`

## Foreslaatt innforingsrekkefolge

Frontend-arbeidet bor gjores i denne rekkefolgen:

1. Side 1 `Dag`
   - viktigst for flest brukere
   - minst rom for feil i logikk
   - stor gevinst pa mobil
2. Side 5 `Stock`
   - minst risiko
   - raskt a modernisere
3. Side 2 `Måned`
   - stor funksjonell gevinst
4. Side 3 `År`
   - kan bygge videre pa samme mønster som Måned
5. Side 4 `Selgere`
   - mest potensiale for ny funksjonalitet

## Anbefalt neste steg

For frontend spesifikt bor neste arbeidspakke vaere:

1. lage wireframe-niva plan for `Dag`
2. definere hvilke datafelt som vises pa mobil vs desktop
3. bygge en enkel beta-visning av `Dag` med dagens data
4. la klassisk visning vaere fallback via versjonsbryter

