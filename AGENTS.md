# AGENTS.md

Dette er en enkel handoff-logg for parallelle sesjoner i prosjektet.

Regler:
- Les alltid denne filen for du starter en ny jobb.
- Oppdater `Current` nar du starter a jobbe.
- Oppdater `Current` igjen nar du avslutter eller setter jobben pa vent.
- Ikke slett historikk med mindre brukeren ber om det.
- Ikke skriv over andres pagende arbeid. Legg heller inn din egen status i `Current` og noter konflikt under `Blockers`.

## Current

```text
status: in_progress
owner: codex
started_at: 2026-05-28T22:03:27+02:00
updated_at: 2026-05-28T22:03:27+02:00
objective: Kartlegg og commit/push relevante lokale endringer på smooth-menu-branchen
scope: codex/chrome-menu-smooth-collapse og lokale worktree-endringer
next_step: Inspeksjon av diff og valg av commit-scope
```

## Resume Notes

Bruk denne delen for korte notater som hjelper en annen sesjon a fortsette raskt.

- Hva er ferdig: Menyen kollapser na ved scroll, apner ved topp, og har myk overgang.
- Hva gjenstar: De tre lokale pipeline-datafilene er fortsatt endret lokalt og er ikke del av handoff-jobben.
- Viktige valg: Toggle-knappen vises bare nar menyen er kollapset; menyen er sticky i kollapset tilstand.
- Ting som ikke ma rores: De andre lokale endringene i worktree er ikke del av denne jobben.

## Tmux Recovery Task

Bruk denne oppgaven hvis tmux-okt eller en ny sesjon ikke ser branch eller mister konteksten:

```text
Repo: C:\Users\una\Documents\New project\hibernian-beta-copy
Branch: codex/chrome-menu-smooth-collapse
Maal: fa GitHub og repo-tilstand til a se branchen igjen, og fortsette der vi slapp

Kjor i rekkefolge:
1. cd "C:\Users\una\Documents\New project\hibernian-beta-copy"
2. git status --short
3. gh auth status
4. gh auth setup-git
5. git fetch origin --prune
6. git branch -a -vv
7. git switch --track origin/codex/chrome-menu-smooth-collapse

Hvis branchen allerede finnes lokalt:
- bruk `git switch codex/chrome-menu-smooth-collapse`

Hvis Git fortsatt ber om brukernavn/passord:
- kjør `gh auth login -h github.com`
- og gjenta `gh auth setup-git`
```

## Shortcut Command

Hvis du bare sier:

```text
Les AGENTS.md
```

skal tmux-økten gjøre dette automatisk:
1. Lese `Current`.
2. Oppdatere `Current` til `status: in_progress` og eie jobben hvis `owner` er ledig eller peker på en tidligere sesjon.
3. Hvis `Current` peker på recovery eller branch-problemer, følge `Tmux Recovery Task`.
4. Ellers fortsette fra `next_step` i `Current`.
5. Oppdatere `AGENTS.md` med resultatet når den er ferdig.

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
summary: Commit fullfort, men push stoppet av manglende GitHub-autentisering mot origin
files: frontend/app.js, frontend/styles.css
next: Skaff push-tilgang eller autentiser GitHub og kjør push pa nytt
```

```text
timestamp: 2026-05-28T21:18:35+02:00
owner: desktop-agent
status: blocked
summary: Overlevert publiseringsjobben med commit `73d043f` klar for push
files: frontend/app.js, frontend/styles.css
next: Autentiser mot GitHub og push branch `codex/chrome-menu-smooth-collapse`
```

```text
timestamp: 2026-05-28T21:25:00+02:00
owner: codex
status: complete
summary: Klargjorde repoet for tmux-overlevering etter vellykket GitHub-autentisering og push
files: AGENTS.md
next: Ingen
```

```text
timestamp: 2026-05-28T21:41:28+02:00
owner: codex
status: complete
summary: Leste AGENTS.md og verifiserte at `gh auth status` feiler med ugyldig github.com-token
files: AGENTS.md
next: Re-autentiser GitHub med `gh auth login -h github.com`
```

```text
timestamp: 2026-05-28T21:45:43+02:00
owner: codex
status: complete
summary: Leste AGENTS.md for denne sesjonen og oppdaterte Current etter handoff-reglene
files: AGENTS.md
next: Ingen
```

```text
timestamp: 2026-05-28T21:50:48+02:00
owner: codex
status: complete
summary: Overlot jobben til desktop-agent ved a oppdatere Current med ny eier
files: AGENTS.md
next: Desktop fortsetter fra denne statusen
```

```text
timestamp: 2026-05-28T22:02:49+02:00
owner: codex
status: complete
summary: Gjenopprettet repo-tilstanden og verifiserte at recovery-branchen er lokalt tilgjengelig og i sync med origin
files: AGENTS.md
next: Ingen
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

Hvis du vil gi en tmux-okt en ren start, bruk gjerne denne rekkefolgen:

```text
les AGENTS.md
oppdater Current med mitt navn / session-id
kjor neste kommando
skriv tilbake status
```

## Conflict Rule

Hvis en annen sesjon allerede har `status: in_progress` pa samme scope:
- vent med a ta over
- eller skriv en kort kommentar i `Resume Notes`
- eller sett din egen jobb til et annet scope

Det viktigste er at `AGENTS.md` alltid viser hvem som har siste aktive eierskap.

## Commit Scope Guard

Før enhver commit eller push skal tmux-kjøre scope-guarden:

```text
powershell -ExecutionPolicy Bypass -File .\scripts\git-scope-guard.ps1 -Objective "<kort objektiv>"
```

Regler:
- `legacy/frontend-static/data/publish/*` skal ikke med i UI- eller dokumentasjonsjobber
- de filene får bare være med hvis objektivet tydelig er pipeline, data refresh, R2 eller scheduler
- hvis scope-guarden stopper, skal du ikke fortsette med `git add`, `git commit` eller `git push` før scopet er ryddet
- hvis du faktisk jobber med pipeline/data, bruk `-AllowPipelineData`

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
- tmux-okt og Codex-sesjon skal bruke scriptet i stedet for a redigere `AGENTS.md` for hand
- hvis scriptet brukes riktig, skal `Current` alltid oppdateres automatisk ved start og avslutning
