# DocBee für Home Assistant – Handbuch

## Stand und Voraussetzungen

Version 0.1.0 implementiert die Einrichtung über die Oberfläche, Geräte,
Benutzername-Sensoren, regelmäßige Aktualisierung und Token-Erneuerung.
Automatisierte Tests laufen mit Home Assistant Core 2025.6.3 und Python 3.13.
Ältere Versionen werden nicht unterstützt; neuere Versionen wurden nicht separat getestet.

Die API-Anbindung folgt der öffentlich erreichbaren DocBee-OpenAPI-Spezifikation
2026.2.0. **Ein Live-Test mit einer authentifizierten DocBee-Instanz steht noch aus.**
Die Tests prüfen die dokumentierte Struktur mit simulierten API-Antworten.

Benötigt werden eine per HTTPS erreichbare DocBee-Instanz mit gültigem
TLS-Zertifikat und ein Access Token mit Leseberechtigung für alle gewünschten
Benutzer. Home Assistant muss den Host der Instanz erreichen können.
Die Integration kann nur Benutzer sehen, auf die der Token Zugriff hat.

## Installation

1. Den Ordner `custom_components/docbee` aus diesem Repository nach
   `<Home-Assistant-Konfigurationsverzeichnis>/custom_components/docbee`
   kopieren. `manifest.json` muss direkt in diesem Zielordner liegen.
2. Home Assistant neu starten.
3. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** nach
   **DocBee** suchen. Falls sie nicht erscheint, den Browser neu laden und
   die Home-Assistant-Protokolle prüfen.

Es ist keine YAML-Konfiguration nötig. Eine HACS-Installation ist derzeit
nicht eingerichtet. Bei Updates den Integrationsordner durch die neue Version
ersetzen und Home Assistant neu starten.

## Verbindung bei der Ersteinrichtung

1. In DocBee einen Access Token erzeugen. Laut öffentlicher Dokumentation
   befindet sich diese Funktion beim Benutzericon unter
   **Einstellungen → Access Token**. Die Oberfläche kann versionsabhängig abweichen.
2. Im DocBee-Einrichtungsdialog von Home Assistant die HTTPS-URL der Instanz
   eingeben, zum Beispiel `https://firma.example`. Ein abschließendes `/restApi`
   wird automatisch entfernt. Installationen unter einem URL-Unterpfad sind möglich.
3. Den Access Token in das verdeckte Feld eintragen und absenden.
4. Die Integration prüft vor dem Speichern den Benutzerabruf einschließlich
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
| Zentrale Konfiguration | Zentrale Konfiguration | Zentrale Konfiguration | Zunächst keine; werden später festgelegt |
| Benutzer | Benutzername aus DocBee | Benutzer | Sensor „Benutzername“ mit dem Benutzernamen als Zustand |

Das zentrale Gerät wird ausdrücklich registriert, obwohl es keine Entitäten
besitzt. Jeder Benutzer erhält ein eigenes virtuelles Gerät. Identitäten
basieren auf Konfiguration und Benutzer-ID. Gleichnamige Benutzer bleiben
getrennt; eine Umbenennung aktualisiert Zustand und Gerätenamen ohne neue
Entität. Ein manuell vergebener Gerätename in Home Assistant bleibt erhalten.
Home Assistant erzeugt die tatsächlichen `sensor.*`-Entitäts-IDs; es gibt
keine fest vorgegebenen IDs. Sie können in der Entitätsverwaltung angepasst werden.

### Gruppierung in Home Assistant

Home Assistant bietet keine frei definierbare Geräteklasse „Benutzer“ und
keine von dieser Integration vorgegebene verschachtelte Geräteansicht.
„Benutzer“ wird daher als **Gerätemodell** ausgewiesen, „Zentrale Konfiguration“
als separates Gerät. In der Geräteübersicht können die Geräte nach Integration
und Modell gefiltert werden. Eine eigene visuelle Dashboard-Gruppe kann der
Benutzer manuell mit den gewünschten Entitäten anlegen; die Integration legt
keine Dashboard-Karten oder Home-Assistant-Gruppenhelfer an.

## Aktualisierung und Lebenszyklus

- Alle fünf Minuten wird ein vollständiger Benutzer-Snapshot abgefragt.
- Neue Benutzer erzeugen automatisch Geräte und Sensoren.
- Umbenennungen aktualisieren den Sensorzustand und den standardmäßigen Gerätenamen.
- Nicht mehr gelieferte Benutzer bleiben registriert, ihr Sensor wird
  `unavailable`. So gehen individuelle Namen und Historie nicht verloren.
  Bei erneutem Auftreten derselben ID wird die Entität wieder verfügbar.
- Bei Verbindungsfehlern werden Sensoren als nicht verfügbar markiert.
  Ein fehlgeschlagener Teilabruf ersetzt nicht den letzten vollständigen Snapshot.
- Ohne Benutzer bleibt das zentrale Gerät erhalten.
- Neuladen der Integration startet den Abruf erneut. Entfernen der Integration
  entfernt ihre Zuordnung in Home Assistant; in DocBee werden keine Daten geändert.

Die Integration verwendet nur GET-Anfragen für Benutzer. Ticketaktionen,
Schreibzugriffe und zusätzliche zentrale Entitäten sind nicht implementiert.

## Token erneuern und Fehler beheben

| Meldung/Zustand | Bedeutung und Maßnahme |
| --- | --- |
| Ungültige Eingabe | HTTPS-Instanz-URL ohne eingebettete Zugangsdaten, Query oder Fragment sowie nicht leeren Token eingeben. |
| Authentifizierung fehlgeschlagen | HTTP 401/403: Token, Ablaufdatum und Benutzer-Leseberechtigung prüfen. |
| Nicht erreichbar | Netzwerk, DNS, URL, TLS-Zertifikat oder HTTP-Fehler prüfen. Auch Weiterleitungen werden abgelehnt; die direkte Instanz-URL verwenden. |
| Unerwartete Antwort | JSON-Struktur, `id`/`username` und Pagination weichen vom implementierten Vertrag ab. Anonymisierte Probe bereitstellen, siehe unten. |
| Sensor nicht verfügbar | Abruf fehlgeschlagen oder Benutzer nicht mehr im API-Ergebnis. Integrationsstatus und Berechtigungen prüfen. |

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
`GET /restApi/v1/user?fields=id,username&limit=50&offset=N&sortings=id%20asc`.
Ein Token kann direkt in DocBee erzeugt werden; ein Login-Aufruf ist dann unnötig.
Die Antwort folgt dem dokumentierten Schema `UserList`, zum Beispiel:

```json
{
  "user": [{"id": 1, "username": "beispiel"}],
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

Die 38 Tests prüfen API-Fehler und dokumentierte Seitennavigation, URL-Prüfung,
Identitäten sowie Einrichtung, Duplikate, erneute Authentifizierung, echte
Home-Assistant-Geräte-/Entitätsregistrierung, Benutzeränderungen, Ausfälle und
Entladen der Integration. DocBee-Antworten werden simuliert. Die Tests
ersetzen daher keinen Live-Test mit einer authentifizierten DocBee-Instanz.
