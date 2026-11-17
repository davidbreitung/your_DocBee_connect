# Your Docbee Connect für Home Assistant

Custom Integration mit UI-Einrichtung per Access Token, einem virtuellen Gerät
„Zentrale Konfiguration“, Benutzergeräten mit Anzeigenamen und eigenen Queue-Geräten.
Sensoren zählen nicht abgeschlossene Vorgänge je Verantwortlichem und Queue sowie
insgesamt und mit konfigurierbarer Prio-1-Auswahl (ohne Auswahl: Prioritätswert 100). Benutzername, Rolle und Aktiv-Status (Ja/Nein) sind eigene Entitäten.
Die Integrationsansicht trennt die Geräte in die Bereiche **Zentrale Konfiguration**,
**Benutzer** und **Queues**. Tageszähler zeigen heute bearbeitete, neu erstellte
und geschlossene Vorgänge anhand der Home-Assistant-Zeitzone. Pro Benutzer werden
heute bearbeitete und geschlossene Tickets anhand der ausführenden Person aus
Änderungs-/Statushistorien gezählt. Der nicht öffentlich dokumentierte
History-Endpunkt ist anhand einer bereitgestellten Antwort implementiert; eine
authentifizierte Live-Abnahme steht aus.
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

Projektkontext und Rechnerwechsel:

- [Codex-Projektanweisungen](AGENTS.md)
- [Übergabe / aktueller Arbeitskontext](docs/HANDOVER.md)
- [Status](docs/STATUS.md) und [offene Aufgaben](docs/TODO.md)
- [Architektur](docs/ARCHITECTURE.md) und [Entscheidungen](docs/DECISIONS.md)
- [Windows-Einrichtung und Synchronisierung über GitHub](docs/WINDOWS_SETUP.md)

Entwicklung (Python 3.13):

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

## Projektstandard und getrennte Handbücher

- [Anforderungen](REQUIREMENTS.md) und [kompakter Projektstatus](STATUS.md)
- [Benutzerhandbuch](docs/USER_MANUAL.md) – Bedienung und Anwenderhinweise
- [Administrationshandbuch](docs/ADMIN_MANUAL.md) – Installation, Betrieb und Fehlerbehebung

Das bisherige [ausführliche Handbuch](docs/HANDBUCH.md) und die projektspezifischen Codex-Anweisungen bleiben erhalten. Die Handbücher und der Projektstatus werden bei relevanten Codeänderungen mitgepflegt.
