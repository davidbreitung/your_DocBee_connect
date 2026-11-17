# Projektstatus

Stand: **17.11.2026**. Laufzeitversion **0.3.1**, letzter funktionaler Commit
**`247eb17`** („Add daily modified created and closed ticket counters“).
Der folgende Dokumentationscommit ändert weder Runtime-Version noch Dienste.

## Bestätigt implementiert

- HACS-Metadaten, manuelle Installation, deutsche/englische UI-Texte, Handbuch.
- Einrichtung mit URL/Access Token, Duplikatkontrolle, Reauthentifizierung.
- Drei native Bereiche: Zentrale Konfiguration, Benutzer, Queues.
- Benutzergeräte mit Anzeigename; Benutzername, Rolle, Aktiv, zugewiesene offene Vorgänge.
- Queue-Geräte mit „Aktuelle Tickets“, nur nicht abgeschlossene Vorgänge.
- Zentral: „Vorgänge offen“, „Vorgänge Prio 1“ (Wert 100), drei Tageszähler
  (bearbeitet, neu, geschlossen), „Neuer Prio 1 Vorgang“ und Ereignisentität.
- Prio-1-Ereignisbus `docbee_priority_one_ticket`; letzter Wert über Reload hinweg
  gespeichert, Baseline ohne Altalarme beim Start.
- Fünf-Minuten-Polling, vollständige Pagination, Fehlermeldungen, instanzgetrennte
  Identitäten, dynamische Geräte und unverfügbare Sensoren für entfernte Datensätze.
- Migration vorhandener Geräte in Gruppen ohne neue IDs/Verlust eigener Namen.

## Verifikation und Grenzen

Die Suite enthält **86 Tests** und bestand zuletzt in dieser Linux-Cloud-Umgebung
mit Python 3.13, HA Core 2025.6.3 und den Entwicklungsabhängigkeiten. Sie wurde
bei dieser Dokumentationsübergabe erneut ausgeführt. `git diff --check` wird
auch für den Dokumentationsstand geprüft. Windows/WSL-Anleitung ist vorbereitet,
aber auf keinem der Windows-Rechner des Nutzers ausgeführt worden.

Tests simulieren DocBee und verwenden echten HA-Core für die Integration.
Eine vom Agenten durchgeführte authentifizierte Live-Abnahme liegt nicht vor.
Nutzerscreenshots belegen Installation/Ansicht und einen damaligen Prioritätsfehler,
aber nicht die korrekte Live-Zählung aller heute implementierten Funktionen.

## Bekannte Probleme / Einschränkungen

1. **Benutzerbezogene Tageszähler fehlen.** Angefragt: „Bearbeitete Tickets heute“
   und „Geschlossene Tickets heute“ pro ausführendem Benutzer. Zentrale Zähler
   sind fertig, diese Benutzerzähler nicht.
2. Die öffentliche Spezifikation bietet `ticket/{id}/statusChange` mit `user`,
   `date`, `ticketStatus`, `source`. Damit sind Schließungen grundsätzlich
   zuordenbar; diese Auswertung ist noch nicht implementiert.
3. Die DocBee-Änderungskontrolle beschreibt Benutzer und Zeitpunkt allgemeiner
   Änderungen, aber im geprüften OpenAPI-Dokument wurde kein Audit-Endpunkt
   gefunden. Nutzer wurde um den Fetch/XHR-URL-Pfad beim Öffnen der Änderungskontrolle
   gebeten. Er wurde bisher **nicht** geliefert. Ein nicht dokumentierter Browser-
   Endpunkt ist nicht automatisch mit Bearer-Token nutzbar.
4. `Invalid priority value` aus Nutzer-Screenshot wurde defensiv behandelt:
   Zahlenformen werden toleriert, sonst bleibt der Prio-1-Zähler unverfügbar.
   Originalantwort/Typ des problematischen Werts ist unbestätigt.
5. Polling kann kurze Übergänge verpassen; keine rückwirkenden Prio-Ereignisse nach
   Neustart. Sichtrechte beeinflussen alle Zähler und Ereignisse.
6. API-Daten sind kein transaktionaler Snapshot. Ungültige Schema-/Tageszähler-
   Antworten können ein gesamtes Update stoppen. Der Eingabedialog prüft den
   Snapshot; die Tagesabfragen folgen beim Setup/Update.
7. Native Windows-Ausführung der HA-Testumgebung ist nicht erprobt; Linux/WSL
   ist der dokumentierte Testweg. Transitive Abhängigkeiten sind nicht vollständig
   gelockt; Kompatibilitätsgrenze neuerer HA-Versionen nicht nachgewiesen.
8. Kein eigenes Integrationslogo, keine CI-Pipeline, keine automatische Release-
   Veröffentlichung eingerichtet. Screenshot zeigte fehlendes Icon; bisher kein
   eigener Auftrag zur Grafik/Brands-Registrierung.

## Bewusst nicht enthalten

„In Bearbeitung“ und „Offene Tagesabschlüsse“ wurden ausdrücklich verworfen.
Kein MFA-Login, kein Schreiben nach DocBee, kein Webhook oder Polling-Optionsdialog.
Keine lokale Codex-Datenbank oder Authentifizierungsdatei wird mit Git synchronisiert.

## Repository-/Übergabestand

Vor Beginn dieser Übergabe: sauberer Branch `main`, HEAD und `origin/main` identisch
bei `247eb17`; Remote `https://github.com/davidbreitung/your_DocBee_connect.git`.
Historischer Branch `work` bleibt unangetastet. Aktuellen Übertragungsstand stets
mit `git fetch origin` und `git status --short --branch` prüfen, nicht aus dieser
statischen Notiz auf spätere Änderungen schließen.

## Prüfung dieser Kontextübergabe

- Alle sechs angeforderten Kontextdateien sowie Windows-Anleitung und README-
  Verweise angelegt; existierendes Handbuch unverändert erhalten.
- Lokale Markdown-Links und zehn wichtige Ignore-Fälle geprüft.
- 96 historische Git-Dateiversionen auf typische Token-/Privatschlüssel-/JWT-
  Muster und Zugangsdaten in URLs geprüft. Ein URL-Muster traf ausschließlich
  die bewusst ungültige Beispiel-URL in `tests/test_api.py`.
- Neue Dokumentation zusätzlich auf dieselben Muster geprüft, ohne Treffer.
  Das ist eine begrenzte Musterprüfung plus Inhaltsreview, kein mathematischer
  Nachweis, dass beliebig formatierte Geheimnisse niemals enthalten sein können.
- Kein Runtime-Code, keine laufenden Dienste, keine internen Codex-Speicher verändert.
