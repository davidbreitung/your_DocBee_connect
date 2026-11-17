# Your Docbee Connect für Home Assistant – Handbuch

## Stand und Voraussetzungen

Version 0.4.1 implementiert die Einrichtung über die Oberfläche, Benutzer- und
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
| Zentrale Konfiguration | Zentrale Konfiguration | Zentrale Konfiguration | „Vorgänge offen“, „Vorgänge Prio 1“, „Neuer Prio 1 Vorgang“, Ereignis „Prio 1 Vorgangsereignis“, „Bearbeitete Tickets heute“, „Anzahl neue Tickets heute“, „Geschlossene Tickets heute“ |
| Benutzer | Anzeigename (`name`) aus DocBee | Benutzer | „Benutzername“, „Rolle“, „Aktiv“, „Zugewiesene Vorgänge“, „Bearbeitete Tickets heute“, „Geschlossene Tickets heute“ |
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
`"100"` oder `"100.0"` akzeptiert. Fehlt `priority` in der Liste oder ist es
`null`, fragt Version 0.4.1 die betreffende Priorität zusätzlich über den
dokumentierten Endpunkt `GET /restApi/v1/priority/{id}?fields=*` ab.
Bleibt der Wert unbekannt/ungültig oder verweist ein Ticket auf eine unbekannte
Priorität, bleiben „Vorgänge Prio 1“ und der Prio-Ereignisvergleich unverfügbar.
Andere Sensoren funktionieren weiter; unbekannte Werte werden nicht als 0 oder
anhand des Namens interpretiert. Nach gültigen Daten wird die Auswertung fortgesetzt.

Eine zusammengefasste Warnung unterscheidet fehlende Felder (`missing`), explizites
`null` (`NoneType`) und Fehler des Detailabrufs. Sie enthält keine Namen, IDs,
Tokens oder Antwortinhalte und wird beim selben Fehlerbild nicht bei jedem Poll
wiederholt (erneut nach Wiederherstellung oder Neustart möglich).
Der Nutzerscreenshot bestätigt einen fehlenden/null Listenwert; ob der Detailabruf
in der betroffenen Instanz den Wert liefert, ist noch nicht live geprüft.
Falls die Warnung bleibt, reicht ein anonymisiertes Beispiel der Prioritätsliste
und der Detailantwort mit Feldnamen/Datentypen oder der HTTP-Status des Detailabrufs.
Keine Zugangsdaten oder Browser-Cookies weitergeben.

Leere Zählmengen ergeben `0`. Bei einem fehlerhaften oder unvollständigen Abruf
werden die Sensoren dagegen als nicht verfügbar markiert. Es gibt keinen Sensor
„Vorgänge in Bearbeitung“. „Offene Tagesabschlüsse“ wurde auf Wunsch verworfen
und wird nicht als Entität angelegt.

## Tageszähler auf Zentrale Konfiguration

- **Bearbeitete Tickets heute:** Anzahl unterschiedlicher Vorgänge mit letzter
  Änderung heute (`ticketScope=TICKET_MODIFIED`). Mehrere Änderungen an einem
  Vorgang zählen einmal. Auch automatische Änderungen und neu angelegte Vorgänge
  können entsprechend ihrem Änderungsdatum enthalten sein; der Sensor misst
  keine Arbeitszeit und unterscheidet keine menschliche von automatischer Bearbeitung.
- **Anzahl neue Tickets heute:** Vorgänge mit Erstellungsdatum heute
  (`ticketScope=TICKET_CREATED`).
- **Geschlossene Tickets heute:** Vorgänge mit einem laut API heute liegenden
  Schließungsdatum (`ticketScope=TICKET_CLOSED`). Gezählt werden Vorgänge, nicht
  einzelne Schließungsvorgänge. Bei wiederholtem Schließen oder Wiederöffnen ist
  das von DocBee gespeicherte Schließungsdatum maßgeblich; es wird keine vollständige
  Statushistorie rekonstruiert.

Die Abfragen reichen von **00:00 Uhr in der Home-Assistant-Zeitzone bis zum
Abrufzeitpunkt**. Die Zeitgrenzen werden mit dem passenden Zeitzonenversatz nach
UTC umgerechnet, einschließlich Sommer-/Winterzeit. Die drei Werte werden alle
fünf Minuten aktualisiert und beziehen sich nach Mitternacht beim nächsten Abruf
auf den neuen Tag. Die Zähler benötigen keine vorherige lokale Historie und
funktionieren daher auch nach einem Neustart mitten am Tag.

Anders als die Zähler offener Vorgänge verwenden diese Abfragen **keinen**
`notClosed`-Filter. Ein heute neu erstellter oder bearbeiteter und anschließend
geschlossener Vorgang bleibt damit im jeweiligen Tageszähler enthalten. Es werden
nur für den Token sichtbare Vorgänge gezählt. Pro Tageszähler wird eine
Listenabfrage mit `limit=1`, `startDate`, `endDate` und dem jeweiligen `ticketScope`
gestellt und `totalCount` ausgewertet. So funktionieren die Zähler auch über
50 Tickets hinaus, ohne alle Treffer herunterladen zu müssen. Ungültige Antworten
werden nicht als null Vorgänge ausgegeben.

## Tageszähler je Benutzer

Version 0.4.0 ergänzt auf jedem Benutzergerät:

- **Bearbeitete Tickets heute:** Unterschiedliche Tickets, deren Änderungshistorie
  heute einen `INSERT`- oder `UPDATE`-Eintrag dieses Benutzers enthält. Verwendet
  werden `actor.id`, `actorType=user`, `userType=USER` und **das Datum des einzelnen
  Eintrags**, nicht das Datum der äußeren Gruppe. Das umfasst auch manuell erstellte
  Tickets. Automatisierungen, Mail-Parser und Kundenbenutzer werden ausgeschlossen.
  `actor.enabled` beeinflusst die historische Zuordnung nicht.
- **Geschlossene Tickets heute:** Unterschiedliche Tickets mit heutigem
  Statuswechsel dieses Benutzers auf einen Status mit `behaviour=CLOSED`.
  Die Statushistorie liefert `user`, `date`, `ticketStatus`, `source`; gezählt
  werden nur Einträge mit `source=USER`, nicht automatische oder API-Quellen.
  Späteres Wiederöffnen entfernt einen zuvor erfolgten Abschluss nicht aus der
  Tageszählung. Mehrere Abschlüsse desselben Tickets durch denselben Benutzer
  zählen einmal; haben zwei Personen es geschlossen, zählt es für jede einmal.

Der Verantwortliche (`owner`) ist für diese Zähler unerheblich. Die Summe der
Benutzerzähler muss nicht dem zentralen Tageszähler entsprechen: mehrere Personen
können dasselbe Ticket bearbeiten, automatische Änderungen sind zentral enthalten,
und die zentrale Schließungsabfrage wertet keine gesamte Historie aus.

### Datenquelle und Grenzen

Der Nutzer lieferte den Browser-Pfad
`GET /restApi/v1/ticket/{id}/history?exposeDeletedInExpand=true` und eine
Beispielantwort als Array von Gruppen mit `items` und optional verschachtelten
`childItems`. Der Client verarbeitet diese Struktur, ohne Meldungstexte oder Namen
zu speichern oder zu protokollieren. Verschachtelte Einträge müssen eigene
Akteur-/Datumsdaten besitzen; keine Zuordnung über den Elternnamen wird geraten.
Dieser Endpunkt steht **nicht** in der geprüften OpenAPI. Seine Bearer-Unterstützung
und Vollständigkeit sind noch nicht live verifiziert. Ein Abruf ohne Anmeldung
lieferte HTTP 401. Das Beispiel enthält keine Pagination-Metadaten; es wird das
vollständige zurückgegebene Array verarbeitet. Eine nicht erkennbare serverseitige
Kürzung kann die Zählung einschränken und muss bei der Live-Abnahme geprüft werden.

Für Schließungen wird der dokumentierte Endpunkt
`GET /restApi/v1/ticket/{id}/statusChange` mit regulärer Pagination gelesen.
Die Statusdefinitionen kommen aus `/restApi/v1/ticketStatus`. Kandidaten für beide
Zähler sind alle heute laut `TICKET_MODIFIED` geänderten sichtbaren Tickets,
ohne `notClosed`-Filter. Damit werden auch heute bearbeitete geschlossene oder
wieder geöffnete Tickets untersucht. Voraussetzung ist, dass DocBee das
Änderungsdatum bei diesen Aktionen aktualisiert. Gelöschte/nicht mehr sichtbare
Tickets können nicht nachträglich vollständig erfasst werden.

Zeitfenster und Aktualisierung entsprechen den zentralen Tageszählern: HA-Zeitzone,
Mitternacht bis Abrufzeitpunkt, alle fünf Minuten. Es werden bis zu vier Tickets
parallel untersucht; je Ticket sind bis zu zwei Historienabfragen nötig, bei
mehreren Statusseiten entsprechend mehr. Bei großen Tagesmengen kann der Abruf
länger dauern. Keine Historie wird pro Benutzer mehrfach geladen.

Fehlt ein Kandidatenabruf, sind beide Benutzer-Tageszähler nicht verfügbar.
Fehlt nur eine Bearbeitungshistorie, wird kein unvollständiger Bearbeitungszähler
als Zahl ausgegeben; die Schließungszählung kann weiter funktionieren und umgekehrt.
Andere bestehende Sensoren und Ereignisse bleiben bei diesen Zusatzfehlern aktiv.
Der Token benötigt passende Leserechte für Historien und Ticketstatus. Eine
Browser-Session wird nicht übernommen; Cookies werden nicht benötigt oder gespeichert.

Zur Abnahme ein Ticket durch Benutzer A mehrfach ändern, durch B einmal ändern,
schließen, wieder öffnen und erneut schließen. Beide Personen müssen je ein
bearbeitetes Ticket erhalten; der Schließende je ein geschlossenes. Eine reine
Regel-/Mail-Parser-Aktion darf keinem Benutzer zugerechnet werden.

## Ereignis bei neuen Prio-1-Vorgängen

Auf **Zentrale Konfiguration** gibt es zusätzlich:

- **Neuer Prio 1 Vorgang** (`sensor`): Vorgangsnummer des zuletzt gemeldeten
  Prio-1-Vorgangs. Vor dem ersten Ereignis ist der Zustand unbekannt. Der letzte
  Wert wird lokal gespeichert und nach einem Neustart oder Neuladen wiederhergestellt.
- **Prio 1 Vorgangsereignis** (`event`): Zeitpunkt der letzten Erkennung;
  Attribute enthalten `event_type`, `ticket_id`, `ticket_number`, `device_id`
  und `config_entry_id`. Der Ereignistyp lautet `priority_one_ticket`.

Zusätzlich wird auf dem Home-Assistant-Ereignisbus für jeden Treffer
`docbee_priority_one_ticket` mit `ticket_id`, `ticket_number`, `device_id`
und `config_entry_id` ausgelöst. `device_id` bezeichnet das zentrale Gerät.
Die Vorgangsnummer ist die DocBee-Nummer (`ticketNumber`), nicht die interne ID.

### Wann wird ausgelöst?

Ein Ereignis entsteht, wenn ein Vorgang gegenüber dem vorherigen erfolgreichen
Abruf neu zur Menge der Vorgänge mit Prioritätswert **100** gehört: durch
Neuanlage oder durch eine nachträgliche Prioritätsänderung. Ein beobachteter
Wechsel weg von Prio 1 und anschließend zurück löst erneut aus. Ein unverändert
als Prio 1 geführter Vorgang wird nicht wiederholt gemeldet.

Für diese Erkennung werden auch abgeschlossene Vorgänge berücksichtigt. Anders
als die Ticketzähler prüft sie Prioritätsänderungen unabhängig vom Status;
Schließen und Wiederöffnen allein lösen daher kein Ereignis aus. Die API wird
zusätzlich mit `priorityIds` für alle Prioritäten mit Wert 100 und den Feldern
`id,ticketNumber` abgefragt, einschließlich Seitennavigation.

Bei mehreren Treffern werden einzelne Ereignisse in stabiler ID-Reihenfolge
abgegeben. Die Textentität wird jeweils aktualisiert und behält die zuletzt
verarbeitete Nummer. Die tatsächliche zeitliche Reihenfolge mehrerer Änderungen
zwischen zwei Abrufen kann die Integration nicht rekonstruieren. Für
Benachrichtigungen deshalb die Nummer aus den **Ereignisdaten** verwenden, nicht
nachträglich den Textsensor auslesen.

### Start, Ausfälle und Grenzen

- Der erste gültige Abruf nach Einrichtung, Neustart oder Neuladen bildet nur
  den Ausgangsbestand. Vorhandene Prio-1-Vorgänge lösen keine Ereignisflut aus.
  Während Home Assistant ausgeschaltet war entstandene Ereignisse werden nicht
  rückwirkend nachgeliefert. Die zuletzt gemeldete Nummer bleibt gespeichert.
- Bei fehlgeschlagenen Abrufen oder ungültigen Prioritätsdaten wird kein
  Ereignis erzeugt und der letzte gültige Vergleichsbestand nicht geleert.
- Die Erkennung erfolgt beim regulären **Fünf-Minuten-Abruf**, nicht unmittelbar
  bei einer Änderung in DocBee. Wechsel auf Prio 1 und zurück zwischen zwei
  Abrufen können unentdeckt bleiben. Ein Webhook wäre für eine spätere sofortige
  Erkennung eine mögliche Erweiterung, ist aber nicht Bestandteil dieser Version.
- Maßgeblich bleiben die Sichtrechte des Tokens. Eine Änderung der Sichtrechte
  kann bereits bestehende Tickets erstmals sichtbar machen und damit als neu
  erkannte Prio-1-Vorgänge melden.
- Der zuletzt gemeldete Wert wird mit kurzer Verzögerung und beim regulären
  Entladen gespeichert. Bei einem abrupten Prozessabbruch unmittelbar nach dem
  Ereignis kann die letzte Speicherung fehlen.

### Beispielautomation

Dieses Beispiel erzeugt eine Meldung in Home Assistant für jedes Ereignis,
auch wenn mehrere Vorgänge beim selben Abruf erkannt werden:

```yaml
alias: Neuer DocBee Prio-1-Vorgang
triggers:
  - trigger: event
    event_type: docbee_priority_one_ticket
actions:
  - action: persistent_notification.create
    data:
      title: "DocBee: Prio 1"
      message: "Vorgang {{ trigger.event.data.ticket_number }} ist neu auf Prio 1."
mode: queued
max: 100
```

Bei mehreren DocBee-Verbindungen unter dem Trigger zusätzlich `event_data`
mit der gewünschten `config_entry_id` oder der `device_id` des zentralen Geräts
angeben. Die Werte sind in den Attributen der Ereignisentität oder in den
Ereignisdaten unter den Entwicklerwerkzeugen sichtbar. Zum Testen dort auf
`docbee_priority_one_ticket` lauschen, in DocBee einen Vorgang auf Prio 1 setzen
und den nächsten Abruf abwarten.

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

Die Integration verwendet gegenüber DocBee ausschließlich GET-Anfragen. Sie verändert weder
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
