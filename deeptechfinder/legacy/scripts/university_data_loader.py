#!/usr/bin/env python3
"""
University Data Loader for Interactive Widgets

This module provides easy access to the analyzed DeepTechFinder university data
for creating interactive widgets, dropdowns, and visualizations.
"""

import json
import pandas as pd
from typing import Dict, List, Optional

def load_university_data(json_path: str = "/home/jovyan/mtc-patent-analytics/deeptechfinder/output/university_analysis.json") -> Dict:
    """
    Load the analyzed university data from JSON file.
    
    Args:
        json_path: Path to the university analysis JSON file
        
    Returns:
        Dictionary containing university data and sorting options
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Data file not found at {json_path}. Please run analyze_universities.py first.")
        return {}
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}

def get_university_names(sort_by: str = "alphabetical") -> List[str]:
    """
    Get list of university names for dropdown widgets.
    
    Args:
        sort_by: How to sort the names
                'alphabetical' - Alphabetical order
                'by_students' - By student count (descending)
                'by_applications' - By application count (descending)
                'by_granted' - By granted patents (descending)
                'by_grant_rate' - By grant rate (descending)
    
    Returns:
        List of university names
    """
    data = load_university_data()
    if not data:
        return []
    
    if sort_by in data.get('sorting_options', {}):
        return [uni['name'] for uni in data['sorting_options'][sort_by]]
    else:
        return [uni['name'] for uni in data.get('universities', [])]

def get_university_info(university_name: str) -> Optional[Dict]:
    """
    Get detailed information for a specific university.
    
    Args:
        university_name: Name of the university
        
    Returns:
        Dictionary with university details or None if not found
    """
    data = load_university_data()
    if not data:
        return None
    
    for uni in data.get('universities', []):
        if uni['name'] == university_name:
            return uni
    
    return None

def get_universities_dataframe(sort_by: str = "by_applications") -> pd.DataFrame:
    """
    Get university data as a pandas DataFrame for easy analysis and visualization.
    
    Args:
        sort_by: How to sort the data (same options as get_university_names)
        
    Returns:
        pandas DataFrame with university statistics
    """
    data = load_university_data()
    if not data:
        return pd.DataFrame()
    
    if sort_by in data.get('sorting_options', {}):
        universities = data['sorting_options'][sort_by]
    else:
        universities = data.get('universities', [])
    
    return pd.DataFrame(universities)

def get_summary_stats() -> Dict:
    """
    Get overall summary statistics.
    
    Returns:
        Dictionary with summary statistics
    """
    data = load_university_data()
    return data.get('summary', {})

def create_widget_options() -> Dict[str, List[str]]:
    """
    Create options dictionary for interactive widgets.
    
    Returns:
        Dictionary with different sorting options for dropdowns
    """
    return {
        'Alphabetical': get_university_names('alphabetical'),
        'By Student Count': get_university_names('by_students'),
        'By Application Count': get_university_names('by_applications'),
        'By Granted Patents': get_university_names('by_granted'),
        'By Grant Rate': get_university_names('by_grant_rate')
    }

# Example usage functions for interactive widgets
def get_top_universities(n: int = 10, sort_by: str = "by_applications") -> List[Dict]:
    """Get top N universities by specified criteria."""
    data = load_university_data()
    if not data:
        return []
    
    if sort_by in data.get('sorting_options', {}):
        return data['sorting_options'][sort_by][:n]
    else:
        return data.get('universities', [])[:n]

def search_universities(search_term: str) -> List[str]:
    """Search for universities containing the search term."""
    all_names = get_university_names('alphabetical')
    return [name for name in all_names if search_term.lower() in name.lower()]

if __name__ == "__main__":
    # Demo the functions
    print("=== University Data Loader Demo ===")
    
    # Load and display summary
    summary = get_summary_stats()
    print(f"Total Universities: {summary.get('total_universities', 0)}")
    print(f"Total Students: {summary.get('total_students', 0):,}")
    print(f"Total Applications: {summary.get('total_applications', 0):,}")
    print(f"Overall Grant Rate: {summary.get('overall_grant_rate', 0)}%")
    
    # Show widget options
    options = create_widget_options()
    print(f"\nWidget sorting options available: {list(options.keys())}")
    
    # Example university lookup
    test_uni = "Karlsruhe Institute of Technology"
    info = get_university_info(test_uni)
    if info:
        print(f"\n{test_uni}:")
        print(f"  Students: {info['total_students']:,}")
        print(f"  Applications: {info['total_applications']}")
        print(f"  Granted: {info['granted_patents']} ({info['grant_rate']}%)")
    
    # Search example
    search_results = search_universities("Berlin")
    print(f"\nUniversities containing 'Berlin': {len(search_results)}")
    for uni in search_results:
        print(f"  - {uni}")