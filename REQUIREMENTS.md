# Anforderungen – Your Docbee Connect

> Bestandsaufnahme auf Grundlage der vorhandenen Projektdokumentation vom 17.11.2026. Diese Datei ergänzt `docs/DECISIONS.md`, `docs/TODO.md` und `docs/ARCHITECTURE.md`; sie ersetzt sie nicht.

## Zweck und Rahmen
Home-Assistant-Custom-Integration `docbee` (Anzeigename **Your Docbee Connect**) zur lesenden Anzeige von DocBee-Daten über HTTPS/Bearer-Token. Keine Schreibaktionen nach DocBee.

## Bestehender Funktionsumfang
- [x] UI-Einrichtung mit URL, Access Token, Duplikatprüfung und Reauthentifizierung.
- [x] Geräte/Untergruppen für zentrale Konfiguration, Benutzer und Queues.
- [x] Offene Vorgänge, Prio-1-Zähler und Prio-1-Ereignisse; konfigurierbare Prioritäts-IDs, sonst Zahlenwert 100.
- [x] Benutzername, Rolle, Aktiv-Status und zugewiesene Vorgänge.
- [x] Zentrale Tageszähler und benutzerbezogene Tageszähler auf Grundlage von Historien.
- [x] Fünf-Minuten-Polling, Home-Assistant-Zeitzone und stabile Geräte-/Entitätsidentitäten.
- [x] HACS- und manuelle Installation.

## Akzeptanzkriterien
- [x] Automatisierte Tests mit simulierten DocBee-Antworten und Home Assistant Core wurden laut bisherigem Projektstatus ausgeführt.
- [ ] Authentifizierte Live-Abnahme der DocBee-Integration und der historischen Benutzer-Tageszähler.
- [ ] Kompatibilität mit neueren Home-Assistant-Versionen nachweisen.
- [ ] Benutzer- und Administrationshandbuch gegen eine echte Installation prüfen.

## Explizit nicht vorgesehen
Kein DocBee-Schreibzugriff, kein MFA-/Passwort-Login, keine nicht beauftragten Webhooks, keine verworfenen Sensoren „In Bearbeitung“ oder „Offene Tagesabschlüsse“.

## Änderungen und Entscheidungen
Detaillierte Entscheidungen stehen in `docs/DECISIONS.md`. Neue fachliche Anforderungen und geänderte Akzeptanzkriterien hier nachführen und mit `docs/TODO.md` abstimmen.
