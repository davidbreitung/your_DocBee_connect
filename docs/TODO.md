# Offene Aufgaben

Stand 17.11.2026. Prioritäten: P1 = nächster fachlicher Schritt, P2 = Absicherung,
P3 = optionale Idee. Diese Liste ist keine Aufforderung, ohne neuen Arbeitsauftrag
Produktivsysteme zu ändern oder sämtliche Ideen umzusetzen.

## P1 – Benutzerbezogene Tageszähler: Live-Abnahme

- [x] History-Pfad und Beispielstruktur erhalten. `actor.id`/Einzeldatum verwenden,
  INSERT/UPDATE interner Benutzer zählen; Automatisierung/Mail-Parser ausschließen.
- [x] Benutzer-Schließungszähler über dokumentierte Statushistorie implementieren;
  CLOSED-Zielstatus und Quelle USER, Ticket/Benutzer deduplizieren, Wiederöffnung
  und Mehrfachschließung berücksichtigen.
- [x] Anzeigen, Tests, Handbuch und Kontext aktualisieren (Version 0.4.0).
- [ ] **Live prüfen:** Akzeptiert `/ticket/{id}/history` den vorhandenen Bearer-Token?
  Welche Berechtigung ist nötig? Kein Token/Cookie im Chat erforderlich.
- [ ] Vollständigkeit der History-Antwort bei langen Historien prüfen. Bisheriges
  Beispiel ist ein Gruppenarray ohne Pagination-Metadaten; keine unbekannten
  Paging-Parameter erfinden. Abweichende Schemas anonymisiert untersuchen.
- [ ] Vergleich mit DocBee: zwei Benutzer ändern dasselbe Ticket, wiederholte
  Änderungen, automatische Änderung, schließen/wieder öffnen/erneut schließen.
  Prüfen, dass `TICKET_MODIFIED` alle relevanten Vorgänge als Kandidaten liefert.
- [ ] Last/Antwortzeit bei vielen heute geänderten Tickets messen. Maximal vier
  parallele Ticketprüfungen; Statushistorien paginiert, keine unbestätigte Cache-Lösung.

## P2 – Verifikation und Reproduzierbarkeit

- [ ] Live-Abnahme durch Nutzer: Werte mit DocBee vergleichen (Benutzer, Queue,
  zentral, Rolle/Aktiv, Tagesgrenzen und Ereignis). Keine Tokens im Chat verlangen.
- [x] Fehlendes Zahlenfeld bestätigt; explizite Prioritätsauswahl in 0.5.0 umgesetzt.
- [ ] 0.5.0 live prüfen: Priorität über Konfigurieren wählen, Zähler und Ereignis
  bei neuer Prioritätszuordnung prüfen; Speichern darf keine Altalarme auslösen.
- [ ] Windows-PC B anhand `WINDOWS_SETUP.md` einrichten, 125 Tests ausführen,
  Git-Roundtrip A → B → A bestätigen. Anleitung bislang nur auf Linux-Basis vorbereitet.
- [ ] Prüfen, ob aktuelle Desktop-App-Version Cloud-/Remote-Chats offiziell
  geräteübergreifend fortsetzen kann. Installierte Version und Kontokonfiguration
  fehlen; keine Zusage zur lokalen Verlaufssynchronisierung machen.
- [ ] Bei gesondertem Auftrag transitive Dependencies reproduzierbar sperren und
  CI auf Linux ergänzen. Keine unbegründete Aktualisierung der HA-Testbasis.
- [ ] Bei Weiterentwicklung Fehlerisolation für Zusatzabfragen überprüfen, damit
  einzelne neue Datenfelder nicht wieder den gesamten Start unnötig blockieren.

## P3 – Ideen, nicht als beauftragt behandeln

- [ ] DocBee-Webhooks für zeitnahe Prio-1-Ereignisse untersuchen.
- [ ] Konfigurierbares Polling / „Jetzt aktualisieren“-Button.
- [ ] Eigenes Integrationsicon/Brands-Unterstützung.
- [ ] Leistungsprüfung bei vielen (auch geschlossenen) Prio-1-Tickets.

## Nicht wieder einplanen ohne neue Nutzerentscheidung

- „Vorgänge in Bearbeitung“: Status existiert beim Nutzer nicht.
- „Offene Tagesabschlüsse“: explizit vorerst verworfen.
- Vollständige Codex-Rohverläufe oder Auth-Dateien per Git/OneDrive kopieren.

## Aktueller Blocker: HTTP 400

- [ ] Nach 0.5.1 den konkreten fehlgeschlagenen Abruf anhand des neuen
  Meldungstexts identifizieren. Auswahl bleibt laut Nutzer gespeichert.
- [x] Prio-Ereignisabruf isolieren, keine Teilmengen als Ereignisbasis verwenden;
  HTTP-Diagnose ohne IDs, Parameterwerte, Tokens und Antwortinhalte ergänzen.
- [ ] Eigentliche serverseitige Ablehnungsursache mit anonymisierten Angaben
  prüfen; keine geratenen Filter oder Wechsel auf numerische Priorität.

### Aktualisierung 0.5.2

- [x] Screenshot identifiziert Tagesabfrage als Setup-Blocker; Fehler pro zentralem
  Tageszähler isoliert und None als unavailable dargestellt.
- [ ] `scripts/diagnose-daily-counts.ps1` auf Windows ausführen und anonymisierte
  Ergebnisse prüfen. Format/Scope-/Sortierungsursache bislang unbestätigt.

### Aktualisierung 0.5.3

- [x] Diagnose vom Nutzer erhalten: nur modified-offset liefert 400, alle
  Z-Varianten und Basisabfrage 200. Datumsformat als Ursache eingegrenzt.
- [x] Zentrale und benutzerbezogene Tagesabfragen auf UTC-Millisekunden mit Z
  umgestellt; Tests für Tagesgrenzen/Zeitumstellung/Mikrosekunden aktualisiert.
- [ ] 0.5.3 live prüfen: zentrale Tageszähler und Benutzer-History-Zähler.
  Die genaue Bedeutung und Berechtigung der History bleibt separat zu prüfen.

### Aktuell 0.5.4 – allgemeine Änderungshistorie

- [x] Nutzer bestätigt Betrieb nach Datumsfix, Schließungszähler liefert Werte.
- [x] Konkreter Fehler ist HistoryFormatError; Diagnose um Grund/Pfad/Typ erweitert.
- [ ] Neue Warnung nach Update erheben und betroffene Struktur anonymisiert prüfen.
  Keine unbestätigte Vererbung von Parent-Datum/Actor und kein stilles Überspringen.
