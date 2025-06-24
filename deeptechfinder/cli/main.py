"""
Command-line interface for DeepTechFinder Patent Analytics.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.core.university_engine import UniversityEngine
from src.core.config import config
from src.core.exceptions import *

def cmd_test_system(args):
    """Test system components."""
    print(f"🔧 {config.app.name} v{config.app.version}")
    print("=" * 50)
    
    engine = UniversityEngine()
    
    if engine.test_system():
        print("\n✅ All systems operational!")
        return 0
    else:
        print("\n❌ System test failed!")
        return 1

def cmd_list_universities(args):
    """List available universities."""
    try:
        engine = UniversityEngine()
        universities = engine.get_available_universities()
        
        print(f"📚 Available Universities ({len(universities)}):")
        print("=" * 50)
        
        for i, uni in enumerate(universities, 1):
            print(f"{i:3d}. {uni}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def cmd_analyze_university(args):
    """Analyze a specific university."""
    try:
        engine = UniversityEngine()
        
        # Validate patent limit
        limit = args.limit
        if limit < config.analysis.min_patent_limit:
            limit = config.analysis.min_patent_limit
            print(f"⚠️  Adjusting limit to minimum: {limit}")
        elif limit > config.analysis.max_patent_limit:
            limit = config.analysis.max_patent_limit
            print(f"⚠️  Adjusting limit to maximum: {limit}")
        
        # Run analysis
        result = engine.analyze_university(args.university, limit)
        
        # Display summary
        portfolio = result.portfolio
        print(f"\n📋 ANALYSIS SUMMARY")
        print("=" * 30)
        print(f"🏛️  University: {portfolio.university_name}")
        print(f"👥 Students: {portfolio.total_students:,}")
        print(f"📄 Patents analyzed: {portfolio.patents_retrieved}/{portfolio.patents_requested}")
        print(f"📈 Success rate: {portfolio.success_rate:.1f}%")
        
        # Collaboration insights
        collab = result.collaboration_insights
        if collab:
            print(f"\n🤝 COLLABORATION:")
            print(f"   University entities: {collab.get('university_entities', 0)}")
            print(f"   Industry partners: {collab.get('industry_partners', 0)}")
            print(f"   Collaboration rate: {collab.get('collaboration_rate', 0):.1f}%")
        
        # Priority insights
        priority = result.priority_analysis
        if priority:
            print(f"\n🏁 PRIORITIES:")
            print(f"   Total priority claims: {priority.get('total_priority_claims', 0)}")
            print(f"   German priorities: {priority.get('german_priorities', 0)}")
            print(f"   German priority rate: {priority.get('german_priority_rate', 0):.1f}%")
        
        # Inventor insights
        inventors = result.inventor_network
        if inventors:
            print(f"\n🔬 INVENTORS:")
            print(f"   Unique inventors: {inventors.get('unique_inventors', 0)}")
            print(f"   Avg per patent: {inventors.get('avg_inventors_per_patent', 0)}")
            print(f"   Core researchers (3+ patents): {inventors.get('core_researchers', 0)}")
        
        print(f"\n✅ Analysis completed successfully!")
        return 0
        
    except UniversityNotFoundError as e:
        print(f"❌ University not found: {e}")
        print("💡 Use 'list' command to see available universities")
        return 1
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1

def cmd_test_api(args):
    """Test EPO OPS API with a specific patent."""
    try:
        from src.etl.extract.epo_ops_client import EPOOPSClient
        
        client = EPOOPSClient()
        
        print(f"🔐 Testing EPO OPS API...")
        print(f"📄 Test patent: {args.patent}")
        
        response = client.get_application_biblio(args.patent)
        
        if response.status_code == 200:
            print(f"✅ API test successful!")
            print(f"📊 Response size: {len(str(response.response_data))} characters")
            
            # Show some basic info
            if response.response_data:
                print(f"🔍 Response contains patent data")
            
            return 0
        else:
            print(f"❌ API test failed: {response.error_message}")
            return 1
            
    except Exception as e:
        print(f"❌ API test error: {e}")
        return 1

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=f"{config.app.name} v{config.app.version}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m cli.main test               # Test all systems
  python -m cli.main list               # List available universities  
  python -m cli.main analyze "TU Dresden" --limit 10
  python -m cli.main test-api EP19196837A
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test system components')
    test_parser.set_defaults(func=cmd_test_system)
    
    # List universities command
    list_parser = subparsers.add_parser('list', help='List available universities')
    list_parser.set_defaults(func=cmd_list_universities)
    
    # Analyze university command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze university portfolio')
    analyze_parser.add_argument('university', help='University name')
    analyze_parser.add_argument('--limit', type=int, default=config.analysis.default_patent_limit,
                               help=f'Patent limit (default: {config.analysis.default_patent_limit})')
    analyze_parser.set_defaults(func=cmd_analyze_university)
    
    # Test API command
    api_parser = subparsers.add_parser('test-api', help='Test EPO OPS API')
    api_parser.add_argument('patent', help='Patent number to test (e.g., EP19196837A)')
    api_parser.set_defaults(func=cmd_test_api)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())