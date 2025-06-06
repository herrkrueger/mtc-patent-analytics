# mtc-ipcwise

# Funktionen: 
- Authentifizierung über OPS-API-Key und Secret (OAuth)
- Suchanfrage nach IPC-Klasse (z. B. `A61K*`)
- Ausgabe der Trefferanzahl (aus dem HTTP-Header)
- Anzeige der Antwortzeit in Sekunden
- Ausgabe der ersten 3 Dokumentnummern
- Eingabe des IPC-Codes direkt im Terminal

# Vorrausstezungen: 
- Python 3.10 oder höher
- Notweniges Paket: python -m pip install python-dotenv requests python-epo-ops-client
- Das OPS-API-Key und Secret holt man sich von der Seite: https://developers.epo.org/user/register 

# Ausführen: 
- run drücken
- Bitte gib einen IPC-Code ein (z. B. A61K*):

# Beispielausgabe: 
Authentifizierung erfolgreich
Sende Anfrage für IPC: IC=A61K*
Treffer insgesamt: 1234
Antwortzeit: 1.73 Sekunden

Erste Treffer (max. 10):
 • EP1234567
 • EP2345678
 • EP3356789
 • EP2345678
 • EP3451789
 • EP2345628
 • EP3456489
 • EP2345678
 • EP3450789
 • EP2349678
 

# Funktionalität: 
# authy.py
- Holt OPS_KEY und OPS_SECRET aus der .env-Datei.
- Fragt bei der EPO API ein Zugriffstoken an.
- Gibt den Token zurück oder zeigt Fehler bei ungültigen Zugangsdaten.

# ipc_query.py
- Sendet eine Suchanfrage mit dem IPC-Code an die EPO API.
- Gibt die Trefferanzahl und Antwortzeit aus.
- Zeigt (wenn möglich) die ersten 10 Patentnummern.

# info:
- Die EPO OPS API liefert maximal 10.000 Treffer pro Anfrage, um Serverlast zu begrenzen und Missbrauch zu vermeiden – auch wenn es in Wirklichkeit mehr Ergebnisse gäbe.
