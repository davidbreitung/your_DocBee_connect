# Benutzerhandbuch – Your Docbee Connect

> Benutzerorientierter Einstieg. Die vollständigen Detailbeschreibungen und Einschränkungen stehen im bestehenden [Handbuch](HANDBUCH.md).

## Zweck
Die Home-Assistant-Integration zeigt lesend Informationen aus DocBee an: offene Vorgänge, Prio-1-Vorgänge, Tageszähler, Benutzer und Queues. Sie ändert keine Tickets in DocBee.

## Voraussetzungen
- Home Assistant mit installierter Integration **Your Docbee Connect**
- HTTPS-Adresse einer DocBee-Instanz und ein gültiger Access Token mit passenden Leserechten

## Einrichtung
1. Integration über HACS als benutzerdefiniertes Repository `https://github.com/davidbreitung/your_DocBee_connect` installieren oder `custom_components/docbee` manuell kopieren.
2. Home Assistant neu starten.
3. **Einstellungen → Geräte & Dienste → Integration hinzufügen → Your Docbee Connect** öffnen.
4. DocBee-HTTPS-Adresse und Access Token eingeben.
5. Bei Bedarf unter **Konfigurieren** die Prio-1-Prioritäten auswählen.

## Bedienung
- **Zentrale Konfiguration:** Gesamtzahl offener Vorgänge, Prio-1-Zähler, Ereignisse und zentrale Tageszähler.
- **Benutzer:** Benutzername, Rolle, Aktiv-Status, zugewiesene Vorgänge sowie Tageszähler.
- **Queues:** Anzahl aktuell nicht abgeschlossener Tickets je Queue.
- Die Werte werden regulär alle fünf Minuten aktualisiert. Ereignisse zwischen Abrufen können unbemerkt bleiben.
- Bei der Prio-1-Auswahl gelten ausgewählte Prioritäts-IDs; ohne Auswahl wird der numerische Prioritätswert 100 verwendet.

## Hinweise und Fehlerbehebung
- Angezeigte Zahlen hängen von den Berechtigungen des DocBee-Tokens ab.
- Nicht verfügbare Sensoren können auf API-, Berechtigungs- oder Datenprobleme hinweisen; sie sind nicht mit dem Wert null gleichzusetzen.
- Benutzerbezogene Tageszähler sind implementiert, aber noch nicht mit einer authentifizierten DocBee-Instanz live abgenommen.
- Weitere Details: [Ausführliches Handbuch](HANDBUCH.md).

## Datenschutz
Keine Tokens, Tickets mit personenbezogenen Inhalten oder Screenshots mit vertraulichen Informationen in öffentliche Issues einstellen.
