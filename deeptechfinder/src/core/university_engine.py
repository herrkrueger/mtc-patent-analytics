"""
Main University Engine - ETL orchestrator for patent analysis.
"""

import time
from typing import Optional, List, Dict, Any
from datetime import datetime

from .config import config
from .exceptions import *
from ..etl.extract.deeptechfinder_reader import DeepTechFinderReader
from ..etl.extract.epo_ops_client import EPOOPSClient
from ..etl.transform.priority_normalizer import PriorityNormalizer
from ..etl.transform.applicant_normalizer import ApplicantNormalizer
from ..etl.transform.inventor_normalizer import InventorNormalizer
from ..etl.load.data_models import (
    UniversityPortfolio, EnrichedPatent, BiblioData, AnalysisResult
)

class UniversityEngine:
    """
    Main ETL engine for university patent analysis.
    Orchestrates Extract → Transform → Load → Analyze workflow.
    """
    
    def __init__(self):
        # Initialize ETL components
        self.dtf_reader = DeepTechFinderReader()
        self.ops_client = EPOOPSClient()
        self.priority_normalizer = PriorityNormalizer()
        self.applicant_normalizer = ApplicantNormalizer()
        self.inventor_normalizer = InventorNormalizer()
        
        print(f"🏭 University Engine initialized")
        print(f"📊 Config: {config.app.name} v{config.app.version}")
    
    def analyze_university(self, 
                          university_name: str, 
                          patent_limit: Optional[int] = None) -> AnalysisResult:
        """
        Complete ETL pipeline for university patent analysis.
        
        Args:
            university_name: Name of the university to analyze
            patent_limit: Maximum number of patents to process (None for default)
            
        Returns:
            AnalysisResult with complete analysis
        """
        if patent_limit is None:
            patent_limit = config.analysis.default_patent_limit
        
        print(f"\n🚀 STARTING UNIVERSITY ANALYSIS")
        print("=" * 60)
        print(f"🏛️  University: {university_name}")
        print(f"📄 Patent limit: {patent_limit}")
        print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")
        
        # EXTRACT Phase
        print(f"\n📥 EXTRACT PHASE")
        print("-" * 20)
        portfolio = self._extract_data(university_name, patent_limit)
        
        # TRANSFORM Phase
        print(f"\n🔄 TRANSFORM PHASE") 
        print("-" * 20)
        self._transform_data(portfolio)
        
        # ANALYZE Phase
        print(f"\n📊 ANALYZE PHASE")
        print("-" * 20)
        analysis_result = self._analyze_data(portfolio)
        
        print(f"\n🎯 ANALYSIS COMPLETED")
        print("=" * 30)
        print(f"✅ Patents processed: {portfolio.patents_retrieved}/{portfolio.patents_requested}")
        print(f"📈 Success rate: {portfolio.success_rate:.1f}%")
        print(f"🕐 Completed: {datetime.now().strftime('%H:%M:%S')}")
        
        return analysis_result
    
    def _extract_data(self, university_name: str, patent_limit: int) -> UniversityPortfolio:
        """
        EXTRACT phase: Get raw data from DeepTechFinder CSV and EPO OPS.
        """
        # Extract CSV data
        print(f"📄 Extracting DeepTechFinder data...")
        patent_applications = self.dtf_reader.get_university_patents(university_name, patent_limit)
        
        if not patent_applications:
            raise UniversityNotFoundError(f"No patents found for {university_name}")
        
        # Initialize portfolio
        portfolio = UniversityPortfolio(
            university_name=university_name,
            total_students=patent_applications[0].total_students,
            patents_requested=len(patent_applications),
            patents_retrieved=0
        )
        
        print(f"📄 Found {len(patent_applications)} patent applications")
        
        # Test EPO OPS connection
        print(f"🔐 Testing EPO OPS connection...")
        if not self.ops_client.test_connection():
            print(f"⚠️  EPO OPS connection test failed, proceeding anyway...")
        
        # Authenticate with EPO OPS
        if not self.ops_client.get_access_token():
            raise AuthenticationError("Failed to authenticate with EPO OPS")
        
        # Extract EPO OPS data for each patent
        print(f"🌐 Extracting EPO OPS bibliographic data...")
        
        for i, patent_app in enumerate(patent_applications, 1):
            ep_number = self.dtf_reader.extract_ep_number(patent_app.espacenet_link)
            
            if not ep_number:
                print(f"⚠️  {i}/{len(patent_applications)}: Invalid EP number from {patent_app.espacenet_link}")
                continue
            
            print(f"🔍 {i}/{len(patent_applications)}: Processing {ep_number}")
            
            # Get EPO OPS data with rate limiting
            ops_response = self.ops_client.fetch_with_rate_limit(ep_number)
            
            # Create enriched patent record
            enriched_patent = EnrichedPatent(
                ep_number=ep_number,
                university=patent_app.university,
                filing_year=patent_app.filing_year,
                patent_status=patent_app.patent_status,
                technical_field=patent_app.technical_field,
                original_title=patent_app.application_title,
                ops_success=(ops_response.status_code == 200)
            )
            
            if ops_response.status_code == 200:
                print(f"✅ Retrieved data for {ep_number}")
                portfolio.patents_retrieved += 1
                # Store raw OPS data for transformation phase
                enriched_patent._ops_response = ops_response
            else:
                print(f"❌ Failed to retrieve {ep_number}: {ops_response.error_message}")
                enriched_patent.errors.append(ops_response.error_message or "Unknown error")
            
            portfolio.patents.append(enriched_patent)
        
        portfolio.calculate_success_rate()
        print(f"📊 Extraction complete: {portfolio.patents_retrieved}/{portfolio.patents_requested} patents ({portfolio.success_rate:.1f}% success)")
        
        return portfolio
    
    def _transform_data(self, portfolio: UniversityPortfolio):
        """
        TRANSFORM phase: Normalize and clean all extracted data.
        """
        print(f"🔄 Transforming bibliographic data...")
        
        successful_patents = [p for p in portfolio.patents if p.ops_success and hasattr(p, '_ops_response')]
        
        if not successful_patents:
            print(f"⚠️  No successful EPO OPS responses to transform")
            return
        
        all_priorities = []
        all_applicants = []
        all_inventors = []
        
        for patent in successful_patents:
            ops_response = patent._ops_response
            
            # Transform priorities
            priorities = self.priority_normalizer.extract_priority_claims(ops_response)
            
            # Transform applicants
            applicants = self.applicant_normalizer.extract_applicants(ops_response)
            
            # Transform inventors
            inventors = self.inventor_normalizer.extract_inventors(ops_response)
            
            # Extract title (simple for now)
            title = self._extract_title(ops_response)
            
            # Create BiblioData
            patent.biblio = BiblioData(
                ep_number=patent.ep_number,
                title=title or patent.original_title,
                applicants=applicants,
                inventors=inventors,
                priority_claims=priorities
            )
            
            # Collect for aggregation
            all_priorities.append(priorities)
            all_applicants.append(applicants)
            all_inventors.append(inventors)
            
            # Clean up temporary data
            delattr(patent, '_ops_response')
        
        # Aggregate unique entities
        portfolio.unique_applicants = self._aggregate_unique_applicants(all_applicants)
        portfolio.unique_inventors = self._aggregate_unique_inventors(all_inventors)
        portfolio.priority_statistics = self.priority_normalizer.analyze_priority_patterns(all_priorities)
        
        print(f"✅ Transformation complete:")
        print(f"   👥 Unique applicants: {len(portfolio.unique_applicants)}")
        print(f"   🔬 Unique inventors: {len(portfolio.unique_inventors)}")
        print(f"   🏁 Priority claims: {portfolio.priority_statistics.get('total_priority_claims', 0)}")
    
    def _extract_title(self, ops_response) -> Optional[str]:
        """Extract patent title from EPO OPS response."""
        try:
            title_data = self.applicant_normalizer._find_recursive(ops_response.response_data, ['invention-title'])
            
            for title_section in title_data:
                if isinstance(title_section, list):
                    for title_item in title_section:
                        if isinstance(title_item, dict):
                            # Prefer English title
                            if title_item.get('@lang') == 'en':
                                return title_item.get('$', title_item.get('#text', ''))
                            elif title_item.get('$') or title_item.get('#text'):
                                return title_item.get('$', title_item.get('#text', ''))
            return None
        except Exception:
            return None
    
    def _aggregate_unique_applicants(self, all_applicants: List[List]) -> List:
        """Aggregate unique applicants across all patents."""
        unique_applicants = {}
        for patent_applicants in all_applicants:
            for applicant in patent_applicants:
                unique_applicants[applicant.name] = applicant
        return list(unique_applicants.values())
    
    def _aggregate_unique_inventors(self, all_inventors: List[List]) -> List:
        """Aggregate unique inventors across all patents."""
        unique_inventors = {}
        for patent_inventors in all_inventors:
            for inventor in patent_inventors:
                unique_inventors[inventor.name] = inventor
        return list(unique_inventors.values())
    
    def _analyze_data(self, portfolio: UniversityPortfolio) -> AnalysisResult:
        """
        ANALYZE phase: Generate insights from transformed data.
        """
        # Extract data for analysis
        all_applicants = [[a for a in p.biblio.applicants] for p in portfolio.patents if p.biblio]
        all_inventors = [[i for i in p.biblio.inventors] for p in portfolio.patents if p.biblio]
        all_priorities = [[pc for pc in p.biblio.priority_claims] for p in portfolio.patents if p.biblio]
        
        # Generate analysis results
        collaboration_insights = self.applicant_normalizer.analyze_collaboration_patterns(all_applicants)
        priority_analysis = self.priority_normalizer.analyze_priority_patterns(all_priorities)
        inventor_network = self.inventor_normalizer.analyze_inventor_network(all_inventors)
        
        print(f"📊 Analysis insights generated:")
        print(f"   🤝 Collaboration rate: {collaboration_insights.get('collaboration_rate', 0)}%")
        print(f"   🇩🇪 German priority rate: {priority_analysis.get('german_priority_rate', 0)}%")
        print(f"   🔬 Inventor network: {inventor_network.get('unique_inventors', 0)} researchers")
        
        return AnalysisResult(
            portfolio=portfolio,
            collaboration_insights=collaboration_insights,
            priority_analysis=priority_analysis,
            inventor_network=inventor_network
        )
    
    def get_available_universities(self) -> List[str]:
        """Get list of available universities."""
        return self.dtf_reader.get_available_universities()
    
    def test_system(self) -> bool:
        """Test all system components."""
        try:
            print("🔧 Testing system components...")
            
            # Test data loading
            universities = self.dtf_reader.get_available_universities()
            print(f"✅ Data loading: {len(universities)} universities available")
            
            # Test EPO OPS connection
            ops_works = self.ops_client.test_connection()
            print(f"{'✅' if ops_works else '❌'} EPO OPS connection: {'Working' if ops_works else 'Failed'}")
            
            return len(universities) > 0 and ops_works
            
        except Exception as e:
            print(f"❌ System test failed: {e}")
            return False