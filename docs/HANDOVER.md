# Übergabe – zuerst lesen

**Stand 17.11.2026.** Projekt: **Your Docbee Connect**, Home-Assistant-Integration
für DocBee. Runtime **0.4.1** (neuester Codecommit: `git log -1`), Entwicklungsbranch
**`main`**, Repository [davidbreitung/your_DocBee_connect](https://github.com/davidbreitung/your_DocBee_connect).
Diese Übergabe ist versioniertes Projektwissen, kein vollständiger Codex-Chatimport.

## In fünf Minuten weiterarbeiten

1. Sauberen Checkout prüfen und `git pull --ff-only origin main` ausführen.
2. `AGENTS.md`, diese Datei, `STATUS.md` und `TODO.md` lesen. Bei technischen
   Fragen `ARCHITECTURE.md` und `DECISIONS.md` hinzunehmen.
3. Linux-/WSL-Testumgebung gemäß [Windows-Anleitung](WINDOWS_SETUP.md) einrichten.
4. `python -m pytest -q`: bisher **106 Tests grün**, keine DocBee-Zugangsdaten nötig.
5. Noch nicht implementierte Arbeit nicht aus Chat-Zusammenfassungen als fertig
   ableiten. Vorher aktuellen Git-Diff/Log ansehen; keine alten Änderungen neu anwenden.

## Was umgesetzt wurde

UI-Einrichtung mit HTTPS/Bearer-Token; HACS; Geräte und native Gruppen für Zentrale
Konfiguration, Benutzer, Queues. Benutzernamen/Anzeigenamen, Rollen, Aktiv-Status,
zugewiesene offene Vorgänge, Queue-Zähler, zentrale offene/Prio-1-Zähler.
Prio-1-Ereignis plus persistenter letzter Ticketnummer. Zentrale Tageszähler
für bearbeitete, neue und geschlossene Tickets in der HA-Zeitzone. Fünf-Minuten-
Polling, Tests und ausführliches [Handbuch](HANDBUCH.md).

## Nutzerentscheidungen, die nicht verloren gehen dürfen

- Exakter Anzeigename **Your Docbee Connect**; Domain bleibt `docbee`.
- Geräte heißen nach DocBees `name`, Benutzername bleibt eigene Entität.
- „Auf Benutzer gesperrt“ wurde präzisiert zu **Verantwortlicher (`owner`)**,
  nicht technische Sperre `isLocked` und nicht tatsächlicher Bearbeiter.
- Alle bisherigen offenen Benutzer-/Queue-/Prio-Zähler schließen abgeschlossene
  Vorgänge aus. Prio 1 = numerischer Prioritätswert **100**, nicht ID 1.
- „In Bearbeitung“ entfällt, da der Status nicht existiert.
- „Offene Tagesabschlüsse“ zuerst gewünscht (alle überfälligen), später ausdrücklich
  verworfen. Nicht erneut hinzufügen, auch wenn die alte Planung im Chat auftaucht.
- Native Untergruppen zentral/Benutzer/Queues statt bloßer Modellkennzeichnungen.
- Prio-Ereignisse sowohl für neue Tickets als auch spätere Hochstufung; Nummer
  zentral anzeigen. Startbasis ohne Meldung aller alten Tickets wurde implementiert
  und erläutert. Polling-Grenzen und Zähler-/Ereignisunterschiede stehen im Handbuch.
- GitHub ist zentrale Quelle; auf `main` arbeiten/pushen. Interne Codex-Dateien oder
  Datenbanken nicht ohne ausdrückliche Freigabe verändern. Keine produktiven Dienste
  im Rahmen der Rechnerwechsel-Dokumentation ändern.

## Probleme und Lösungen aus dem Chat

| Problem | Ergebnis / verbleibende Unsicherheit |
| --- | --- |
| Repository enthielt anfangs nur README | Integration schrittweise neu erstellt; heute vollständiger Code versioniert. |
| Dokumentation zunächst durch Cloud-Proxy blockiert | Domain-Freigabe angefordert/gespeichert, später HTTP 200. Nicht erneut pauschal Netzwerkrichtlinien überschreiben. |
| Öffentliche Übersicht nennt nicht vorhandenen API-Doku-Menüpunkt | Nutzer lieferte direkte URL `/restApi/v1/documentation#overview`; OpenAPI unter `/restApi/v1/openapi.json` gefunden. |
| Antwortformat zunächst nur angenommen | Auf dokumentiertes `user`-Listenfeld mit `totalCount/offset/limit` korrigiert. Keine alten `data`-Annahmen wieder einführen. |
| Erster Push auf `work` statt erwartetem `main` | PR #1 wurde gemergt; danach `main`. `work` ist nur Historie. |
| HACS meldete fehlende `hacs.json` | Stammdatei und `issue_tracker` ergänzt, Manifest-Schemata geprüft. |
| Screenshot „Invalid priority value“ | 0.2.2 toleriert äquivalente Zahlenformen und isoliert ungültige Werte. Echter problematischer Rohwert unbekannt; kein Live-Erfolg behaupten. |
| Modellnamen gruppierten UI nicht | 0.2.3 nutzt ConfigSubentries; Migrationstest schützt IDs und eigene Namen. |
| HA-Testinstallation: Python.h fehlte | Managed Python 3.13 mit Headern statt unvollständigem System-Python verwendet. |
| HA 2025.3.4-Abhängigkeit war zurückgezogen | Testbasis HA 2025.6.3 gewählt. |
| aiodns/pycares inkompatibel | `pycares==4.9.0` in Entwicklungsanforderungen festgehalten. |

## Letzte funktionale Änderungen

- `60d2484`, 0.2.1: Rolle und Aktiv.
- `f2b1e9f`, 0.2.2: Prioritätswert-Fehlerbehandlung.
- `3960216`, 0.2.3: drei echte Untergruppen.
- `ec64ac2`, 0.3.0: Prio-1-Ereignisse und letzte Vorgangsnummer.
- `247eb17`, 0.3.1: drei **zentrale** Tageszähler, 86 Tests.

Nach dem Kontextcommit `5465354` lieferte der Nutzer den History-Pfad und eine
Beispielantwort. Version 0.4.0 ergänzt jetzt die benutzerbezogenen Tageszähler;
der Commit dieser Erweiterung ist über `git log` ersichtlich.

## Woran wir zuletzt fachlich gearbeitet haben

**Neu bestätigt:** Der Nutzer lieferte den Pfad
`/restApi/v1/ticket/{id}/history?exposeDeletedInExpand=true` und eine Beispielantwort:
Array von Gruppen mit `items`; Einträge haben `actor.id`, `actorType`, `userType`,
`date`, `type`, `messages`, `childItems`. Wichtig: Einträge einer Gruppe können
verschiedene Daten haben; immer das Einzeldatum auswerten. Persönliche Namen,
reale Ticket-/Benutzer-IDs und Texte wurden nicht ins Repository übernommen.

**Implementiert in 0.4.0:** „Bearbeitete Tickets heute“ je Benutzer zählt INSERT/
UPDATE mit `actorType=user`, `userType=USER`. „Geschlossene Tickets heute“ zählt
Statushistorien mit `source=USER`, `user`, `date` und CLOSED-Zielstatus. Beide
zählen unterschiedliche Tickets pro Benutzer; `owner` ist dafür irrelevant.
Automatisierungen/Mail-Parser zählen nicht als Benutzeraktivität. Die Kandidaten
kommen aus heute geänderten Tickets, auch bereits geschlossenen. Zeitfenster:
HA-Zeitzone, Mitternacht bis Abrufzeitpunkt. Maximal vier parallele Ticketprüfungen.
Fehlende/ungültige Einzelhistorien verhindern irreführende Teilzahlen und betreffen
nur den jeweiligen neuen Zähler. Bestehende Sensoren bleiben nutzbar.

**Noch unbestätigt:** Anonymer Abruf liefert HTTP 401. History fehlt weiterhin in
der geprüften OpenAPI; Bearer-Unterstützung und Vollständigkeit müssen in der
Nutzerinstanz geprüft werden. Das Beispiel enthält keine Pagination-Angaben.
Statushistorie ist dokumentiert und wird regulär paginiert. Die Kandidatenwahl
setzt voraus, dass DocBee bei jeder relevanten Aktion `modified` aktualisiert.

**Nächster Schritt:** Nutzer aktualisiert und prüft echte Fälle; bei nicht
verfügbaren Zählern anonymisierten Antwortstatus/Schema erheben, keine Tokens
anfordern. Ein fehlender History-Zugriff blockiert die unabhängige Schließungszählung
nicht. Tests: 106 bestanden mit synthetischen Historiendaten. Details in TODO/Handbuch.

## Was diese Sicherung nicht enthält

Keine vollständige Gesprächsabschrift, internen Modellüberlegungen, Original-
Screenshots, persönlichen Namen aus Screenshots, Tokens, Browser-Cookies oder
Rohantworten. Nur zugänglicher Chatkontext und überprüfter Code/Git-Verlauf wurden
zusammengefasst. Nicht verfügbare Sitzungen, entfernte Verläufe oder frühere
nicht sichtbare Informationen konnten nicht rekonstruiert werden.

Die lokale Codex-Historie, App-Einstellungen, Anmeldung und Laufzeitprozesse
werden durch Git nicht übertragen. Die Veröffentlichung der Cloud-Umgebung im
Chat ist von einem Git-Push und von einer Windows-Einrichtung verschieden.
Die aktuelle Desktop-Version/Kontoeinstellungen der beiden Windows-PCs sind
unbekannt; tatsächliche geräteübergreifende Chatverfügbarkeit wurde nicht getestet.

## Startprompt auf dem zweiten Rechner

> Lies AGENTS.md sowie docs/HANDOVER.md, STATUS.md und TODO.md. Prüfe den aktuellen
> Branch und Git-Status. Wir arbeiten an Your Docbee Connect auf main. Fasse den
> tatsächlichen Stand und den nächsten offenen Schritt kurz zusammen. Wende keine
> bereits erledigten Änderungen erneut an. Bearbeite danach meinen neuen Auftrag.
> Ändere keine lokalen Codex-Datenbanken und keine produktiven Dienste.

Am Arbeitsende STATUS/TODO/HANDOVER mit neuen Ergebnissen und Grenzen aktualisieren,
prüfen, committen, pushen. Git-Status sauber hinterlassen, bevor der andere Rechner
weiterarbeitet. Exakte Befehle: [Windows- und Synchronisierungsanleitung](WINDOWS_SETUP.md).

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
