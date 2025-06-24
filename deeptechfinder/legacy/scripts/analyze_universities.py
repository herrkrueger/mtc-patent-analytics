#!/usr/bin/env python3
"""
Analyze DeepTechFinder dataset to extract university statistics for interactive widgets.

This script processes the DeepTechFinder CSV to create a structured dataset with:
- University names
- Student counts
- Total patent applications
- Granted patents count
"""

import pandas as pd
import json
from collections import defaultdict

def analyze_universities():
    """Analyze the DeepTechFinder dataset and extract university statistics."""
    
    # Read the CSV file
    csv_path = "/home/jovyan/mtc-patent-analytics/deeptechfinder/data/EPO_DeepTechFinder_20250513_DE_Uni_Top100.csv"
    print(f"Reading CSV file: {csv_path}")
    
    try:
        # Try different encodings to handle the file
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_path, encoding=encoding)
                print(f"Successfully loaded with {encoding} encoding: {len(df)} rows and {len(df.columns)} columns")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("Could not read file with any standard encoding")
            return None
            
        print(f"Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None
    
    # Get unique universities
    unique_universities = df['University'].unique()
    print(f"Found {len(unique_universities)} unique universities")
    
    # Initialize results structure
    university_stats = {}
    
    # Process each university
    for university in unique_universities:
        # Filter data for this university
        uni_data = df[df['University'] == university]
        
        # Calculate statistics
        total_applications = len(uni_data)
        
        # Get student count (should be same for all rows of same university)
        student_counts = uni_data['Total_students'].unique()
        total_students = student_counts[0] if len(student_counts) > 0 else 0
        
        # Count granted patents
        granted_patents = len(uni_data[uni_data['Patent_status'] == 'EP granted'])
        
        # Store results
        university_stats[university] = {
            'name': university,
            'total_students': int(total_students) if pd.notna(total_students) else 0,
            'total_applications': total_applications,
            'granted_patents': granted_patents,
            'grant_rate': round(granted_patents / total_applications * 100, 1) if total_applications > 0 else 0
        }
        
        print(f"{university}: {total_students} students, {total_applications} applications, {granted_patents} granted ({university_stats[university]['grant_rate']}%)")
    
    # Sort by total applications (descending) for initial display
    sorted_universities = sorted(university_stats.values(), 
                                key=lambda x: x['total_applications'], 
                                reverse=True)
    
    # Create summary statistics
    summary = {
        'total_universities': len(unique_universities),
        'total_students': sum(uni['total_students'] for uni in university_stats.values()),
        'total_applications': sum(uni['total_applications'] for uni in university_stats.values()),
        'total_granted': sum(uni['granted_patents'] for uni in university_stats.values()),
        'overall_grant_rate': round(sum(uni['granted_patents'] for uni in university_stats.values()) / 
                                   sum(uni['total_applications'] for uni in university_stats.values()) * 100, 1)
    }
    
    print("\n=== SUMMARY STATISTICS ===")
    print(f"Total Universities: {summary['total_universities']}")
    print(f"Total Students: {summary['total_students']:,}")
    print(f"Total Applications: {summary['total_applications']:,}")
    print(f"Total Granted: {summary['total_granted']:,}")
    print(f"Overall Grant Rate: {summary['overall_grant_rate']}%")
    
    # Prepare data for interactive widgets
    widget_data = {
        'universities': sorted_universities,
        'summary': summary,
        'sorting_options': {
            'alphabetical': sorted(university_stats.values(), key=lambda x: x['name']),
            'by_students': sorted(university_stats.values(), key=lambda x: x['total_students'], reverse=True),
            'by_applications': sorted(university_stats.values(), key=lambda x: x['total_applications'], reverse=True),
            'by_granted': sorted(university_stats.values(), key=lambda x: x['granted_patents'], reverse=True),
            'by_grant_rate': sorted(university_stats.values(), key=lambda x: x['grant_rate'], reverse=True)
        }
    }
    
    return widget_data

def save_results(data, output_path):
    """Save the analysis results to JSON file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to: {output_path}")
    except Exception as e:
        print(f"Error saving results: {e}")

if __name__ == "__main__":
    # Analyze the data
    results = analyze_universities()
    
    if results:
        # Save to JSON file for easy loading in notebooks
        output_path = "/home/jovyan/mtc-patent-analytics/deeptechfinder/output/university_analysis.json"
        save_results(results, output_path)
        
        # Display top 10 universities by applications
        print("\n=== TOP 10 UNIVERSITIES BY APPLICATIONS ===")
        for i, uni in enumerate(results['universities'][:10], 1):
            print(f"{i:2d}. {uni['name'][:50]:<50} | Students: {uni['total_students']:>6,} | Apps: {uni['total_applications']:>4} | Granted: {uni['granted_patents']:>3} ({uni['grant_rate']:>5.1f}%)")
        
        # Display top 10 universities by students
        print("\n=== TOP 10 UNIVERSITIES BY STUDENT COUNT ===")
        for i, uni in enumerate(results['sorting_options']['by_students'][:10], 1):
            print(f"{i:2d}. {uni['name'][:50]:<50} | Students: {uni['total_students']:>6,} | Apps: {uni['total_applications']:>4} | Granted: {uni['granted_patents']:>3} ({uni['grant_rate']:>5.1f}%)")
        
        print(f"\nComplete analysis saved to: {output_path}")
        print("Data structure ready for interactive widgets!")