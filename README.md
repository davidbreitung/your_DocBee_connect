# Your Docbee Connect für Home Assistant

Custom Integration mit UI-Einrichtung per Access Token, einem virtuellen Gerät
„Zentrale Konfiguration“, Benutzergeräten mit Anzeigenamen und eigenen Queue-Geräten.
Sensoren zählen nicht abgeschlossene Vorgänge je Verantwortlichem und Queue sowie
insgesamt und mit Prioritätswert 100. Benutzername, Rolle und Aktiv-Status (Ja/Nein) sind eigene Entitäten.
Die Integrationsansicht trennt die Geräte in die Bereiche **Zentrale Konfiguration**,
**Benutzer** und **Queues**.
Neu erkannte Prio-1-Vorgänge lösen ein Home-Assistant-Ereignis aus; die letzte
Vorgangsnummer wird auf dem zentralen Gerät angezeigt. Die Erkennung erfolgt
beim Fünf-Minuten-Abruf, mit Ausgangsbestand ohne Auslösung nach einem Neustart.

**Entwicklungsstand:** Implementiert anhand der DocBee-OpenAPI-Spezifikation
2026.2.0 und mit Home Assistant Core 2025.6.3 getestet. Ein Live-Test mit einer
authentifizierten DocBee-Instanz steht noch aus.

- [Handbuch: Installation, Einrichtung, Funktionen und Fehlerbehebung](docs/HANDBUCH.md)
- [PowerShell-Diagnose mit anonymisierter Ausgabe](scripts/Get-DocBeeApiSample.ps1)

Installation über HACS / Marketplace: Dieses Repository über seinen GitHub-Link
hinzufügen (Kategorie **Integration**, falls abgefragt), **Your Docbee Connect** herunterladen
und Home Assistant neu starten. Anschließend unter **Einstellungen → Geräte &
Dienste → Integration hinzufügen → Your Docbee Connect** einrichten. Die vollständigen Schritte
stehen im Handbuch.

Entwicklung (Python 3.13):

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```
