"""
Priority claims normalization and extraction.
Implements corrected logic based on working EPO OPS JSON structure.
"""

from typing import List, Dict, Any, Optional
from ..load.data_models import PriorityClaim, EPOOPSResponse

class PriorityNormalizer:
    """
    Normalizes priority claims from EPO OPS responses.
    Uses correct JSON structure: priority-claims → priority-claim entries.
    """
    
    def extract_priority_claims(self, ops_response: EPOOPSResponse) -> List[PriorityClaim]:
        """
        Extract and normalize priority claims from EPO OPS response.
        
        Strategy:
        1. Look for German (DE) priorities first
        2. If no German priority, use the first available priority-claim
        
        Args:
            ops_response: EPO OPS API response
            
        Returns:
            List of normalized PriorityClaim objects
        """
        if not ops_response.response_data or ops_response.status_code != 200:
            return []
        
        try:
            priorities = []
            
            # Navigate to correct JSON structure
            priority_claims_data = self._find_priority_claims_section(ops_response.response_data)
            
            if not priority_claims_data:
                return []
            
            # Extract all priority claims
            all_priorities = []
            german_priorities = []
            
            for priority_claim in priority_claims_data:
                if isinstance(priority_claim, dict):
                    doc_ids = priority_claim.get('document-id', [])
                    if not isinstance(doc_ids, list):
                        doc_ids = [doc_ids]
                    
                    for doc_id in doc_ids:
                        if isinstance(doc_id, dict):
                            priority = self._extract_priority_from_doc_id(doc_id)
                            if priority:
                                all_priorities.append(priority)
                                
                                # Check if it's a German priority
                                if priority.country == 'DE':
                                    german_priorities.append(priority)
            
            # Use German priorities if available, otherwise use first priority
            if german_priorities:
                priorities.extend(german_priorities)
            elif all_priorities:
                priorities.append(all_priorities[0])  # Use first available priority
            
            return priorities
            
        except Exception as e:
            print(f"⚠️ Error extracting priorities for {ops_response.ep_number}: {e}")
            return []
    
    def _find_priority_claims_section(self, ops_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find priority-claims section in EPO OPS response.
        
        Args:
            ops_data: Full EPO OPS response data
            
        Returns:
            List of priority-claim entries
        """
        try:
            # Navigate through the JSON structure
            world_patent_data = ops_data.get('world-patent-data', {})
            if not isinstance(world_patent_data, dict):
                return []
            
            exchange_documents = world_patent_data.get('exchange-documents', {})
            if not isinstance(exchange_documents, dict):
                return []
            
            exchange_document = exchange_documents.get('exchange-document', {})
            if not isinstance(exchange_document, dict):
                return []
            
            biblio = exchange_document.get('bibliographic-data', {})
            if not isinstance(biblio, dict):
                return []
            
            # Extract priority-claims section
            priority_claims_section = biblio.get('priority-claims', {})
            if not isinstance(priority_claims_section, dict):
                return []
            
            priority_claims = priority_claims_section.get('priority-claim', [])
            if not isinstance(priority_claims, list):
                priority_claims = [priority_claims]
            
            return priority_claims
            
        except Exception:
            return []
    
    def _extract_priority_from_doc_id(self, doc_id: Dict[str, Any]) -> Optional[PriorityClaim]:
        """
        Extract priority information from a document-id entry.
        
        Args:
            doc_id: document-id entry from priority-claim
            
        Returns:
            PriorityClaim object or None
        """
        try:
            country = doc_id.get('country', {}).get('$', '')
            number = doc_id.get('doc-number', {}).get('$', '')
            date = doc_id.get('date', {}).get('$', '')
            
            if not all([country, number, date]):
                return None
            
            # Format the priority claim
            formatted = self._format_priority_claim(country, number, date)
            
            return PriorityClaim(
                country=country,
                number=number,
                date=date,
                formatted=formatted
            )
            
        except Exception:
            return None
    
    def _format_priority_claim(self, country: str, number: str, date: str) -> str:
        """
        Format priority claim in standardized format.
        
        Args:
            country: Country code (e.g., "DE")
            number: Document number 
            date: Date in YYYYMMDD format
            
        Returns:
            Formatted priority string (e.g., "DE102123456A·2021-03-15")
        """
        try:
            # Convert date from YYYYMMDD to YYYY-MM-DD
            if len(date) >= 8:
                formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
            else:
                formatted_date = date
            
            # Special handling for German applications
            if country == 'DE' and number.startswith('102') and len(number) == 12:
                return f"{country}{number}A·{formatted_date}"
            elif country == 'EP':
                return f"{number}W·{formatted_date}"
            else:
                return f"{country}{number}·{formatted_date}"
                
        except Exception:
            return f"{country}{number}·{date}"
    
    def analyze_priority_patterns(self, all_priorities: List[List[PriorityClaim]]) -> Dict[str, Any]:
        """
        Analyze priority filing patterns across multiple patents.
        
        Args:
            all_priorities: List of priority claims for each patent
            
        Returns:
            Dictionary with priority statistics
        """
        total_patents = len(all_priorities)
        patents_with_priorities = sum(1 for p in all_priorities if p)
        
        if total_patents == 0:
            return {}
        
        # Count by country
        country_counts = {}
        total_priorities = 0
        
        for patent_priorities in all_priorities:
            for priority in patent_priorities:
                country_counts[priority.country] = country_counts.get(priority.country, 0) + 1
                total_priorities += 1
        
        # Calculate statistics
        priority_rate = (patents_with_priorities / total_patents) * 100
        german_priorities = country_counts.get('DE', 0)
        german_rate = (german_priorities / total_priorities * 100) if total_priorities > 0 else 0
        
        return {
            'total_patents': total_patents,
            'patents_with_priorities': patents_with_priorities,
            'priority_rate': round(priority_rate, 1),
            'total_priority_claims': total_priorities,
            'german_priorities': german_priorities,
            'german_priority_rate': round(german_rate, 1),
            'countries': country_counts
        }