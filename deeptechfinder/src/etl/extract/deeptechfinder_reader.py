"""
DeepTechFinder CSV data reader with proper encoding handling.
"""

import pandas as pd
from typing import List, Optional
from pathlib import Path

from ...core.config import config
from ...core.exceptions import DataExtractionError, UniversityNotFoundError
from ..load.data_models import PatentApplication

class DeepTechFinderReader:
    """
    Reader for DeepTechFinder CSV data with latin-1 encoding support.
    """
    
    def __init__(self):
        self.data_file = config.get_data_file_path()
        self.encoding = config.data.encoding
        self._df = None
    
    def load_data(self) -> pd.DataFrame:
        """
        Load the DeepTechFinder CSV file with proper encoding.
        """
        if self._df is not None:
            return self._df
        
        try:
            print(f"📊 Loading DeepTechFinder data from {self.data_file}")
            
            # Try specified encoding first, then fallback options
            encodings = [self.encoding, 'utf-8', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    self._df = pd.read_csv(self.data_file, encoding=encoding)
                    print(f"✅ Successfully loaded with {encoding} encoding: {len(self._df)} rows and {len(self._df.columns)} columns")
                    break
                except UnicodeDecodeError:
                    continue
            
            if self._df is None:
                raise DataExtractionError(f"Could not read {self.data_file} with any encoding")
            
            print(f"📋 Columns: {list(self._df.columns)}")
            return self._df
            
        except Exception as e:
            raise DataExtractionError(f"Failed to load DeepTechFinder data: {e}")
    
    def get_available_universities(self) -> List[str]:
        """
        Get list of all available universities in the dataset.
        """
        df = self.load_data()
        universities = sorted(df['University'].unique())
        print(f"📚 Found {len(universities)} universities in dataset")
        return universities
    
    def get_university_patents(self, university_name: str, limit: Optional[int] = None) -> List[PatentApplication]:
        """
        Get patent applications for a specific university.
        
        Args:
            university_name: Name of the university (must match exactly)
            limit: Maximum number of patents to return (None for all)
        
        Returns:
            List of PatentApplication objects
        """
        df = self.load_data()
        
        # Filter by university
        university_data = df[df['University'] == university_name]
        
        if len(university_data) == 0:
            available = self.get_available_universities()
            raise UniversityNotFoundError(
                f"University '{university_name}' not found. "
                f"Available universities: {available[:10]}..." if len(available) > 10 else f"Available: {available}"
            )
        
        # Apply limit if specified
        if limit:
            university_data = university_data.head(limit)
        
        print(f"📄 Found {len(university_data)} patents for {university_name}")
        
        # Convert to PatentApplication objects
        patents = []
        for _, row in university_data.iterrows():
            patent = PatentApplication(
                university=row['University'],
                espacenet_link=row['Espacenet_link'],
                filing_year=str(row['Filing_year']),
                patent_status=row['Patent_status'],
                technical_field=row['Technical_field'],
                application_title=row['Application_title'],
                total_students=int(row['Total_students']) if pd.notna(row['Total_students']) else 0,
                total_applications=int(row['Total_number_of_applications']) if pd.notna(row['Total_number_of_applications']) else 0
            )
            patents.append(patent)
        
        return patents
    
    def extract_ep_number(self, espacenet_link: str) -> Optional[str]:
        """
        Extract EP patent number from Espacenet link.
        
        Args:
            espacenet_link: Full Espacenet URL
            
        Returns:
            EP patent number (e.g., "EP19196837A") or None if not found
        """
        try:
            if 'espacenet' in espacenet_link.lower() and '=' in espacenet_link:
                return espacenet_link.split('=')[-1]
            return None
        except Exception:
            return None
    
    def get_university_statistics(self) -> pd.DataFrame:
        """
        Get summary statistics for all universities.
        """
        df = self.load_data()
        
        stats = []
        for university in df['University'].unique():
            uni_data = df[df['University'] == university]
            
            stat = {
                'university': university,
                'total_students': uni_data['Total_students'].iloc[0] if len(uni_data) > 0 else 0,
                'total_applications': len(uni_data),
                'granted_patents': len(uni_data[uni_data['Patent_status'] == 'EP granted']),
            }
            stat['grant_rate'] = (stat['granted_patents'] / stat['total_applications'] * 100) if stat['total_applications'] > 0 else 0
            stats.append(stat)
        
        return pd.DataFrame(stats).sort_values('total_applications', ascending=False)