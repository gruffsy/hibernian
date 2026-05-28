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
status: blocked
owner: desktop-agent
started_at: 2026-05-28T21:17:25+02:00
updated_at: 2026-05-28T21:18:35+02:00
objective: Legge til myk overgang for menyen og publisere endringene til repoet
scope: frontend/app.js, frontend/styles.css
next_step: Logg inn mot GitHub og push `codex/chrome-menu-smooth-collapse`
verification: Commit er laget lokalt på `codex/chrome-menu-smooth-collapse` med hash `73d043f`
blockers: GitHub-push krever autentisering for `https://github.com/gruffsy/hibernian-beta.git`
```

## Resume Notes

Bruk denne delen for korte notater som hjelper en annen sesjon a fortsette raskt.

- Hva er ferdig: Menyen kollapser nå ved scroll, åpner ved topp, og har myk overgang.
- Hva gjenstår: Pushe commit `73d043f` på branch `codex/chrome-menu-smooth-collapse` til `origin`.
- Viktige valg: Toggle-knappen vises bare når menyen er kollapset; menyen er sticky i kollapset tilstand.
- Ting som ikke ma rores: De andre lokale endringene i worktree er ikke del av denne jobben.

## History

Legg inn korte historikkposter nederst eller under denne seksjonen.

```text
timestamp: 2026-05-28T21:15:01+02:00
owner: codex
status: complete
summary: Gjorde menyen utvidet ved start og koblet kollaps til scroll, med knapp kun i kollapset tilstand
files: frontend/app.js, frontend/styles.css, AGENTS.md
next: Ingen
```

```text
timestamp: 2026-05-28T21:18:35+02:00
owner: codex
status: complete
summary: La til myk overgang for menyen og klargjorde repoet for commit/push
files: frontend/app.js, frontend/styles.css, AGENTS.md
next: Ingen
```

```text
timestamp: 2026-05-28T21:18:35+02:00
owner: codex
status: blocked
summary: Commit fullført, men push stoppet av manglende GitHub-autentisering mot origin
files: frontend/app.js, frontend/styles.css
next: Skaff push-tilgang eller autentiser GitHub og kjør push på nytt
```

```text
timestamp: 2026-05-28T21:18:35+02:00
owner: desktop-agent
status: blocked
summary: Overlevert publiseringsjobben med commit `73d043f` klar for push
files: frontend/app.js, frontend/styles.css
next: Autentiser mot GitHub og push branch `codex/chrome-menu-smooth-collapse`
```

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
