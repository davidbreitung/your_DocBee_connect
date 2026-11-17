# Your Docbee Connect – Anweisungen für Codex

## Beim Einstieg

- Lies zuerst `docs/HANDOVER.md`, dann `docs/STATUS.md` und `docs/TODO.md`.
  Architektur und Begründungen stehen in `docs/ARCHITECTURE.md` und
  `docs/DECISIONS.md`. Nutzeranleitung: `docs/HANDBUCH.md`.
- Prüfe `git status --short --branch`, Branch und Remote-Stand, bevor du arbeitest.
  Der vereinbarte Entwicklungsbranch ist **main**, nicht der historische Branch
  `work`. Fremde lokale Änderungen erhalten; keine Resets oder Force-Pushes.
- Vor Pull/Merge muss der Arbeitsstand gesichert sein. Bei sauberem Checkout
  `git fetch origin` und `git pull --ff-only origin main` verwenden. Bei Divergenz
  erst untersuchen, nicht blind überschreiben oder Rebase erzwingen.
- Jede Cloud-Aufgabe ist bereits isoliert. Bestehenden Checkout verwenden;
  keinen zusätzlichen Worktree anlegen, außer der Nutzer verlangt es ausdrücklich.
- Aktuelle Nutzeranweisungen haben Vorrang. Ein Dokument mit „offen“ ist keine
  Behauptung, dass die Funktion bereits implementiert oder live geprüft ist.

## Projekt und Konventionen

- Home-Assistant-Custom-Integration, Python 3.13, interne Domain `docbee`.
  Anzeigename exakt **Your Docbee Connect**. Nutzerkommunikation und Handbuch
  auf Deutsch; Quellcode-Bezeichner und englische Basisübersetzungen auf Englisch.
- `custom_components/docbee/` enthält den Laufzeitcode. Keine eigenständige
  Web-App und kein separat zu startender DocBee-Dienst.
- HA-Core-Testbasis: 2025.6.3. Entwicklungsabhängigkeiten stehen in
  `requirements-dev.txt`; nicht beiläufig aktualisieren. Die Versionen sind
  keine vollständige Sperrdatei sämtlicher transitiven Abhängigkeiten.
- Handbuch bei Funktionsänderungen aktualisieren. Neue Benutzeroberflächen-Texte
  in `strings.json` und `translations/de.json` sowie `translations/en.json` pflegen.
- Für nutzbare Funktions-/Fehlerbehebungsupdates Manifest-Version erhöhen;
  reine Dokumentationsänderungen benötigen keine neue Integrationsversion.

## Architekturregeln

- DocBee wird ausschließlich lesend per HTTPS und Bearer-Token angesprochen.
  Shared aiohttp-Session von HA verwenden; TLS-Prüfung nicht deaktivieren.
  Keine Passwörter/MFA-Logins implementieren, ohne dies gesondert zu vereinbaren.
- API-Verträge anhand der OpenAPI prüfen; Feldnamen, Filter und Endpunkte nicht
  erfinden. Nicht dokumentierte Browser-Endpunkte nicht ungeprüft als öffentliche
  Bearer-API behandeln. Produktionszugriffe und Schreibaktionen nicht aus Tests ableiten.
- `owner` bezeichnet Verantwortlichen/Queue, nicht den tatsächlichen Bearbeiter.
  `modified` allein beweist keine Bearbeiter-ID. Benutzerbezogene Tageszähler
  benötigen eine belastbare Zuordnung über Historie/Audit (siehe TODO).
- Prio 1: explizite `priority_one_ids` in ConfigEntry.options haben Vorrang.
  Ohne Auswahl gilt numerischer Wert **100**, niemals automatisch ID 1 oder ein Name.
  Keine instanzspezifischen IDs fest codieren; Optionsänderung lädt die Anbindung
  neu und setzt die Ereignisbasis ohne Altereignisse.
  Zähler offener Vorgänge verwenden `notClosed=true`; Ereignisse und Tageszähler
  haben andere, im Handbuch festgelegte Filter.
- Aktualisierungsintervall fünf Minuten. Tagesgrenzen aus der HA-Zeitzone in UTC
  umrechnen; Sommer-/Winterzeit beachten. Keine fest codierte Europe/Berlin-Zeitzone.
- Geräte-/Entitätsidentitäten erhalten. IDs auf Config-Entry, Typ und DocBee-ID
  aufbauen, nie auf veränderlichen Namen. Nutzerdefinierte Namen erhalten.
- Die drei Bereiche sind native ConfigSubentries: Zentrale Konfiguration,
  Benutzer, Queues. Bei Migration erst neue Gerätezuordnung hinzufügen, dann
  Entitäten zuordnen, zuletzt alte Root-Zuordnung entfernen, sonst löscht HA
  gegebenenfalls Entitäten. Regressionstest dafür erhalten.
- Keine erfundenen Nullwerte bei API-Fehlern. Ungültige Prioritätswerte betreffen
  den Prio-1-Sensor; vollständige Abruffehler erhalten den letzten Vergleichsbestand.
- Prio-1-Ereignisse: Start/Reload setzt Baseline ohne Altereignisse; zuletzt
  gemeldete Vorgangsnummer wird lokal gespeichert. Polling ist keine garantierte
  lückenlose Ereignishistorie. Automationen erhalten jede Nummer im Event-Payload.

## Prüfen, dokumentieren, übergeben

- Relevante bestehende Tests laufen lassen, bei Verhaltensänderungen sinnvolle
  Regressionstests ergänzen. Linux/WSL mit Python 3.13:
  `python -m pytest -q` in der eingerichteten Umgebung. `git diff --check` ausführen.
- Tests verwenden simulierte DocBee-Antworten und echten HA-Core. Grüne Tests
  sind kein Live-Nachweis mit einer authentifizierten DocBee-Instanz.
- Windows-/Rechnerwechsel-Anleitung: `docs/WINDOWS_SETUP.md`. Virtuelle Umgebungen
  und lokale Codex-Speicher nicht kopieren; pro Rechner neu einrichten.
- Vor Gerätewechsel HANDOVER, STATUS, TODO und bei neuen Entscheidungen DECISIONS
  auf den tatsächlichen Stand bringen. Tests, offene Blocker und nächsten Schritt nennen.
- Vor Commit den Diff auf Geheimnisse und personenbezogene Daten prüfen.
  Tokens, `.env`, HA-Konfiguration/Backups, Browser-HARs und lokale Codex-Verläufe
  gehören nicht ins Repository. Keine internen Codex-Dateien/Datenbanken ändern
  oder synchronisieren, ohne ausdrückliche Nutzerfreigabe.
- Commit/Push bei Nutzerauftrag bzw. bestehender Sitzungsautorisierung auf den
  vereinbarten Branch; vor Push Remote-Fortschritt prüfen. Keine produktiven
  Dienste ändern, keine Cloud-Umgebung ohne Auftrag veröffentlichen.
