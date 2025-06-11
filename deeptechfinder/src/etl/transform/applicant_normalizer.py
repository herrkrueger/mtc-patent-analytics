"""
Applicant normalization and categorization.
"""

from typing import List, Dict, Any
from ..load.data_models import Applicant, EPOOPSResponse

class ApplicantNormalizer:
    """
    Normalizes and categorizes applicants from EPO OPS responses.
    """
    
    def __init__(self):
        self.university_terms = [
            'university', 'universität', 'technische', 'hochschule', 
            'college', 'institut', 'tu ', 'technische universität'
        ]
    
    def extract_applicants(self, ops_response: EPOOPSResponse) -> List[Applicant]:
        """
        Extract and normalize applicants from EPO OPS response.
        
        Args:
            ops_response: EPO OPS API response
            
        Returns:
            List of normalized Applicant objects
        """
        if not ops_response.response_data or ops_response.status_code != 200:
            return []
        
        try:
            applicants = []
            
            # Find applicant data using recursive search
            applicant_data = self._find_recursive(ops_response.response_data, ['applicant'])
            
            seen_names = set()
            
            for app_section in applicant_data:
                if isinstance(app_section, list):
                    for applicant in app_section:
                        if isinstance(applicant, dict) and 'applicant-name' in applicant:
                            name_data = applicant['applicant-name']
                            if isinstance(name_data, dict) and 'name' in name_data:
                                name = name_data['name'].get('$', name_data['name'].get('#text', str(name_data['name'])))
                                
                                if isinstance(name, str) and name.strip() and name not in seen_names:
                                    clean_name = name.strip()
                                    category = self._categorize_applicant(clean_name)
                                    
                                    # Extract country if available
                                    country = None
                                    if 'residence' in applicant:
                                        country_data = applicant['residence'].get('country', {})
                                        if isinstance(country_data, dict):
                                            country = country_data.get('$', '')
                                    
                                    applicants.append(Applicant(
                                        name=clean_name,
                                        category=category,
                                        country=country
                                    ))
                                    seen_names.add(name)
            
            return applicants
            
        except Exception as e:
            print(f"⚠️ Error extracting applicants for {ops_response.ep_number}: {e}")
            return []
    
    def _categorize_applicant(self, applicant_name: str) -> str:
        """
        Categorize applicant as University or Industry/Other.
        
        Args:
            applicant_name: Name of the applicant
            
        Returns:
            "University" or "Industry/Other"
        """
        name_lower = applicant_name.lower()
        
        for term in self.university_terms:
            if term in name_lower:
                return "University"
        
        return "Industry/Other"
    
    def _find_recursive(self, data: Any, target_keys: List[str]) -> List[Any]:
        """
        Recursively find keys in nested structure.
        
        Args:
            data: Data structure to search
            target_keys: List of keys to find
            
        Returns:
            List of found values
        """
        results = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if any(target in key.lower() for target in target_keys):
                    results.append(value)
                results.extend(self._find_recursive(value, target_keys))
        elif isinstance(data, list):
            for item in data:
                results.extend(self._find_recursive(item, target_keys))
        
        return results
    
    def analyze_collaboration_patterns(self, all_applicants: List[List[Applicant]]) -> Dict[str, Any]:
        """
        Analyze collaboration patterns across multiple patents.
        
        Args:
            all_applicants: List of applicant lists for each patent
            
        Returns:
            Dictionary with collaboration statistics
        """
        total_patents = len(all_applicants)
        
        if total_patents == 0:
            return {}
        
        # Aggregate unique applicants
        all_unique_applicants = {}
        collaboration_count = 0
        
        for patent_applicants in all_applicants:
            if len(patent_applicants) > 1:
                collaboration_count += 1
            
            for applicant in patent_applicants:
                all_unique_applicants[applicant.name] = applicant
        
        # Categorize applicants
        university_count = sum(1 for a in all_unique_applicants.values() if a.category == "University")
        industry_count = sum(1 for a in all_unique_applicants.values() if a.category == "Industry/Other")
        
        collaboration_rate = (collaboration_count / total_patents * 100) if total_patents > 0 else 0
        
        return {
            'total_patents': total_patents,
            'patents_with_collaboration': collaboration_count,
            'collaboration_rate': round(collaboration_rate, 1),
            'unique_applicants': len(all_unique_applicants),
            'university_entities': university_count,
            'industry_partners': industry_count,
            'top_applicants': self._get_top_applicants(all_applicants, 10)
        }
    
    def _get_top_applicants(self, all_applicants: List[List[Applicant]], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top applicants by frequency across patents."""
        applicant_counts = {}
        
        for patent_applicants in all_applicants:
            for applicant in patent_applicants:
                key = (applicant.name, applicant.category)
                applicant_counts[key] = applicant_counts.get(key, 0) + 1
        
        # Sort by frequency and return top N
        sorted_applicants = sorted(applicant_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'name': name,
                'category': category,
                'patent_count': count
            }
            for (name, category), count in sorted_applicants[:limit]
        ]