"""
Inventor normalization and standardization.
"""

import re
from typing import List, Dict, Any
from ..load.data_models import Inventor, EPOOPSResponse

class InventorNormalizer:
    """
    Normalizes inventor names from EPO OPS responses.
    Implements proper name standardization to eliminate duplicates.
    """
    
    def extract_inventors(self, ops_response: EPOOPSResponse) -> List[Inventor]:
        """
        Extract and normalize inventors from EPO OPS response.
        
        Args:
            ops_response: EPO OPS API response
            
        Returns:
            List of normalized Inventor objects
        """
        if not ops_response.response_data or ops_response.status_code != 200:
            return []
        
        try:
            inventors = []
            
            # Find inventor data using recursive search
            inventor_data = self._find_recursive(ops_response.response_data, ['inventor'])
            
            seen_names = set()
            
            for inv_section in inventor_data:
                if isinstance(inv_section, list):
                    for inventor in inv_section:
                        if isinstance(inventor, dict) and 'inventor-name' in inventor:
                            name_data = inventor['inventor-name']
                            if isinstance(name_data, dict) and 'name' in name_data:
                                name = name_data['name'].get('$', name_data['name'].get('#text', str(name_data['name'])))
                                
                                if isinstance(name, str) and name.strip():
                                    normalized_name = self._normalize_inventor_name(name.strip())
                                    
                                    if normalized_name and normalized_name not in seen_names:
                                        # Extract country if available
                                        country = None
                                        if 'residence' in inventor:
                                            country_data = inventor['residence'].get('country', {})
                                            if isinstance(country_data, dict):
                                                country = country_data.get('$', '')
                                        
                                        inventors.append(Inventor(
                                            name=normalized_name,
                                            country=country
                                        ))
                                        seen_names.add(normalized_name)
            
            return inventors
            
        except Exception as e:
            print(f"⚠️ Error extracting inventors for {ops_response.ep_number}: {e}")
            return []
    
    def _normalize_inventor_name(self, name: str) -> str:
        """
        Normalize inventor name to eliminate comma-based duplicates.
        Implements improved normalization from legacy fixes.
        
        Args:
            name: Raw inventor name
            
        Returns:
            Normalized inventor name
        """
        if not name or not isinstance(name, str):
            return ""
        
        # Clean up the name
        normalized = name.strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Handle comma variations properly
        # Example: "Smith, John" vs "Smith,John" vs "Smith , John"
        if ',' in normalized:
            parts = [part.strip() for part in normalized.split(',')]
            if len(parts) == 2 and parts[0] and parts[1]:
                # Standard "Last, First" format
                normalized = f"{parts[0]}, {parts[1]}"
        
        # Remove trailing punctuation except for titles
        normalized = re.sub(r'[.,;]$', '', normalized)
        
        # Standardize title abbreviations
        normalized = re.sub(r'\bDr\.\s*', 'Dr. ', normalized)
        normalized = re.sub(r'\bProf\.\s*', 'Prof. ', normalized)
        
        return normalized.strip()
    
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
    
    def analyze_inventor_network(self, all_inventors: List[List[Inventor]]) -> Dict[str, Any]:
        """
        Analyze inventor network patterns across multiple patents.
        
        Args:
            all_inventors: List of inventor lists for each patent
            
        Returns:
            Dictionary with inventor network statistics
        """
        total_patents = len(all_inventors)
        
        if total_patents == 0:
            return {}
        
        # Count inventor frequencies
        inventor_counts = {}
        total_inventor_instances = 0
        
        for patent_inventors in all_inventors:
            for inventor in patent_inventors:
                inventor_counts[inventor.name] = inventor_counts.get(inventor.name, 0) + 1
                total_inventor_instances += 1
        
        # Calculate statistics
        unique_inventors = len(inventor_counts)
        avg_inventors_per_patent = total_inventor_instances / total_patents if total_patents > 0 else 0
        
        # Categorize inventors by productivity
        core_researchers = len([c for c in inventor_counts.values() if c >= 3])
        regular_contributors = len([c for c in inventor_counts.values() if c == 2])
        specialized_contributors = len([c for c in inventor_counts.values() if c == 1])
        
        # Top inventors
        top_inventors = sorted(inventor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_patents': total_patents,
            'unique_inventors': unique_inventors,
            'total_inventor_instances': total_inventor_instances,
            'avg_inventors_per_patent': round(avg_inventors_per_patent, 1),
            'core_researchers': core_researchers,  # 3+ patents
            'regular_contributors': regular_contributors,  # 2 patents
            'specialized_contributors': specialized_contributors,  # 1 patent
            'top_inventors': [
                {'name': name, 'patent_count': count} 
                for name, count in top_inventors
            ]
        }