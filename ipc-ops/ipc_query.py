import time
from typing import Dict, List, Optional, Union, Any
import requests
from auth import get_access_token


class IPCQueryResult:
    """Represents the result of an IPC query."""
    
    def __init__(self, total_results: str, response_time: float, patents: List[Dict[str, str]]):
        self.total_results = total_results
        self.response_time = response_time
        self.patents = patents
    
    def display_summary(self) -> None:
        """Display query summary information."""
        print(f"\n Trefferanzahl: {self.total_results}")
        print(f" Antwortzeit: {self.response_time} Sekunden")
    
    def display_patents(self, limit: int = 10) -> None:
        """Display patent results with optional limit."""
        if not self.patents:
            print("\n Keine Patente gefunden.")
            return
            
        print("\n Erste Treffer:")
        for patent in self.patents[:limit]:
            print(f" • {patent['country']}{patent['number']} ({patent['kind']})")


class IPCQuery:
    """Handles IPC (International Patent Classification) queries to EPO OPS API."""
    
    BASE_URL = "https://ops.epo.org/3.2/rest-services/published-data/search"
    
    def __init__(self):
        self.token = get_access_token()
    
    def search(self, ipc_subclass: str, verbose: bool = True) -> IPCQueryResult:
        """Search for patents by IPC subclass.
        
        Args:
            ipc_subclass: The IPC subclass to search for (e.g., 'A61K', 'B66B')
            verbose: Whether to print progress messages
            
        Returns:
            IPCQueryResult containing search results
        """
        # Validate and clean IPC subclass format
        cleaned_ipc_subclass = self._validate_ipc_code(ipc_subclass)
        
        # EPO OPS uses 'ic' (lowercase) for IPC classification
        query = f"ic={cleaned_ipc_subclass}"
        
        if verbose:
            print(f"\n🔎 Sende Anfrage für IPC: {query}")
        
        response = self._make_request(query)
        response_time = getattr(response, 'response_time', 0.0)
        
        total_results = self._extract_total_results(response)
        patents = self._extract_patents(response)
        
        return IPCQueryResult(total_results, response_time, patents)
    
    def _validate_ipc_code(self, ipc_code: str) -> str:
        """Validate IPC subclass format - only subclasses allowed (4 characters: A61K, B66B, etc.)"""
        import re
        
        # Remove any wildcards
        clean_code = ipc_code.rstrip('*')
        
        # IPC subclass format: Letter + 2 digits + Letter (exactly 4 characters)
        # Examples: A61K, B66B, H01L, G06F, etc.
        if not re.match(r'^[A-H]\d{2}[A-Z]$', clean_code):
            raise ValueError(f"Invalid IPC subclass format: {ipc_code}. Expected 4-character subclass like A61K, B66B, H01L, etc.")
        
        return clean_code
    
    def _make_request(self, query: str) -> requests.Response:
        """Make HTTP request to OPS API."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
        params = {"q": query}
        
        start_time = time.time()
        response = requests.get(self.BASE_URL, headers=headers, params=params)
        end_time = time.time()
        
        response.response_time = round(end_time - start_time, 2)
        
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 400:
                raise ValueError(f"Invalid IPC subclass or query format: {query}. Check IPC format (e.g., A61K, B66B)")
            elif response.status_code == 401:
                raise ValueError("Authentication failed. Check OPS credentials.")
            elif response.status_code == 403:
                raise ValueError("Access forbidden. Check API permissions.")
            else:
                raise ValueError(f"API request failed: {e}")
        
        return response
    
    def _extract_total_results(self, response: requests.Response) -> str:
        """Extract total result count from response."""
        total = response.headers.get("X-Total-Results")
        if total:
            return total
            
        try:
            data = response.json()
            return data["ops:world-patent-data"]["ops:biblio-search"]["@total-result-count"]
        except (KeyError, ValueError):
            return "unbekannt"
    
    def _extract_patents(self, response: requests.Response) -> List[Dict[str, str]]:
        """Extract patent information from response."""
        try:
            data = response.json()
            entries = data["ops:world-patent-data"]["ops:biblio-search"]["ops:search-result"]["ops:publication-reference"]
            
            if isinstance(entries, dict):
                entries = [entries]
            
            patents = []
            for entry in entries:
                patent_info = self._parse_patent_entry(entry)
                if patent_info:
                    patents.append(patent_info)
                    
            return patents
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"\n Fehler beim Auslesen der Ergebnisse: {e}")
            return []
    
    def _parse_patent_entry(self, entry: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Parse individual patent entry to extract key information."""
        try:
            doc_info = entry["document-id"]
            if isinstance(doc_info, dict):
                doc_info = [doc_info]
            
            for doc in doc_info:
                if doc.get("@document-id-type") == "docdb":
                    return {
                        "country": doc["country"]["$"],
                        "number": doc["doc-number"]["$"],
                        "kind": doc["kind"]["$"]
                    }
        except (KeyError, TypeError):
            pass
        
        return None


def query_ipc(ipc_subclass: str, verbose: bool = True) -> IPCQueryResult:
    """Convenience function to query IPC subclasses.
    
    Args:
        ipc_subclass: The IPC subclass to search for (e.g., 'A61K', 'B66B')
        verbose: Whether to display results
        
    Returns:
        IPCQueryResult object
    """
    ipc_query = IPCQuery()
    result = ipc_query.search(ipc_subclass, verbose)
    
    if verbose:
        result.display_summary()
        result.display_patents()
    
    return result


if __name__ == "__main__":
    ipc_subclass = input("\nBitte gib einen IPC-Subclass ein (z. B. A61K, B66B): ")
    query_ipc(ipc_subclass)