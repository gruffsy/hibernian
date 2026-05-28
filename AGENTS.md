# AGENTS.md

Dette er en enkel handoff-logg for parallelle sesjoner i prosjektet.

Regler:
- Les alltid denne filen for du starter en ny jobb.
- Oppdater `Current` nar du starter a jobbe.
- Oppdater `Current` igjen nar du avslutter eller setter jobben pa vent.
- Ikke slett historikk med mindre brukeren ber om det.
- Ikke skriv over andres pagående arbeid. Legg heller inn din egen status i `Current` og noter konflikt under `Blockers`.

## Current

```text
status: idle | in_progress | blocked | complete
owner: <agent-navn eller session-id>
started_at: <ISO-8601 tid>
updated_at: <ISO-8601 tid>
objective: <kort beskrivelse av jobben>
scope: <hvilke filer eller deler av appen som er i spill>
next_step: <helt konkret neste steg>
verification: <hva som er testet eller bekreftet>
blockers: <ingen | kort forklaring>
```

## Resume Notes

Bruk denne delen for korte notater som hjelper en annen sesjon a fortsette raskt.

- Hva er ferdig:
- Hva gjenstar:
- Viktige valg:
- Ting som ikke ma rores:

## History

Legg inn korte historikkposter nederst eller under denne seksjonen.

### Template for en ny post

```text
timestamp: <ISO-8601 tid>
owner: <agent-navn eller session-id>
status: <in_progress | blocked | complete>
summary: <kort oppsummering>
files: <list de viktigste filene>
next: <neste steg hvis relevant>
```

## Hand-off pattern

Nar du starter:
1. Les `Current`.
2. Oppdater `owner`, `status`, `started_at`, `updated_at`, `objective`, `scope` og `next_step`.
3. Fortsett arbeidet.

Nar du avslutter:
1. Oppdater `Current` med resultatet.
2. Sett `status` til `complete` eller `blocked`.
3. Fyll inn `verification` og `blockers` tydelig.
4. Legg gjerne til en kort post i `History`.

## Tmux Routine

Dette er den anbefalte ma-ten a jobbe pa fra SSH eller tmux:

```text
1. Les AGENTS.md
2. Sjekk Current for siste status
3. Oppdater Current til at du eier jobben
4. Kjor kommandoen du fikk
5. Oppdater Current med resultatet
6. Fortsett med neste kommando, eller sett status til complete
```

Kort variant du kan bruke som standard beskjed til en annen sesjon:

```text
Les AGENTS.md, ta eierskap til jobben, kjør: <kommando>, og oppdater AGENTS.md nar du er ferdig.
```

Hvis du vil gi en tmux-økt en ren start, bruk gjerne denne rekkefolgen:

```text
les AGENTS.md
oppdater Current med mitt navn / session-id
kjør neste kommando
skriv tilbake status
```

## Conflict Rule

Hvis en annen sesjon allerede har `status: in_progress` pa samme scope:
- vent med a ta over
- eller skriv en kort kommentar i `Resume Notes`
- eller sett din egen jobb til et annet scope

Det viktigste er at `AGENTS.md` alltid viser hvem som har siste aktive eierskap.

## Automatisk Bruk

For a slippe manuell redigering skal denne fila oppdateres av scriptet:

```text
scripts/agent-task.ps1
```

Vanlig bruk:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\agent-task.ps1 -Mode start -Owner tmux -Objective "<jobb>" -Scope "<filer>" -NextStep "<neste steg>"
powershell -ExecutionPolicy Bypass -File .\scripts\agent-task.ps1 -Mode finish -Owner tmux -Objective "<jobb>" -Scope "<filer>" -Summary "<kort resultat>"
```

Hvis du vil at ett kall skal starte, kjorre kommando og avslutte automatisk:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\agent-task.ps1 -Mode run -Owner tmux -Objective "<jobb>" -Scope "<filer>" -Command "<kommando>"
```

Regel:
- tmux-økt og Codex-sesjon skal bruke scriptet i stedet for a redigere `AGENTS.md` for hand
- hvis scriptet brukes riktig, skal `Current` alltid oppdateres automatisk ved start og avslutning
