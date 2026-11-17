# Offene Aufgaben

Stand 17.11.2026. Prioritäten: P1 = nächster fachlicher Schritt, P2 = Absicherung,
P3 = optionale Idee. Diese Liste ist keine Aufforderung, ohne neuen Arbeitsauftrag
Produktivsysteme zu ändern oder sämtliche Ideen umzusetzen.

## P1 – Benutzerbezogene Tageszähler (Nutzerauftrag, noch offen)

- [ ] **Geschlossene Tickets heute pro Benutzer:** dokumentierten Endpunkt
  `/restApi/v1/ticket/{id}/statusChange` auswerten. `user` ist ausführender Benutzer,
  `date` Zeitpunkt, Zielstatus über `ticketStatus.behaviour == CLOSED` bestimmen.
  Pagination, Quellen/automatische Aktionen und Zeitzone beachten. Keine Gleichsetzung
  mit `owner`. Tickets pro Person deduplizieren; wiederholte Schließungen und
  Wiederöffnung in Tests abdecken. Effiziente Kandidatenabfrage prüfen: allein
  heutiger *letzter* Schließungszeitpunkt könnte bestimmte Historienfälle auslassen.
- [ ] **Bearbeitete Tickets heute pro Benutzer:** Audit-Zugriff zuerst klären.
  Aktueller Blocker: Fetch/XHR-Pfad der allgemeinen Änderungskontrolle fehlt.
  Falls geliefert, Schema, Pagination, Authentifizierung, Benutzer-/Objekt-ID und
  Datumsfilter prüfen. Keine Session-Cookies in Integration oder Repository übernehmen.
  Ohne unterstützten Zugang Funktion als blockiert melden, nicht heimlich nur
  Verantwortliche oder Statusänderungen zählen.
- [ ] Beide Benutzerzähler nach belegtem Datenvertrag implementieren, testen und
  Handbuch/Version aktualisieren. Schließungszähler ist unabhängig vom Audit-Blocker
  untersuchbar; die beiden Aufgaben nicht fälschlich als vollständig blockiert behandeln.

## P2 – Verifikation und Reproduzierbarkeit

- [ ] Live-Abnahme durch Nutzer: Werte mit DocBee vergleichen (Benutzer, Queue,
  zentral, Rolle/Aktiv, Tagesgrenzen und Ereignis). Keine Tokens im Chat verlangen.
- [ ] Falls Prio-1-Sensor weiter unverfügbar: anonymisierten Datentyp/Schema prüfen;
  bisheriger Screenshot erklärt nicht den tatsächlichen Rohwert.
- [ ] Windows-PC B anhand `WINDOWS_SETUP.md` einrichten, 86 Tests ausführen,
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
