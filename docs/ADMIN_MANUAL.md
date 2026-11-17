# Administrationshandbuch – Your Docbee Connect

> Betriebsorientierte Ergänzung zum bestehenden [Handbuch](HANDBUCH.md), zur [Architektur](ARCHITECTURE.md) und zum [Projektstatus](STATUS.md).

## Architektur
Home-Assistant-Custom-Integration mit Domain `docbee`, Anzeigename **Your Docbee Connect**. Lesender HTTPS-Zugriff auf DocBee über Bearer-Token, Home-Assistant-aiohttp-Session und regelmäßiges Polling (fünf Minuten). Keine eigenständige Web-App und keine DocBee-Schreiboperationen.

## Installation
- **HACS:** GitHub-Repository als benutzerdefinierte Integration hinzufügen, installieren und Home Assistant neu starten.
- **Manuell:** `custom_components/docbee` nach `/config/custom_components/docbee` kopieren; `manifest.json` muss direkt im Ordner liegen. Danach Home Assistant neu starten.
- Integration über **Einstellungen → Geräte & Dienste** konfigurieren. YAML-Konfiguration ist nicht erforderlich.

## Konfiguration und Berechtigungen
- DocBee-HTTPS-URL und Access Token mit Leseberechtigungen für relevante API-Ressourcen.
- Token wird in Home Assistants Konfiguration verwaltet; Konfigurationsdateien und Backups schützen.
- TLS-Zertifikatsprüfung nicht deaktivieren. Keine Tokens in Logs, Issues oder Screenshots veröffentlichen.
- Prio-1-Prioritäten über Integrationsoptionen festlegen; die Auswahl ist instanzbezogen.

## Betrieb und Monitoring
- Reguläres Polling alle fünf Minuten, Tagesgrenzen gemäß Home-Assistant-Zeitzone.
- API-/Schemafehler können Sensoren als nicht verfügbar kennzeichnen; keine künstlichen Nullwerte annehmen.
- Home-Assistant-Protokolle und Integrationsdiagnosen bei Problemen prüfen, vertrauliche Inhalte vor Weitergabe anonymisieren.
- Geräte- und Entitätsidentitäten bei Updates erhalten; native Untergruppen nicht durch manuelle Migration ersetzen.

## Update und Rollback
- Vor Änderungen Home-Assistant-Backup erstellen und eine bekannte funktionierende Integrationsversion festhalten.
- Über HACS aktualisieren oder den Integrationsordner kontrolliert ersetzen; danach Home Assistant neu starten.
- Bei Problemen vorherige Version wiederherstellen und Logs prüfen. Diese Schritte wurden bei der Dokumentationsmigration nicht live ausgeführt.

## Teststatus und Einschränkungen
- Vorhandener Projektstatus berichtet 133 bestandene Tests mit Python 3.13 und HA Core 2025.6.3.
- Die Tests verwenden simulierte DocBee-Antworten, keine authentifizierte Live-Instanz.
- Insbesondere der nicht öffentlich dokumentierte History-Endpunkt und benutzerbezogene Tageszähler benötigen eine Live-Abnahme.
- Keine zugesicherte Kompatibilität mit neueren Home-Assistant-Versionen.

## Weiterführende Dokumente
[Handbuch](HANDBUCH.md) · [Architektur](ARCHITECTURE.md) · [Entscheidungen](DECISIONS.md) · [Status](STATUS.md) · [Offene Aufgaben](TODO.md)
