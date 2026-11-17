# Projektstatus – Your Docbee Connect

> Kompakte Einstiegsübersicht. Detaillierter Status: [docs/STATUS.md](docs/STATUS.md), offene Aufgaben: [docs/TODO.md](docs/TODO.md), Übergabe: [docs/HANDOVER.md](docs/HANDOVER.md).

## Stand
- Integration: `docbee`, Anzeigename **Your Docbee Connect**.
- Laut vorhandener Dokumentation: Version **0.5.5**.
- Dokumentiert implementiert: Einrichtung, zentrale/Benutzer-/Queue-Geräte, Ticket- und Tageszähler, Prio-1-Ereignisse, HACS.
- Bestandsdokumentation nennt **133 erfolgreiche Tests** mit Python 3.13 und HA Core 2025.6.3. Diese Zahl wurde bei dieser Dokumentationsmigration **nicht neu getestet**.

## Offene Prüfungen und Risiken
- Authentifizierte DocBee-Live-Abnahme steht aus, besonders History-Endpunkt und benutzerbezogene Tageszähler.
- Neuere Home-Assistant-Versionen und Windows-Testausführung nicht separat bestätigt.
- Die beiden neu angelegten Handbücher sind aus vorhandenen Projektunterlagen abgeleitet; praktische Abnahme steht aus.

## Dokumentationsmigration
- 2026-11-17: Bestehende `AGENTS.md` um gemeinsame Entwicklungsregeln ergänzt; `REQUIREMENTS.md`, diese Übersicht und getrennte Handbücher eingeführt.
- Laufzeitcode und Integrationsversion bleiben unverändert.
- Keine Tests im Rahmen dieser reinen Dokumentationsmigration ausgeführt.
- Ausführliches `docs/HANDBUCH.md` und bestehende Status-/Entscheidungsdateien bleiben erhalten.

## Nächster Schritt
Bei jeder weiteren Entwicklung Anforderungen, diese Übersicht, detaillierten Projektstatus sowie beide Handbücher synchron aktualisieren. Live-Abnahme der offenen API-Funktionen durchführen, sobald eine geeignete Testumgebung verfügbar ist.
