# Übergabe – zuerst lesen

**Stand 17.11.2026.** Projekt: **Your Docbee Connect**, Home-Assistant-Integration
für DocBee. Runtime **0.3.1**, letzter Codecommit **`247eb17`**, Entwicklungsbranch
**`main`**, Repository [davidbreitung/your_DocBee_connect](https://github.com/davidbreitung/your_DocBee_connect).
Diese Übergabe ist versioniertes Projektwissen, kein vollständiger Codex-Chatimport.

## In fünf Minuten weiterarbeiten

1. Sauberen Checkout prüfen und `git pull --ff-only origin main` ausführen.
2. `AGENTS.md`, diese Datei, `STATUS.md` und `TODO.md` lesen. Bei technischen
   Fragen `ARCHITECTURE.md` und `DECISIONS.md` hinzunehmen.
3. Linux-/WSL-Testumgebung gemäß [Windows-Anleitung](WINDOWS_SETUP.md) einrichten.
4. `python -m pytest -q`: bisher **86 Tests grün**, keine DocBee-Zugangsdaten nötig.
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

Danach wurden die **benutzerbezogenen** Tageszähler diskutiert, noch nicht gebaut.
Die jetzige Arbeit sichert ausschließlich Dokumentation und Rechnerwechselablauf.

## Woran wir zuletzt fachlich gearbeitet haben

Der Nutzer will zusätzlich pro Benutzer „Bearbeitete Tickets heute“ und
„Geschlossene Tickets heute“ nach der tatsächlich ausführenden Person.

**Bestätigt durch Dokumentationsprüfung:** `modified` am Ticket enthält nur den
Zeitpunkt; `owner` ist nicht der Bearbeiter. `GET /v1/ticket/{id}/statusChange`
liefert `user`, `date`, `ticketStatus`, `source` und ist für Schließungen brauchbar.
Die allgemeine Änderungskontrolle beschreibt laut DocBee Benutzer und Zeitpunkt
aller Änderungen. In der geprüften OpenAPI wurde jedoch kein Audit-Endpunkt gefunden.

**Offen:** Der Nutzer wurde um den URL-Pfad unter Browser-Entwicklertools →
Netzwerk → Fetch/XHR beim Öffnen der Änderungskontrolle gebeten, ohne Tokens/Cookies.
Er lieferte erneut die bekannte Doku-URL, aber noch keinen solchen Anfragepfad.
Ein Audit-Endpunkt kann existieren, ist aktuell aber nicht bestätigt.

**Nächster fachlicher Schritt:** Schließungszähler anhand Statushistorie unabhängig
untersuchen; für allgemeine Bearbeitungszählung Audit-Zugriff klären. Details und
Abnahmekriterien: [TODO](TODO.md). Nicht `owner` als Ersatz-Bearbeiter verwenden.

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
