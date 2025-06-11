"""
Data models for patent analytics using Pydantic for validation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class PatentApplication(BaseModel):
    """Raw patent application data from DeepTechFinder CSV."""
    university: str
    espacenet_link: str
    filing_year: str
    patent_status: str
    technical_field: str
    application_title: str
    total_students: int
    total_applications: int

class PriorityClaim(BaseModel):
    """Normalized priority claim data."""
    country: str
    number: str
    date: str
    formatted: str  # e.g., "DE102123456A·2021-03-15"

class Applicant(BaseModel):
    """Normalized applicant data."""
    name: str
    category: str  # "University" or "Industry/Other"
    country: Optional[str] = None

class Inventor(BaseModel):
    """Normalized inventor data."""
    name: str
    country: Optional[str] = None

class Classification(BaseModel):
    """Patent classification data."""
    system: str  # "IPC" or "CPC"
    code: str
    description: Optional[str] = None

class EPOOPSResponse(BaseModel):
    """Raw EPO OPS API response data."""
    ep_number: str
    status_code: int
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retrieved_at: datetime = Field(default_factory=datetime.now)

class BiblioData(BaseModel):
    """Extracted and normalized bibliographic data."""
    ep_number: str
    title: Optional[str] = None
    applicants: List[Applicant] = Field(default_factory=list)
    inventors: List[Inventor] = Field(default_factory=list)
    priority_claims: List[PriorityClaim] = Field(default_factory=list)
    classifications: List[Classification] = Field(default_factory=list)
    filing_date: Optional[str] = None
    publication_date: Optional[str] = None

class EnrichedPatent(BaseModel):
    """Complete patent record combining CSV and EPO OPS data."""
    # Original CSV data
    ep_number: str
    university: str
    filing_year: str
    patent_status: str
    technical_field: str
    original_title: str
    
    # Enriched bibliographic data
    biblio: Optional[BiblioData] = None
    
    # Processing metadata
    ops_success: bool = False
    extraction_date: datetime = Field(default_factory=datetime.now)
    errors: List[str] = Field(default_factory=list)

class UniversityPortfolio(BaseModel):
    """Complete university patent portfolio."""
    university_name: str
    total_students: int
    
    # Patent data
    patents: List[EnrichedPatent] = Field(default_factory=list)
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.now)
    patents_requested: int
    patents_retrieved: int
    success_rate: float = 0.0
    
    # Aggregated data
    unique_applicants: List[Applicant] = Field(default_factory=list)
    unique_inventors: List[Inventor] = Field(default_factory=list)
    priority_statistics: Dict[str, int] = Field(default_factory=dict)
    classification_statistics: Dict[str, int] = Field(default_factory=dict)
    
    def calculate_success_rate(self):
        """Calculate and update success rate."""
        if self.patents_requested > 0:
            successful = sum(1 for p in self.patents if p.ops_success)
            self.success_rate = (successful / self.patents_requested) * 100.0
        else:
            self.success_rate = 0.0

class AnalysisResult(BaseModel):
    """Results from university patent analysis."""
    portfolio: UniversityPortfolio
    
    # Analysis results
    collaboration_insights: Dict[str, Any] = Field(default_factory=dict)
    priority_analysis: Dict[str, Any] = Field(default_factory=dict)
    technology_analysis: Dict[str, Any] = Field(default_factory=dict)
    inventor_network: Dict[str, Any] = Field(default_factory=dict)
    
    # Export paths
    export_paths: Dict[str, str] = Field(default_factory=dict)