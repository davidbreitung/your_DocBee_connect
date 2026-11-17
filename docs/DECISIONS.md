# Entscheidungen und Begründungen

Rekonstruiert am 17.11.2026 aus zugänglichem Chat und Code. Die Reihenfolge ist
inhaltlich; wo keine genaue Entscheidungszeit vorliegt, wird keine erfunden.

| Nr. | Entscheidung | Begründung und Herkunft |
| --- | --- | --- |
| D01 | Custom Integration mit UI-Ersteinrichtung | Nutzerwunsch: Anbindung bei der Ersteinrichtung; keine YAML-Pflicht. |
| D02 | HTTPS mit manuell erzeugtem Bearer-Token | Dokumentierte DocBee-Authentifizierung. Kein gespeichertes DocBee-Passwort und kein interaktiver MFA-Flow. MFA findet bei der Tokenbeschaffung in DocBee statt. Laufzeit bestimmt DocBee, nicht pauschal das 15-Minuten-Login-Beispiel. |
| D03 | Name „Your Docbee Connect“, Domain `docbee` bleibt | Explizite Umbenennung durch Nutzer; technische Kennung beibehalten, um vorhandene Installationen und IDs nicht zu brechen. |
| D04 | Virtuelle Geräte mit ID-basierter Identität | Benutzer-/Queue-Namen können sich ändern. Config-Entry und DocBee-ID sichern stabile Entitäten; manuell gesetzte HA-Namen erhalten. |
| D05 | Benutzer-Gerätename aus `name` statt `username` | Expliziter Nutzerwunsch. Benutzername bleibt eigene Entität, bei fehlendem Anzeigenamen dient er als Ersatz. |
| D06 | Drei native ConfigSubentries | Gerätemodell allein trennte die angezeigten Geräte nicht. Nach Nutzerfeedback echte Bereiche „Zentrale Konfiguration“, „Benutzer“, „Queues“, ohne neue Verbindungen oder Tokens. Frühere Behauptung, es gebe keine passende Gruppierung, wurde damit korrigiert. |
| D07 | Polling alle fünf Minuten, nur GET | Bisherige Implementationsentscheidung, dem Nutzer erläutert. Kein Webhook, keine DocBee-Schreibaktionen. Kurze Zwischenzustände können verloren gehen. |
| D08 | „Gesperrte“ Vorgänge meint Verantwortlicher (`owner`) | Nutzer stellte klar: Unter „Verantwortlicher“ eingetragener Benutzer, nicht `isLocked=true`. `owner` kann auch eine Queue sein. |
| D09 | Ticketzähler nur nicht abgeschlossen | Vom Nutzer bestätigt. Zentrale offene und Prio-1-Zähler sowie Benutzer-/Queue-Zähler nutzen `notClosed=true`. Tageszähler und Ereigniserkennung sind ausdrücklich andere Abfragen. |
| D10 | Prio 1 = Prioritätswert 100 | Nutzer bestätigte Wert 100 und „Prio 1“ in der Bezeichnung. Auf Wert, nicht Name oder ID filtern; mehrere passende Prioritäten gemeinsam zählen. |
| D11 | „In Bearbeitung“ entfällt | Nutzer korrigierte sich: diesen Status gibt es nicht. Keine entsprechende Entität anlegen. |
| D12 | „Offene Tagesabschlüsse“ vorerst verworfen | Nutzer wollte zunächst alle überfälligen Abschlüsse. Screenshot zeigte Monatsübersicht, OpenAPI nur Konfiguration. Danach explizit verworfen; die vorübergehend vorbereitete Entität wurde vor Veröffentlichung entfernt. Nicht ohne neuen Auftrag wieder aktivieren. |
| D13 | Rolle und Aktiv als eigene Sensoren | Nutzerwunsch. Rolle über `permissionGroup.name`, ID als Attribut; Aktiv über `enabled`, kein Anwesenheitsstatus. Fehlende Werte bleiben unbekannt. |
| D14 | Prioritätsfehler blockiert nicht alles | Live-Screenshot zeigte „Invalid priority value“. Zahlenformen tolerieren; bei unbekanntem Wert nur Prio-1-Zähler nicht verfügbar. Tatsächlich problematischer Rohwert wurde nicht geliefert: genaue Ursache unbestätigt. |
| D15 | Prio-1-Ereignis und letzte Vorgangsnummer zentral | Nutzer wollte neue Tickets und nachträgliche Hochstufungen. Eigene EventEntity plus Bus-Ereignis; letztes `ticketNumber` persistent. Kein initialer Alarm für bestehende Tickets. |
| D16 | Ereignisvergleich unabhängig vom geschlossen-Status | Implementationsentscheidung gegen falsche Ereignisse beim Schließen/Wiederöffnen. Abgeschlossene Prio-1-Vorgänge werden beim Vergleich mitgelesen, während Zähler nur offene berücksichtigen. Im Handbuch erklärt. |
| D17 | Tageszähler nach HA-Zeitzone | „Heute“ von lokaler Mitternacht bis Abrufzeitpunkt, nach UTC übersetzt. Sommer-/Winterzeit getestet. Jeder passende Vorgang einmal, keine Summe einzelner Änderungen. |
| D18 | Verantwortlicher ist nicht Bearbeiter | Fachlich entscheidend für offene Benutzer-Tageszähler: `owner` nicht ersatzweise verwenden. Statuswechsel liefern `user`; allgemeine Änderungen brauchen Audit-Zugang. |
| D19 | Entwicklung und Push auf `main` | Ein erster Push ging auf vorgefundenen Branch `work`. Nutzer erwartete `main`, später wurde `work` per PR #1 gemergt. Alle folgenden Änderungen wurden auf `main` gepusht. Keine neue Branch-Strategie ohne Anlass. |
| D20 | GitHub versioniert Projektwissen, keine Codex-Innendaten | Aktueller Auftrag: geräteübergreifende Weiterarbeit mit AGENTS/Architektur/Status/Handover. Keine Manipulation oder Rohsynchronisierung interner Sitzungsdateien/-datenbanken ohne ausdrückliche Freigabe. |

## Noch nicht entschieden / nicht implementiert

- API-Zugang zum allgemeinen Änderungsprotokoll (nicht in geprüfter öffentlicher
  OpenAPI gefunden); damit keine belastbare allgemeine Bearbeiterzählung.
- Details der benutzerbezogenen Schließungszählung: pro Person unterschiedliche
  Tickets, Umgang mit Wiederöffnen/mehrfacher Schließung und automatischen Quellen.
  Dokumentierte Statushistorie bietet eine Grundlage, noch keine fertige Umsetzung.
- Webhook, kürzeres/einstellbares Polling und „Jetzt aktualisieren“-Button wurden
  als Ideen genannt, aber nicht als umgesetzte oder freigegebene Funktionen behandeln.
- Vollständige automatische Synchronisierung lokaler Codex-Sitzungen zwischen
  zwei Windows-Rechnern ist nicht verifiziert; siehe Windows-Anleitung.
