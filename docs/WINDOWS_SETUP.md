# Windows-Rechnerwechsel und Codex-Projektkontext

Stand: 17.11.2026. **GitHub ist die zentrale Quelle für Code und Projektwissen.**
Jeder Rechner hat einen eigenen Checkout und eine eigene Anmeldung/Testumgebung.
Keine gemeinsame Arbeitskopie und keine Live-Synchronisierung über OneDrive,
Dropbox oder ein Netzlaufwerk verwenden.

## Was übertragen wird – und was nicht

| Inhalt | Übertragung / Wiederherstellung |
| --- | --- |
| Integration, Tests, HACS-Metadaten, Hilfsskript | Git commit → push → pull |
| `AGENTS.md`, Architektur, Entscheidungen, Status, TODO, Handover, Handbuch | Dieselbe Git-Historie; vor Rechnerwechsel aktualisieren |
| Python-/Testabhängigkeiten | Pro Rechner aus `requirements-dev.txt` neu installieren |
| `.venv`, Python-/pytest-Caches, Coverage | Nicht versioniert, nicht erforderlich, neu erzeugen |
| Git-Anmeldung | Pro Rechner über Git Credential Manager/SSH, keine Tokens in Git-URLs |
| Codex-App-Anmeldung, persönliche Einstellungen, Berechtigungen | Pro Rechner bzw. über offiziell angebotene Kontofunktionen; nicht aus Git |
| Lokale Codex-Threads, SQLite-Dateien, Session-JSONL, interne IDs | Kein Bestandteil dieses Repositorys; nicht manuell synchronisieren |
| Home-Assistant-Token, `.storage`, Recorder-Historie, Backups | Daten der HA-Instanz, nicht der Entwicklungsrechner; nicht in Git übernehmen |
| Cloud-Snapshot und gespeicherte Umgebungsentwürfe | Plattformzustand, kein Ersatz für Git und keine Windows-Installation |
| Screenshots, echte API-/HAR-Exporte | Nicht zur Entwicklung nötig; bei Diagnose nur ausdrücklich und anonymisiert teilen |

## Lokale Voraussetzungen

- Windows 11 empfohlen, aktuelle Codex-Desktop-App aus offizieller Quelle.
- Git for Windows mit eingerichtetem GitHub-Zugriff (Repository-Lese-/Schreibrechte).
- Ein lokaler Projektordner, z. B. `C:\src\your_DocBee_connect`, außerhalb von
  OneDrive/Cloud-Ordnersynchronisierung. Ordnername/Pfad kann auf PC B abweichen.
- **WSL2 mit Ubuntu** für die HA-Tests. Die Desktop-App kann den Windows-Ordner
  bearbeiten; Tests laufen explizit in WSL. Keine native Windows-Testfähigkeit
  voraussetzen: bisher getestet wurde Linux, nicht Windows.
- Python **3.13** in WSL; `uv` kann einen passenden Interpreter mit Headern
  installieren. C/C++-Buildwerkzeuge sind für native Pakete gegebenenfalls nötig.
- Optional PowerShell **7** (`pwsh`) nur für `scripts/Get-DocBeeApiSample.ps1`.
  Für dieses Entwicklungsvorgehen werden keine echten DocBee-Zugangsdaten benötigt.

Diese Anleitung ist anhand der vorhandenen Linux-Testumgebung vorbereitet,
aber auf einem tatsächlichen Windows-PC noch nicht ausgeführt. Insbesondere
Desktop-App-Version, WSL-Zugriff und Unternehmensrichtlinien lokal prüfen.

## Rechner B einmalig einrichten

### 1. Git-Checkout in PowerShell

Git installieren und Zugriff über den üblichen GitHub-Anmeldeweg einrichten.
Codex-Anmeldung und GitHub-Anmeldung sind getrennte Dinge. Persönliche Git-Identität
bei Bedarf lokal konfigurieren; keine Identität aus fremden Commits übernehmen.

```powershell
git --version
New-Item -ItemType Directory -Force C:\src | Out-Null
Set-Location C:\src
git -c core.autocrlf=false clone https://github.com/davidbreitung/your_DocBee_connect.git
Set-Location C:\src\your_DocBee_connect
git config core.autocrlf false
git switch main
git pull --ff-only origin main
git status --short --branch
```

`core.autocrlf=false` verhindert für diese gemeinsame Windows-/WSL-Arbeitskopie
unnötige Zeilenendenwechsel. Kein globales Git-Setting wird geändert. Existiert
der Ordner bereits, **nicht überschreiben**, sondern dessen Status/Remote prüfen.

### 2. WSL installieren, falls noch nicht vorhanden

In einer administrativen PowerShell, soweit lokal erlaubt:

```powershell
wsl --install -d Ubuntu
```

Gegebenenfalls Windows neu starten und Ubuntu initial mit eigenem Linux-Benutzer
öffnen. Mit `wsl --list --verbose` prüfen, ob Ubuntu Version 2 verwendet. Ein
vorhandenes funktionierendes WSL nicht unnötig neu installieren. Sandbox-/IT-
Beschränkungen nicht umgehen; fehlende Berechtigungen gezielt lokal klären.

### 3. Testumgebung innerhalb von Ubuntu

Die folgenden Befehle **in Ubuntu/WSL**, nicht in PowerShell, ausführen:

```bash
sudo apt-get update
sudo apt-get install -y git python3-venv build-essential ca-certificates
mkdir -p ~/.venvs
python3 -m venv ~/.venvs/codex-tools
~/.venvs/codex-tools/bin/python -m pip install uv
~/.venvs/codex-tools/bin/uv python install 3.13
~/.venvs/codex-tools/bin/uv venv --python 3.13 --python-preference only-managed ~/.venvs/your_docbee_connect
cd /mnt/c/src/your_DocBee_connect
~/.venvs/codex-tools/bin/uv pip install --python ~/.venvs/your_docbee_connect/bin/python -r requirements-dev.txt
~/.venvs/your_docbee_connect/bin/python -m pytest -q
```

Die Python-Umgebung liegt im Linux-Dateisystem und wird nicht mit Windows-Python
geteilt. Das Repository wird nicht ein zweites Mal geklont: `/mnt/c/src/...`
ist derselbe Checkout wie `C:\src\...`. Git-Synchronisierung in diesem Ablauf
über Git for Windows ausführen; nicht gleichzeitig aus Windows und WSL verändern.

Erwartete Testbasis dieses Stands: **99 bestandene Tests**. Native Builds können
bei der ersten Einrichtung dauern. Fehler wie fehlende `Python.h` sprechen für
einen ungeeigneten Interpreter ohne Header; deshalb der managed Python oben.
`pycares==4.9.0` ist absichtlich gepinnt. Bei Installationsfehlern nicht blind
Versionen/TLS-Prüfung ändern, sondern konkreten Fehler prüfen.

Sind bereits entsprechende virtuelle Umgebungen vorhanden, sie erst untersuchen
und wiederverwenden; nicht unbesehen neu erzeugen oder fremde Umgebungen ersetzen.

Spätere Testaufrufe aus PowerShell:

```powershell
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/c/src/your_DocBee_connect && ~/.venvs/your_docbee_connect/bin/python -m pytest -q'
```

Falls Codex die WSL-Ausführung in seiner lokalen Sandbox nicht ausführen darf,
Tests im eigenen WSL-Terminal starten und das Ergebnis mitteilen. Keine globalen
Sicherheitsrichtlinien oder Codex-Innendaten dafür manipulieren.

### 4. Projekt in der Codex-Desktop-App öffnen

1. Auf Rechner B in der App anmelden.
2. Den lokalen Ordner `C:\src\your_DocBee_connect` als Projekt/Ordner öffnen
   (genaue Menübezeichnung abhängig von der App-Version).
3. Vorhandenen geeigneten Chat fortsetzen, falls die App ihn offiziell anbietet,
   oder einen neuen Projektchat starten.
4. Den Startprompt aus `HANDOVER.md` verwenden. `AGENTS.md` liegt im Projektstamm;
   die übrigen Kontextdateien ausdrücklich lesen lassen, nicht ihre automatische
   vollständige Aufnahme in jeden Chat voraussetzen.
5. Erst nach Git-Status-/Kontextprüfung den nächsten Änderungsauftrag geben.

## Einfacher Wechsel A → B → A

Immer nur **ein Rechner bearbeitet denselben Branch aktiv**. Git überträgt nur
Commits; ungesicherte Dateien, Stashes und laufende Codex-Arbeit bleiben lokal.

### Vor Arbeitsbeginn auf jedem Rechner

```powershell
Set-Location C:\src\your_DocBee_connect
git status --short --branch
git switch main
git fetch origin
git pull --ff-only origin main
```

Nur bei sauberem Arbeitsverzeichnis fortfahren. Bei lokalen Änderungen diese
zuerst verstehen/sichern, nicht einfach löschen. `--ff-only` bricht bei divergierenden
Commits sicher ab. Dann Unterschiede mit `git log --oneline --left-right HEAD...origin/main`
prüfen und bewusst zusammenführen lassen; kein `reset --hard` oder Force-Push.

### Zum Abschluss auf Rechner A (ebenso später auf B)

1. Arbeit fertigstellen und relevante Tests ausführen. Keine laufende Codex-
   Bearbeitung auf A weiterlaufen lassen, während B dieselben Dateien ändert.
2. `STATUS.md`, `TODO.md`, `HANDOVER.md` aktualisieren; neue Entscheidungen in
   `DECISIONS.md`, Architektur-/Funktionsänderungen in passenden Dokumenten festhalten.
3. Diff auf Geheimnisse, persönliche Daten und versehentliche lokale Dateien prüfen.

```powershell
git status --short
git diff --check
git diff
# Nur geprüfte Dateien aufnehmen; diese Auswahl gilt für eine Kontextübergabe:
git add AGENTS.md docs README.md .gitignore
git diff --cached --stat
git diff --cached
# Nur committen, wenn tatsächlich gestagte Änderungen vorhanden sind:
git commit -m "Update project context and handover"
git fetch origin
git status --short --branch
git push origin main
```

Bei Codeänderungen die konkret geänderten Code-/Testdateien zusätzlich explizit
stagen. Wenn nach dem Fetch neue Remote-Commits vorliegen, zuerst integrieren und
erneut prüfen; normale Pushes überschreiben keine abweichende Remote-Historie.
Ein abgelehnter Push ist Anlass zur Klärung, nicht zu `--force`.

Auf B anschließend den Arbeitsbeginn-Ablauf ausführen und die aktuelle Übergabe
lesen lassen. Für den Rückweg identisch vorgehen. Die Desktop-App kann dieselben
Git-Schritte anbieten; entscheidend bleiben Commit, Push und Pull, nicht ein
bloß gespeicherter Chat. Auch unfertige Arbeit kann als klar gekennzeichneter,
reviewbarer Zwischenstand übergeben werden; keine Behauptung „fertig“, wenn Tests
fehlen oder Arbeit noch offen ist.

## Umgebungsvariablen und Geheimnisse

Für die automatisierten Tests sind **keine Projekt-Umgebungsvariablen und keine
API-Tokens erforderlich**. Das Projekt lädt derzeit keine `.env`-Datei.

| Einstellung | Woher / Umgang |
| --- | --- |
| DocBee-URL und Access Token | Nur in HA-Ersteinrichtung/Reauth; keine Projekt-Environment-Variablen |
| GitHub-Zugang | Git Credential Manager oder eigener SSH-Schlüssel pro Rechner; nichts davon committen |
| Codex-Anmeldung | Offizieller Login pro App/Rechner; keine Auth-Dateien kopieren |
| `OPENAI_API_KEY` | Für dieses Projekt und seine Tests nicht erforderlich; keine Variable anlegen, nur um das Projekt zu öffnen |
| `CODEX_HOME` | Kein projektspezifischer Override nötig; bestehende App-Konfiguration nicht umbiegen |
| `UV_CACHE_DIR`, `UV_PYTHON_INSTALL_DIR` | Nur in der früheren eingeschränkten Cloud-Umgebung nach `/workspace` umgelegt; auf normalem WSL nicht erforderlich |

In der Cloud liegen aktuell Interpreter/Umgebungen außerhalb des Repositorys
(z. B. `/workspace/docbee-test-venv`, `/workspace/.python`, `/workspace/.cache/uv`).
Sie sind nicht versioniert und nicht als portable Windows-Umgebung geeignet.
Innerhalb des Repositorys sind bislang nur Python-/pytest-Caches ignoriert
vorhanden. Erweiterte Ignore-Regeln schützen künftig lokale `.env`, `.codex`,
`ha-config`, Diagnoseexports und Coverage; `.gitignore` ersetzt keine Diff-Prüfung
und entfernt keine bereits getrackten Geheimnisse aus der Historie.

## Können die eigentlichen Codex-Unterhaltungen synchronisiert werden?

**Git synchronisiert sie nicht.** Dieses Repository sichert eine redigierte,
fachliche Zusammenfassung, keine ausführbare Sitzungsdatenbank und keinen
vollständigen Chatverlauf.

Am 17.11.2026 wurden offizielle OpenAI-Seiten zu Desktop-App, Windows und CLI
geprüft. Die früheren Codex-Dokumentations-URLs leiten inzwischen teilweise auf
`learn.chatgpt.com` weiter. Dokumentiert sind die Wiederaufnahme gespeicherter
Chats (`/resume`) und ein Übergang zur Desktop-App (`/app`), ebenso versions- und
kontenabhängige Cloud-Funktionen. Daraus folgt **keine Zusage**, dass alle lokalen
Windows-Threads automatisch zwischen zwei Computern repliziert werden.

Eine offiziell dokumentierte, von uns verifizierte automatische Synchronisierung
beliebiger lokaler Codex-Sitzungsdateien/-datenbanken zwischen zwei Windows-PCs
wurde nicht festgestellt. Installierte App-Versionen und Einstellungen der
beiden Rechner sind hier nicht bekannt. Das ist keine Behauptung, dass jede
Form geräteübergreifender Chatfortsetzung unmöglich ist.

Sicheres Vorgehen:

- Wenn derselbe Cloud-/Kontochat auf beiden Geräten offiziell angeboten wird,
  ihn dort fortsetzen und den **separaten lokalen Git-Stand** trotzdem abgleichen.
  Verfügbarkeit mit der installierten App testen, nicht aus gleichem Login ableiten.
- Offizielle Export-/Import-/Remote-Funktionen nur verwenden, wenn die konkrete
  App-Version sie anbietet und dokumentiert. Remote-Fortsetzung kann Zugriff auf
  denselben Rechner bedeuten, nicht zwei synchronisierte lokale Checkouts.
- Keine internen Datenbanken, `auth.json`, Session-JSONL oder ganze Codex-Home-
  Verzeichnisse in Git/OneDrive ablegen. Mögliche Probleme sind Geheimnisse,
  parallele Schreibzugriffe, inkompatible Versionen und rechnergebundene Pfade.
- Bestehende Chat-Exporte nur bei Bedarf separat und sicher aufbewahren. Roh-Exporte
  nicht automatisch als sicher/anonymisiert behandeln; für dieses Projekt genügt
  die geprüfte Zusammenfassung im Repository.
- Dieses Vorhaben hat **keine internen Codex-Dateien gelesen, verändert oder kopiert**.

Offizielle Quellen (am 17.11.2026 abgerufen; Inhalte können sich ändern):

- [Desktop-App](https://developers.openai.com/codex/app/) → [aktuelles Ziel](https://learn.chatgpt.com/docs/app)
- [Windows](https://developers.openai.com/codex/windows/) → [Windows-Sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)
- [CLI-Referenz](https://developers.openai.com/codex/cli/reference/) → [Developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

## Was noch vor Ort bestätigt werden muss

Die App auf beiden PCs installieren/anmelden, Repository öffnen, WSL-Tests laufen
lassen und einen echten A/B-Git-Roundtrip durchführen. Lokale Sitzungsübernahme
nur über die angebotenen offiziellen Funktionen testen. Projektwissen und Code
sind auch ohne dieselbe Chat-Sitzung über Git vollständig für die hier dokumentierte
Weiterarbeit verfügbar; nicht zugängliche ältere Gesprächsinhalte sind davon ausgenommen.
