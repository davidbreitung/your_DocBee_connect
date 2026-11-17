# Your Docbee Connect für Home Assistant – Handbuch

## Stand und Voraussetzungen

Version 0.2.3 implementiert die Einrichtung über die Oberfläche, Benutzer- und
Queue-Geräte, Benutzername- und Ticketzähler-Sensoren, regelmäßige Aktualisierung
und Token-Erneuerung.
Automatisierte Tests laufen mit Home Assistant Core 2025.6.3 und Python 3.13.
Ältere Versionen werden nicht unterstützt; neuere Versionen wurden nicht separat getestet.

Die API-Anbindung folgt der öffentlich erreichbaren DocBee-OpenAPI-Spezifikation
2026.2.0. **Ein Live-Test mit einer authentifizierten DocBee-Instanz steht noch aus.**
Die Tests prüfen die dokumentierte Struktur mit simulierten API-Antworten.

Benötigt werden eine per HTTPS erreichbare DocBee-Instanz mit gültigem
TLS-Zertifikat und ein Access Token mit Leseberechtigung für Benutzer, Queues,
Prioritäten und Vorgänge. Home Assistant muss den Host der Instanz erreichen können.
Alle Zähler beziehen sich auf die für den Token sichtbaren Vorgänge. Für
instanzweite Gesamtzahlen benötigt der Token Zugriff auf alle Vorgänge.

## Installation

### Über HACS / Marketplace

1. In HACS den Dialog zum Hinzufügen über einen GitHub-Link öffnen
   (je nach Version unter „Benutzerdefinierte Repositories“).
2. `https://github.com/davidbreitung/your_DocBee_connect` eintragen.
   Falls eine Kategorie abgefragt wird, **Integration** auswählen.
3. **Your Docbee Connect** hinzufügen und herunterladen/installieren. Falls eine
   Versionsauswahl erscheint, kann der Standardbranch **main** verwendet werden.
4. Home Assistant neu starten.
5. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen**
   nach **Your Docbee Connect** suchen und die Verbindung wie unten beschrieben einrichten.

Das Repository enthält `hacs.json` im Stammverzeichnis; die Integration liegt
unter `custom_components/docbee`. Wird weiterhin eine fehlende `hacs.json`
gemeldet, den Hinzufügen-Dialog schließen, HACS neu laden und erneut versuchen.

### Manuelle Installation

1. Den Ordner `custom_components/docbee` aus diesem Repository nach
   `<Home-Assistant-Konfigurationsverzeichnis>/custom_components/docbee`
   kopieren. `manifest.json` muss direkt in diesem Zielordner liegen.
2. Home Assistant neu starten.
3. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
   **Your Docbee Connect** suchen. Falls sie nicht erscheint, den Browser neu laden und
   die Home-Assistant-Protokolle prüfen.

Es ist keine YAML-Konfiguration nötig. Bei manuellen Updates den Integrationsordner
durch die neue Version ersetzen und Home Assistant neu starten. Bei Installation
über HACS können Aktualisierungen dort heruntergeladen werden.

Die interne Integrationskennung und der Installationsordner heißen weiterhin
`docbee`. Bestehende Geräte und Entitäten behalten ihre Identitäten. Bereits
gespeicherte Eintragsnamen werden nicht überschrieben; einen bisherigen Namen
„DocBee (URL)“ kannst du in Home Assistant bei Bedarf manuell umbenennen.

## Verbindung bei der Ersteinrichtung

1. In DocBee einen Access Token erzeugen. Laut öffentlicher Dokumentation
   befindet sich diese Funktion beim Benutzericon unter
   **Einstellungen → Access Token**. Die Oberfläche kann versionsabhängig abweichen.
2. Im Einrichtungsdialog von Your Docbee Connect in Home Assistant die HTTPS-URL der Instanz
   eingeben, zum Beispiel `https://firma.example`. Ein abschließendes `/restApi`
   wird automatisch entfernt. Installationen unter einem URL-Unterpfad sind möglich.
3. Den Access Token in das verdeckte Feld eintragen und absenden.
4. Die Integration prüft vor dem Speichern den Abruf von Benutzern, Queues, Prioritäten und Vorgängen einschließlich
   Seitennavigation. Bei Fehlern bleibt der Einrichtungsdialog offen.
5. Eine bereits eingerichtete Instanz-URL wird als Duplikat erkannt.

Das DocBee-Passwort wird nicht benötigt. Der Token wird in der internen
Home-Assistant-Konfiguration gespeichert; Backups und Zugriff auf das
Konfigurationsverzeichnis entsprechend schützen. Tokens nicht in Logs,
Screenshots oder Fehlerberichte aufnehmen. Zertifikatsprüfung bleibt aktiv;
HTTP und Weiterleitungen werden nicht akzeptiert.

## Geräte und Entitäten

| Typ | Gerätename | Modell | Entitäten |
| --- | --- | --- | --- |
| Zentrale Konfiguration | Zentrale Konfiguration | Zentrale Konfiguration | „Vorgänge offen“, „Vorgänge Prio 1“ |
| Benutzer | Anzeigename (`name`) aus DocBee | Benutzer | „Benutzername“, „Rolle“, „Aktiv“, „Zugewiesene Vorgänge“ |
| Queue | Queue-Name aus DocBee | Queues | „Aktuelle Tickets“ |

Das zentrale Gerät wird ausdrücklich registriert. Jeder Benutzer und jede Queue
erhält ein eigenes virtuelles Gerät. Identitäten basieren auf Konfiguration,
Gerätetyp und DocBee-ID. Gleichnamige Benutzer bleiben
getrennt; Änderungen am Anzeigenamen aktualisieren den Gerätenamen, Änderungen am
Benutzernamen den Sensorzustand. Es entstehen dabei keine neuen Entitäten.
Fehlt der Anzeigename oder ist er leer, dient der Benutzername als Ersatz. Ein manuell vergebener Gerätename in Home Assistant bleibt erhalten.
Home Assistant erzeugt die tatsächlichen `sensor.*`-Entitäts-IDs; es gibt
keine fest vorgegebenen IDs. Sie können in der Entitätsverwaltung angepasst werden.

### Gruppierung in Home Assistant

Die Integrationsansicht enthält drei getrennte Konfigurations-Untereinträge:

- **Zentrale Konfiguration:** das zentrale virtuelle Gerät mit Gesamtzählern.
- **Benutzer:** alle virtuellen Benutzergeräte und ihre Entitäten.
- **Queues:** alle virtuellen Queue-Geräte und ihre Entitäten.

Die Bereiche lassen sich in der Integrationsansicht aufklappen. Sie gehören
zur selben DocBee-Verbindung und verwenden denselben Token und Datenabruf.
Die Zuordnung erfolgt über native Home-Assistant-Untereinträge, nicht nur über
das Gerätemodell. Die Gerätemodelle bleiben zusätzlich zum Filtern erhalten.
Es werden keine Dashboard-Karten oder Gruppenhelfer angelegt.

Nach dem Update und Neustart werden bestehende Geräte und Entitäten automatisch
in ihre Bereiche übernommen. Geräte-IDs, Entitäts-IDs, individuelle Namen und
bestehende Zuordnungen bleiben erhalten. Auch später neu erkannte Benutzer und
Queues landen automatisch im passenden Bereich. Die drei Bereiche werden von
der Integration verwaltet; entfernte Bereiche werden beim nächsten Einrichten
neu angelegt. Die Darstellung setzt eine Home-Assistant-Oberfläche mit
Unterstützung für Konfigurations-Untereinträge voraus (Core-Testbasis 2025.6.3).

### Rolle und Aktiv-Status

- **Rolle:** Anzeigename der zugeordneten DocBee-Rolle (`permissionGroup.name`).
  Die Rollen-ID steht zusätzlich im Attribut `permission_group_id`. Die Rolle
  ist die Berechtigungsgruppe des Benutzers, nicht eine Liste einzelner Rechte.
- **Aktiv:** Das DocBee-Feld `enabled`, in der deutschen Oberfläche als **Ja**
  oder **Nein** angezeigt. Für Automationen sind die Zustandswerte `yes` und `no`.
  Dies ist der Aktivierungsstatus des Kontos, keine Online-/Anwesenheitsanzeige.

Beide Werte werden mit dem regulären Fünf-Minuten-Abruf aktualisiert. Auch
inaktive Benutzer behalten ihr Gerät und ihre Entitäten. Fehlende Werte werden
als unbekannt dargestellt, nicht als „Nein“ oder als erfundene Rolle. Falls DocBee
nur eine Rollen-ID liefert, bleibt der Rollenname unbekannt und die ID im Attribut
erhalten. Bei Abruffehlern oder einem entfernten Benutzer sind die Entitäten
wie die übrigen Benutzersensoren nicht verfügbar. Die Integration ändert weder
Rollen noch den Aktiv-Status in DocBee.

### Bedeutung der Ticketzähler

Alle Zähler berücksichtigen ausschließlich **nicht abgeschlossene Vorgänge**
(`notClosed=true`). „Offen“ bedeutet hier nicht abgeschlossen und keinen
bestimmten benannten Status. Auch pausierte, aber nicht geschlossene Vorgänge
sind entsprechend der DocBee-Filtersemantik enthalten.

- **Zugewiesene Vorgänge:** `owner` entspricht der Benutzer-ID, also dem Feld
  „Verantwortlicher“. Der Sperrstatus `isLocked` spielt keine Rolle.
- **Aktuelle Tickets:** `owner` entspricht der Queue-ID. Alle von der API
  gelieferten Queues erhalten ein Gerät, auch solche ohne aktuelle Vorgänge.
- **Vorgänge offen:** Gesamtzahl aller nicht abgeschlossenen sichtbaren Vorgänge,
  einschließlich Vorgängen ohne Verantwortlichen.
- **Vorgänge Prio 1:** Nicht abgeschlossene Vorgänge mit einer Priorität, deren
  numerischer Prioritätswert **100** ist. Maßgeblich ist der Wert, nicht die ID
  oder die Bezeichnung; mehrere Prioritäten mit Wert 100 werden gemeinsam gezählt.

Prioritätswerte werden auch als gleichwertige Zahlenformate wie `100.0`,
`"100"` oder `"100.0"` akzeptiert. Fehlt ein Prioritätswert, ist er ungültig
oder verweist ein Vorgang auf eine nicht gelieferte Priorität, wird ausschließlich
„Vorgänge Prio 1“ als nicht verfügbar markiert. Die Einrichtung und die übrigen
Sensoren funktionieren weiter. Nach einem gültigen Abruf wird der Sensor wieder
verfügbar. Ein Hinweis im Protokoll nennt bei ungültigen Werten nur den Datentyp,
keine Rohdaten. Diese Behandlung behebt den bisherigen vollständigen
Einrichtungsabbruch mit „Invalid priority value“; das genaue Antwortformat der
betroffenen Instanz wurde noch nicht direkt geprüft.

Leere Zählmengen ergeben `0`. Bei einem fehlerhaften oder unvollständigen Abruf
werden die Sensoren dagegen als nicht verfügbar markiert. Es gibt keinen Sensor
„Vorgänge in Bearbeitung“. „Offene Tagesabschlüsse“ wurde auf Wunsch verworfen
und wird nicht als Entität angelegt.

## Aktualisierung und Lebenszyklus

- Alle fünf Minuten wird ein vollständiger Datenstand aus Benutzern, Queues, Prioritäten und offenen Vorgängen abgefragt.
- Neue Benutzer und Queues erzeugen automatisch Geräte und Sensoren.
- Umbenennungen aktualisieren den Sensorzustand und den standardmäßigen Gerätenamen.
- Nicht mehr gelieferte Benutzer und Queues bleiben registriert, ihre Sensoren werden
  `unavailable`. So gehen individuelle Namen und Historie nicht verloren.
  Bei erneutem Auftreten derselben ID wird die Entität wieder verfügbar.
- Bei Verbindungsfehlern werden Sensoren als nicht verfügbar markiert.
  Ein fehlgeschlagener Teilabruf ersetzt nicht den letzten vollständigen Snapshot.
- Ohne Benutzer bleibt das zentrale Gerät erhalten.
- Neuladen der Integration startet den Abruf erneut. Entfernen der Integration
  entfernt ihre Zuordnung in Home Assistant; in DocBee werden keine Daten geändert.

Die Integration verwendet ausschließlich GET-Anfragen. Sie verändert weder
Vorgänge noch Zuordnungen in DocBee.

## Token erneuern und Fehler beheben

| Meldung/Zustand | Bedeutung und Maßnahme |
| --- | --- |
| Ungültige Eingabe | HTTPS-Instanz-URL ohne eingebettete Zugangsdaten, Query oder Fragment sowie nicht leeren Token eingeben. |
| Authentifizierung fehlgeschlagen | HTTP 401/403: Token, Ablaufdatum und Leseberechtigungen für Benutzer, Queues, Prioritäten und Vorgänge prüfen. |
| Nicht erreichbar | Netzwerk, DNS, URL, TLS-Zertifikat oder HTTP-Fehler prüfen. Auch Weiterleitungen werden abgelehnt; die direkte Instanz-URL verwenden. |
| Unerwartete Antwort | JSON-Struktur, Pflichtfelder und Pagination weichen vom implementierten Vertrag ab. Anonymisierte Probe bereitstellen, siehe unten. |
| Sensor nicht verfügbar | Abruf fehlgeschlagen oder Benutzer/Queue nicht mehr im API-Ergebnis. Integrationsstatus und Berechtigungen prüfen. |

Wird ein Token im laufenden Betrieb zurückgewiesen, fordert Home Assistant
zur erneuten Authentifizierung auf. Dort einen neuen Access Token eintragen.
Erst nach erfolgreicher Prüfung wird er gespeichert und die Integration
neu geladen. Bei temporären Startfehlern versucht Home Assistant die
Einrichtung später erneut.

## API-Vertrag

Quellen:

- Überblick: <https://documentation.docbee.com/rest_api/>
- Detaildokumentation: <https://my.docbee.com/restApi/v1/documentation#overview>
- OpenAPI-Spezifikation 2026.2.0: <https://my.docbee.com/restApi/v1/openapi.json>

Die Detaildokumentation ist direkt über die URL erreichbar; ein Menüpunkt in
DocBee ist dafür nicht erforderlich. Für die Einrichtung wird weiterhin die
URL der eigenen Instanz verwendet, nicht automatisch `my.docbee.com`.

Der Client verwendet Bearer-Authentifizierung und
`GET /restApi/v1/user?fields=id,username,name,enabled,permissionGroup.id,permissionGroup.name&limit=50&offset=N&sortings=id%20asc`.
Ein Token kann direkt in DocBee erzeugt werden; ein Login-Aufruf ist dann unnötig.
Die Antwort folgt dem dokumentierten Schema `UserList`, zum Beispiel:

```json
{
  "user": [{"id": 1, "username": "beispiel", "name": "Beispiel Benutzer", "enabled": true, "permissionGroup": {"id": 17, "name": "Techniker"}}],
  "totalCount": 1,
  "offset": 0,
  "limit": 50
}
```

Der Client liest die Liste aus `user` und erhöht den Offset um die Zahl der
empfangenen Benutzer, bis `totalCount` erreicht ist. Die Sortierung nach ID
stabilisiert die Reihenfolge. Auch kleinere serverseitige Seitengrößen werden
berücksichtigt. Wiederholte IDs, falsche Metadaten, ein vorzeitig leeres Ergebnis,
eine sich während des Abrufs ändernde Gesamtzahl oder mehr als 1.000 Seiten
führen zu einem Fehler. Der nächste Abruf versucht es erneut. Ein neuer
Snapshot wird erst nach erfolgreichem vollständigem Abruf übernommen.
Benutzernamen über 255 Zeichen werden abgelehnt, weil sie nicht als
Home-Assistant-Zustand darstellbar sind.

Der Rollenname wird mit der dokumentierten `fields`-Erweiterung des verknüpften
Objekts `permissionGroup` direkt im Benutzerabruf gelesen.

Für die Zähler werden zusätzlich die Listen `queue` (`id,name`), `priority`
(`id,priority`) und `ticket` (`id,owner,priority`, Filter `notClosed=true`)
unter `/restApi/v1/` abgerufen. Sie verwenden dieselben Metadaten für die
Seitennavigation; die Datensätze stehen im jeweils gleichnamigen Listenfeld.
Die Vorgänge werden pro Aktualisierung einmal vollständig gelesen und lokal
nach Verantwortlichem und Priorität gezählt, nicht für jedes Gerät erneut.
Der Abrufaufwand wächst mit der Anzahl offener Vorgänge (bis zu 50 pro Seite).
Die API-Abfragen sind kein transaktionaler Snapshot; Änderungen während des
Abrufs können bis zur nächsten Aktualisierung zu zeitlichen Abweichungen führen.

### Update von einer früheren Version

Die Dateien aktualisieren und Home Assistant neu starten. Bestehende Geräte-IDs
und Benutzername-Sensoren bleiben erhalten. Neue Sensoren (einschließlich „Rolle“ und „Aktiv“) und Queue-Geräte
werden automatisch ergänzt. Der automatisch erzeugte Benutzer-Gerätename
wechselt auf das DocBee-Feld `name`; manuell vergebene Gerätenamen bleiben
bestehen. Dem bisherigen Token gegebenenfalls die zusätzlichen Leserechte für
Queues, Prioritäten und Vorgänge erteilen.

### Anonymisierte PowerShell-Probe

Diese optionale Diagnose ist zur Klärung des API-Vertrags nicht mehr nötig.
Sie kann bei instanzspezifischen Abweichungen helfen.

Das Skript `scripts/Get-DocBeeApiSample.ps1` benötigt **PowerShell 7** (`pwsh`).
Es fragt Instanz-URL und Token interaktiv ab, führt zwei reine Leseabfragen mit
`limit=2` und `offset=0` beziehungsweise `offset=2` aus und gibt anonymisiertes
JSON aus. IDs und Benutzernamen erhalten innerhalb eines Laufs konsistente
Pseudonyme. Andere skalare Werte werden bis auf numerische Seiten-Metadaten
und Boolesche Werte maskiert; Feldnamen bleiben sichtbar. Fehlerausgaben
enthalten nur den HTTP-Status oder „Verbindungsfehler“.

```powershell
pwsh -File .\scripts\Get-DocBeeApiSample.ps1
```

Vor dem Teilen die Ausgabe dennoch prüfen, insbesondere falls der Server
personenbezogene Daten bereits als JSON-Feldnamen liefert. Keine Tokens oder
Originalantworten teilen. Das Skript wurde hier mangels PowerShell-Laufzeit
nicht ausgeführt. Die Probe zeigt das Format und erste Hinweise auf Pagination;
bei weniger als drei Benutzern lässt sie deren Funktion nicht sicher bestätigen.

## Entwicklung und Tests

Python 3.13 mit Entwicklungsabhängigkeiten verwenden:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Die automatisierten Tests prüfen Anzeigenamen, Ticketzähler und API-Fehler und dokumentierte Seitennavigation, URL-Prüfung,
Identitäten sowie Einrichtung, Duplikate, erneute Authentifizierung, echte
Home-Assistant-Geräte-/Entitätsregistrierung, Benutzeränderungen, Ausfälle und
Entladen der Integration. DocBee-Antworten werden simuliert. Die Tests
ersetzen daher keinen Live-Test mit einer authentifizierten DocBee-Instanz.
