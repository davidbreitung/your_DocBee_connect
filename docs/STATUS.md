# Projektstatus

Stand: **17.11.2026**. Laufzeitversion **0.5.1**. Neu: Benutzer-Tageszähler anhand von Änderungs- und
Statushistorien. Den exakten neuesten Commit mit `git log -1` prüfen.
Vor dieser Erweiterung war `247eb17` der letzte funktionale Stand (0.3.1).

## Bestätigt implementiert

- HACS-Metadaten, manuelle Installation, deutsche/englische UI-Texte, Handbuch.
- Einrichtung mit URL/Access Token, Duplikatkontrolle, Reauthentifizierung.
- Drei native Bereiche: Zentrale Konfiguration, Benutzer, Queues.
- Benutzergeräte mit Anzeigename; Benutzername, Rolle, Aktiv, zugewiesene offene Vorgänge, heute bearbeitete und heute geschlossene Tickets.
- Queue-Geräte mit „Aktuelle Tickets“, nur nicht abgeschlossene Vorgänge.
- Zentral: „Vorgänge offen“, „Vorgänge Prio 1“ (gewählte IDs, sonst Wert 100), drei Tageszähler
  (bearbeitet, neu, geschlossen), „Neuer Prio 1 Vorgang“ und Ereignisentität.
- Prio-1-Ereignisbus `docbee_priority_one_ticket`; letzter Wert über Reload hinweg
  gespeichert, Baseline ohne Altalarme beim Start.
- Fünf-Minuten-Polling, vollständige Pagination, Fehlermeldungen, instanzgetrennte
  Identitäten, dynamische Geräte und unverfügbare Sensoren für entfernte Datensätze.
- Migration vorhandener Geräte in Gruppen ohne neue IDs/Verlust eigener Namen.

## Verifikation und Grenzen

Die Suite enthält **117 Tests** und bestand zuletzt in dieser Linux-Cloud-Umgebung
mit Python 3.13, HA Core 2025.6.3 und den Entwicklungsabhängigkeiten. Sie wurde
bei der Erweiterung um Benutzer-Tageszähler erneut ausgeführt. `git diff --check` wird
auch für den Dokumentationsstand geprüft. Windows/WSL-Anleitung ist vorbereitet,
aber auf keinem der Windows-Rechner des Nutzers ausgeführt worden.

Tests simulieren DocBee und verwenden echten HA-Core für die Integration.
Eine vom Agenten durchgeführte authentifizierte Live-Abnahme liegt nicht vor.
Nutzerscreenshots belegen Installation/Ansicht und einen damaligen Prioritätsfehler,
aber nicht die korrekte Live-Zählung aller heute implementierten Funktionen.

## Bekannte Probleme / Einschränkungen

1. **Benutzerbezogene Tageszähler sind implementiert, nicht live abgenommen.**
   `actor.id` aus der Änderungshistorie ordnet INSERT/UPDATE zu internen Benutzern;
   Statushistorie ordnet manuelle Schließungen über `user` und CLOSED-Zielstatus zu.
   Pro Ticket/Benutzer wird dedupliziert; Automatisierungen zählen nicht als Benutzer.
2. Für Statushistorie ist `/ticket/{id}/statusChange` dokumentiert. Kandidaten für
   beide Zähler werden per `TICKET_MODIFIED` ermittelt; dabei muss DocBee auch bei
   Statusänderungen das Änderungsdatum pflegen. Vollständig gelöschte/unsichtbare
   Tickets sind nicht erfasst. Manuelle Schließungen werden über `source=USER` gefiltert.
3. Nutzer lieferte `/ticket/{id}/history?exposeDeletedInExpand=true` und ein
   JSON-Beispiel (Gruppenarray mit `items`, `actor`, `date`, `type`, `childItems`).
   In OpenAPI 2026.2.0 weiterhin nicht dokumentiert; anonymer Abruf HTTP 401.
   Bearer-Unterstützung, Zusatzrechte und serverseitige Vollständigkeit sind noch
   unbestätigt. Keine Pagination-Metadaten im Beispiel; unsichtbare Kürzungen sind
   nicht erkennbar. Fehler isolieren die betroffenen neuen Zähler, nicht die
   bisherigen Integrationsfunktionen. Persönliche Beispielinhalte nicht gespeichert.
4. `Invalid priority value` aus Nutzer-Screenshot wurde defensiv behandelt:
   Zahlenformen werden toleriert, sonst bleibt der Prio-1-Zähler unverfügbar.
   Neuer Screenshot bestätigt `NoneType` (Feld fehlt oder null); siehe Nachtrag 0.4.1.
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

## Nachtrag 0.4.1 – fehlende Prioritätswerte

Nutzerscreenshot: Warnung mit `NoneType`; bisher unterschied `row.get()` nicht
zwischen fehlendem Feld und explizitem null. OpenAPI bestätigt weiterhin `priority`
als Zahlenfeld und den Einzelabruf `/v1/priority/{id}` mit `fields=*`.
Fehlende/null Listenwerte werden nun per Einzelabruf nachgeladen; ungültige oder
nicht zugängliche Details bleiben unbekannt, andere Sensoren funktionieren weiter.
Warnungen werden pro Fehlerbild zusammengefasst, statt pro Priorität/Poll wiederholt.
106 Tests bestanden. Nächster Schritt: 0.4.1 live prüfen; bei weiterhin fehlenden
Werten anonymisierte Listen-/Detailstruktur erheben. Keine gesicherte Aussage,
dass der Einzelabruf den instanzspezifischen Datenmangel behebt.

## Aktuell: 0.5.0 – konfigurierbare Prio-1-Auswahl

Der Nutzer lieferte eine vollständige Prioritätsantwort mit `id`, `name`, `color`
und `link`, ohne Zahlenwert `priority`. Auch der Detail-Fallback half nicht.
Der Nutzer hat daher die konfigurierbare Auswahl ausdrücklich beauftragt.
OptionsFlow lädt `id,name` und speichert eine Mehrfachauswahl in
`ConfigEntry.options.priority_one_ids`. Diese hat Vorrang vor Wert 100.
Keine persönlichen Instanz-IDs wurden fest im Code hinterlegt. Leere Auswahl
behält den automatischen Modus; Umbenennungen ändern die ID-Zuordnung nicht.
Fehlende ausgewählte Prioritäten verhindern falsche Nullwerte/Ereignisse.
Optionsänderungen laden neu und setzen eine frische Ereignisbasis ohne Altalarme.
114 Tests bestanden. Nächster Schritt: Nutzer aktualisiert, wählt über
Konfigurieren seine Prio 1 und prüft Zähler sowie eine echte Prioritätsänderung.
Live-Abnahme und Benutzer-History-Abnahme bleiben offen.

## Aktuell: 0.5.1 – HTTP 400 nach Prioritätsauswahl

Nutzer bestätigt gespeicherte Auswahl, Screenshot zeigt danach Setup-Fehler HTTP
400. Die frühere Vermutung einer nicht gespeicherten Auswahl ist widerlegt.
Der auslösende Abruf ist noch nicht live identifiziert. Die öffentliche OpenAPI
bestätigt `priorityIds` (kommagetrennte IDs) und `ticketNumber`; keine unbestätigte
Parameteränderung vorgenommen. HTTP-Fehler nennen nun den anonymisierten Pfad und
Parameternamen ohne Werte. Fehler der Prio-Ereignisticketabfrage (außer Authfehlern)
setzen nur den Ereignisbestand auf unbekannt, nicht den ganzen Snapshot. Zähler
bleiben erhalten, eine unvollständige Ereignismenge wird nie veröffentlicht.
117 Tests bestanden. Nächster Schritt: Nutzer installiert 0.5.1 und liefert bei
weiterem Fehler den neuen Meldungstext. HTTP-400-Ursache weiterhin ungeklärt;
keine bestätigte Live-Behebung behaupten. Keine erneute Prioritätsauswahl nötig.
