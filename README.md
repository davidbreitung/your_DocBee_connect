# DocBee für Home Assistant

Custom Integration mit UI-Einrichtung per Access Token, einem virtuellen Gerät
„Zentrale Konfiguration“ und einem Gerät samt Benutzername-Sensor je DocBee-Benutzer.

**Entwicklungsstand:** Implementiert anhand der DocBee-OpenAPI-Spezifikation
2026.2.0 und mit Home Assistant Core 2025.6.3 getestet. Ein Live-Test mit einer
authentifizierten DocBee-Instanz steht noch aus.

- [Handbuch: Installation, Einrichtung, Funktionen und Fehlerbehebung](docs/HANDBUCH.md)
- [PowerShell-Diagnose mit anonymisierter Ausgabe](scripts/Get-DocBeeApiSample.ps1)

Entwicklung (Python 3.13):

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```
