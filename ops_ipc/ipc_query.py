import time
import requests
from auth import get_access_token

def query_ipc(ipc_code: str):
    token = get_access_token()
    query = f"IC={ipc_code}"

    print(f"\n🔎 Sende Anfrage für IPC: {query}")

    url = "https://ops.epo.org/3.2/rest-services/published-data/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    params = {"q": query}

    start_time = time.time()
    response = requests.get(url, headers=headers, params=params)
    end_time = time.time()
    response_time = round(end_time - start_time, 2)

    # Trefferanzahl: Header oder Fallback auf JSON
    total = response.headers.get("X-Total-Results")
    if not total:
        try:
            total = response.json()["ops:world-patent-data"]["ops:biblio-search"]["@total-result-count"]
        except Exception:
            total = "unbekannt"

    print(f"\n Trefferanzahl: {total}")
    print(f" Antwortzeit: {response_time} Sekunden")

    try:
        data = response.json()
        entries = data["ops:world-patent-data"]["ops:biblio-search"]["ops:search-result"]["ops:publication-reference"]

        # Falls nur ein Element (Dict) vorliegt, in Liste umwandeln
        if isinstance(entries, dict):
            entries = [entries]

        print("\n Erste Treffer:")
        for entry in entries[:10]:  # Zeige die ersten 10 Treffer
            doc_info = entry["document-id"]
            if isinstance(doc_info, dict):  # Einzeltreffer
                doc_info = [doc_info]
            for doc in doc_info:
                if doc["@document-id-type"] == "docdb":
                    country = doc["country"]["$"]
                    number = doc["doc-number"]["$"]
                    kind = doc["kind"]["$"]
                    print(f" • {country}{number} ({kind})")
                    break

    except Exception as e:
        print(f"\n Fehler beim Auslesen der Ergebnisse: {e}")

if __name__ == "__main__":
    ipc_code = input("\nBitte gib einen IPC-Code ein (z. B. A61K*): ")
    query_ipc(ipc_code)
