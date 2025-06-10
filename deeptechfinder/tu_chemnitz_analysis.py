#!/usr/bin/env python3
"""
TU Chemnitz Patent Analysis with EPO OPS
Analyzes all TU Chemnitz patents from DeepTechFinder, extracts German priorities and industry collaborators
"""

import pandas as pd
import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict

# Load credentials
load_dotenv('../ipc-ops/.env')
ops_key = os.getenv('OPS_KEY')
ops_secret = os.getenv('OPS_SECRET')

print("🎯 TU CHEMNITZ PATENT ANALYSIS")
print("=" * 50)
print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")

class EPOOPSClient:
    def __init__(self):
        self.base_url = "http://ops.epo.org/3.2/rest-services"
        self.auth_url = "https://ops.epo.org/3.2/auth/accesstoken"
        self.consumer_key = ops_key
        self.consumer_secret = ops_secret
        self.access_token = None
        
    def get_access_token(self):
        try:
            response = requests.post(
                self.auth_url,
                data={'grant_type': 'client_credentials'},
                auth=(self.consumer_key, self.consumer_secret),
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                print(f"✅ EPO OPS authenticated (expires in {token_data.get('expires_in', 'unknown')}s)")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def format_patent_number(self, patent_number):
        clean_number = patent_number.replace('EP', '').replace('A', '').replace('B', '')
        
        # Leading zero handling for different patent eras
        if clean_number.startswith('0') and len(clean_number) == 8:
            return clean_number  # Keep leading zero for 2000s patents
        elif clean_number.startswith('00'):
            return clean_number.lstrip('0')
        else:
            return clean_number.lstrip('0') if clean_number.lstrip('0') else clean_number
    
    def get_application_biblio(self, patent_number):
        if not self.access_token:
            return None
        
        clean_number = self.format_patent_number(patent_number)
        
        # Try multiple formats
        formats_to_try = [
            f"published-data/application/epodoc/EP{clean_number}/biblio",
            f"published-data/application/epodoc/EP{clean_number.lstrip('0')}/biblio"
        ]
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        for endpoint in formats_to_try:
            url = f"{self.base_url}/{endpoint}"
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    continue
                else:
                    print(f"  ❌ Error {response.status_code} for {patent_number}")
                    return None
                    
            except Exception as e:
                print(f"  ❌ Request failed for {patent_number}: {e}")
                continue
        
        return None

def normalize_applicant_name(name):
    """Normalize applicant names to combine similar variations"""
    if not name:
        return ""
    
    normalized = name.upper().strip().split('[')[0].strip().rstrip(',').strip()
    
    # TU Chemnitz normalization patterns
    replacements = {
        'TECHNISCHE UNIVERSITÄT CHEMNITZ': 'TU CHEMNITZ',
        'TECHNISCHE UNIVERSITAET CHEMNITZ': 'TU CHEMNITZ',
        'TU CHEMNITZ': 'TU CHEMNITZ',
        'CHEMNITZ UNIVERSITY OF TECHNOLOGY': 'TU CHEMNITZ',
        'UNIVERSITY OF TECHNOLOGY CHEMNITZ': 'TU CHEMNITZ',
    }
    
    for old, new in replacements.items():
        if old in normalized:
            return new
    
    return normalized.strip()

def normalize_inventor_name(name):
    """
    Fixed inventor normalization to handle comma variations properly
    Examples:
    - "SMITH, John," → "Smith, John"
    - "SMITH JOHN [DE]" → "Smith, John" 
    - "Smith, John," → "Smith, John"
    """
    if not name:
        return ""
    
    # Remove country codes and clean up
    clean_name = name.strip().split('[')[0].strip().rstrip(',').strip()
    
    # Handle different formats
    if ',' in clean_name:
        # Format: "LASTNAME, FIRSTNAME" or "Lastname, Firstname"
        parts = clean_name.split(',', 1)  # Split only on first comma
        if len(parts) == 2:
            last_name = parts[0].strip()
            first_name = parts[1].strip()
            
            # Convert to proper case if all caps
            if last_name.isupper():
                last_name = last_name.title()
            if first_name.isupper():
                first_name = first_name.title()
            
            clean_name = f"{last_name}, {first_name}"
        else:
            clean_name = clean_name.title() if clean_name.isupper() else clean_name
    else:
        # Format: "LASTNAME FIRSTNAME" - convert to "Lastname, Firstname"
        parts = clean_name.split()
        if len(parts) >= 2:
            last_name = parts[0].strip()
            first_names = ' '.join(parts[1:]).strip()
            
            # Convert to proper case if all caps
            if last_name.isupper():
                last_name = last_name.title()
            if first_names.isupper():
                first_names = first_names.title()
            
            clean_name = f"{last_name}, {first_names}"
        else:
            clean_name = clean_name.title() if clean_name.isupper() else clean_name
    
    return clean_name

def extract_patent_data(biblio_data):
    """Extract comprehensive patent information from EPO OPS response"""
    
    extracted = {
        'application_number': None,
        'filing_date': None,
        'title': None,
        'applicants': [],
        'inventors': [],
        'ipc_classes': [],
        'cpc_classes': [],
        'priority_claims': []
    }
    
    if not biblio_data or not isinstance(biblio_data, dict):
        return extracted
    
    try:
        # Navigate EPO OPS response structure
        world_data = biblio_data.get('ops:world-patent-data', {})
        exchange_docs = world_data.get('exchange-documents', {})
        exchange_doc = exchange_docs.get('exchange-document', [])
        
        if isinstance(exchange_doc, list) and len(exchange_doc) > 0:
            doc = exchange_doc[0]
        elif isinstance(exchange_doc, dict):
            doc = exchange_doc
        else:
            return extracted
        
        biblio = doc.get('bibliographic-data', {})
        
        # Extract application reference
        app_ref = biblio.get('application-reference', {})
        if app_ref:
            doc_ids = app_ref.get('document-id', [])
            if isinstance(doc_ids, list):
                for doc_id in doc_ids:
                    if doc_id.get('@document-id-type') == 'epodoc':
                        doc_num = doc_id.get('doc-number', {}).get('$', '')
                        date = doc_id.get('date', {}).get('$', '')
                        extracted['application_number'] = doc_num
                        extracted['filing_date'] = date
                        break
        
        # Extract invention title (prefer English)
        titles = biblio.get('invention-title', [])
        if isinstance(titles, list):
            for title_obj in titles:
                if isinstance(title_obj, dict):
                    if title_obj.get('@lang') == 'en':
                        extracted['title'] = title_obj.get('$', '')
                        break
            if not extracted['title'] and len(titles) > 0:
                first_title = titles[0]
                if isinstance(first_title, dict):
                    extracted['title'] = first_title.get('$', '')
        elif isinstance(titles, dict):
            extracted['title'] = titles.get('$', '')
        
        # Extract applicants (prefer original format)
        parties = biblio.get('parties', {})
        applicants_section = parties.get('applicants', {})
        applicants = applicants_section.get('applicant', [])
        if not isinstance(applicants, list):
            applicants = [applicants]
        
        seen_applicants = set()
        for applicant in applicants:
            if isinstance(applicant, dict):
                data_format = applicant.get('@data-format', '')
                name_obj = applicant.get('applicant-name', {})
                
                if isinstance(name_obj, dict):
                    name = name_obj.get('name', {}).get('$', '')
                    clean_name = name.strip()
                    
                    if clean_name and clean_name not in seen_applicants:
                        if data_format == 'original' or len(seen_applicants) == 0:
                            extracted['applicants'].append(clean_name)
                            seen_applicants.add(clean_name)
        
        # Extract inventors (prefer original format)
        inventors_section = parties.get('inventors', {})
        inventors = inventors_section.get('inventor', [])
        if not isinstance(inventors, list):
            inventors = [inventors]
        
        seen_inventors = set()
        # First pass: collect original format inventors
        for inventor in inventors:
            if isinstance(inventor, dict):
                data_format = inventor.get('@data-format', '')
                if data_format == 'original':
                    name_obj = inventor.get('inventor-name', {})
                    if isinstance(name_obj, dict):
                        name = name_obj.get('name', {}).get('$', '')
                        normalized_name = normalize_inventor_name(name)
                        if normalized_name and normalized_name not in seen_inventors:
                            extracted['inventors'].append(normalized_name)
                            seen_inventors.add(normalized_name)
        
        # If no original format found, use epodoc format
        if not extracted['inventors']:
            for inventor in inventors:
                if isinstance(inventor, dict):
                    data_format = inventor.get('@data-format', '')
                    if data_format == 'epodoc':
                        name_obj = inventor.get('inventor-name', {})
                        if isinstance(name_obj, dict):
                            name = name_obj.get('name', {}).get('$', '')
                            normalized_name = normalize_inventor_name(name)
                            if normalized_name and normalized_name not in seen_inventors:
                                extracted['inventors'].append(normalized_name)
                                seen_inventors.add(normalized_name)
        
        # Extract priority claims
        priority_claims_section = biblio.get('priority-claims', {})
        priority_claims = priority_claims_section.get('priority-claim', [])
        if not isinstance(priority_claims, list):
            priority_claims = [priority_claims]
        
        for priority in priority_claims:
            if isinstance(priority, dict):
                doc_ids = priority.get('document-id', [])
                if isinstance(doc_ids, list):
                    for doc_id in doc_ids:
                        if doc_id.get('@document-id-type') == 'original':
                            doc_num = doc_id.get('doc-number', {}).get('$', '')
                            # Get date from epodoc format
                            date = ''
                            for did in doc_ids:
                                if did.get('@document-id-type') == 'epodoc':
                                    date = did.get('date', {}).get('$', '')
                                    break
                            
                            if doc_num and date:
                                if doc_num.startswith('102') and len(doc_num) == 12:  # German application
                                    priority_claim = f"DE{doc_num}A·{date[:4]}-{date[4:6]}-{date[6:8]}"
                                elif doc_num.startswith('EP'):
                                    priority_claim = f"{doc_num}W·{date[:4]}-{date[4:6]}-{date[6:8]}"
                                else:
                                    priority_claim = f"{doc_num}·{date[:4]}-{date[4:6]}-{date[6:8]}"
                                extracted['priority_claims'].append(priority_claim)
                            break
        
        # Extract IPC classifications
        ipc_section = biblio.get('classifications-ipcr', {})
        ipc_classifications = ipc_section.get('classification-ipcr', [])
        if not isinstance(ipc_classifications, list):
            ipc_classifications = [ipc_classifications]
        
        for ipc in ipc_classifications:
            if isinstance(ipc, dict):
                text_obj = ipc.get('text', {})
                if isinstance(text_obj, dict):
                    ipc_text = text_obj.get('$', '')
                    if ipc_text:
                        parts = ipc_text.split()
                        if len(parts) >= 2:
                            clean_ipc = f"{parts[0]}{parts[1]}"
                            extracted['ipc_classes'].append(clean_ipc)
        
        # Extract CPC classifications
        patent_classifications = biblio.get('patent-classifications', {})
        cpc_classifications = patent_classifications.get('patent-classification', [])
        if not isinstance(cpc_classifications, list):
            cpc_classifications = [cpc_classifications]
        
        for cpc in cpc_classifications:
            if isinstance(cpc, dict):
                scheme = cpc.get('classification-scheme', {})
                if scheme.get('@scheme') == 'CPCI':
                    section = cpc.get('section', {}).get('$', '')
                    class_code = cpc.get('class', {}).get('$', '')
                    subclass = cpc.get('subclass', {}).get('$', '')
                    main_group = cpc.get('main-group', {}).get('$', '')
                    subgroup = cpc.get('subgroup', {}).get('$', '')
                    
                    if all([section, class_code, subclass, main_group, subgroup]):
                        cpc_code = f"{section}{class_code}{subclass}{main_group}/{subgroup}"
                        extracted['cpc_classes'].append(cpc_code)
        
    except Exception as e:
        print(f"    ❌ Extraction error: {e}")
    
    return extracted

def main():
    # Initialize OPS client
    ops_client = EPOOPSClient()
    if not ops_client.get_access_token():
        print("🛑 Cannot proceed without authentication")
        return
    
    # Load TU Chemnitz patents
    print("\n📂 Loading TU Chemnitz patents...")
    try:
        patents_df = pd.read_csv('./output/patent_technology_list.csv')
        tu_chemnitz_patents = patents_df[patents_df['University'].str.contains('Chemnitz', case=False, na=False)]
        granted_patents = tu_chemnitz_patents[tu_chemnitz_patents['Patent_status'] == 'EP granted']
        
        print(f"✅ Found {len(tu_chemnitz_patents)} total TU Chemnitz patents")
        print(f"✅ Found {len(granted_patents)} granted patents for analysis")
        print(f"📅 Filing years: {granted_patents['Filing_Year'].min()} to {granted_patents['Filing_Year'].max()}")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Analyze each patent
    print(f"\n🔍 Analyzing {len(granted_patents)} granted patents...")
    
    all_applicants = set()
    all_inventors = set()
    german_priorities = []
    industry_collaborators = set()
    results = []
    failed_patents = []
    
    for idx, (_, row) in enumerate(granted_patents.iterrows(), 1):
        patent_number = row['EP_Patent_Number']
        print(f"  [{idx:2d}/{len(granted_patents)}] {patent_number}", end="")
        
        # Get bibliographic data
        biblio_data = ops_client.get_application_biblio(patent_number)
        
        if biblio_data:
            extracted = extract_patent_data(biblio_data)
            
            # Normalize and collect applicants
            normalized_applicants = [normalize_applicant_name(app) for app in extracted['applicants'] if normalize_applicant_name(app)]
            all_applicants.update(normalized_applicants)
            
            # Normalize and collect inventors
            normalized_inventors = [normalize_inventor_name(inv) for inv in extracted['inventors'] if normalize_inventor_name(inv)]
            all_inventors.update(normalized_inventors)
            
            # Check for German priorities
            for priority in extracted['priority_claims']:
                if priority.startswith('DE'):
                    german_priorities.append({
                        'ep_patent': patent_number,
                        'german_priority': priority,
                        'applicants': normalized_applicants
                    })
            
            # Identify industry collaborators (non-university applicants)
            university_terms = ['university', 'universität', 'technische', 'tu ', 'chemnitz']
            for applicant in normalized_applicants:
                if not any(term in applicant.lower() for term in university_terms):
                    industry_collaborators.add(applicant)
            
            # Store result
            result = {
                'ep_patent': patent_number,
                'filing_year': row['Filing_Year'],
                'technical_field': row['Technical_field'],
                'title': extracted['title'],
                'normalized_applicants': normalized_applicants,
                'normalized_inventors': normalized_inventors,
                'priority_claims': extracted['priority_claims'],
                'german_priorities': [p for p in extracted['priority_claims'] if p.startswith('DE')],
                'ipc_classes': extracted['ipc_classes'],
                'cpc_classes': extracted['cpc_classes'],
                'application_number': extracted['application_number'],
                'filing_date': extracted['filing_date']
            }
            results.append(result)
            print(f" ✅ ({len(normalized_applicants)} applicants, {len(normalized_inventors)} inventors)")
            
        else:
            failed_patents.append(patent_number)
            print(f" ❌ Not found")
        
        # Rate limiting
        time.sleep(2)
    
    # Generate summary
    print(f"\n📊 ANALYSIS COMPLETE")
    print(f"=" * 50)
    print(f"✅ Successfully processed: {len(results)}/{len(granted_patents)} patents")
    print(f"❌ Failed to retrieve: {len(failed_patents)} patents")
    
    if failed_patents:
        print(f"📋 Failed patents: {', '.join(failed_patents[:5])}{'...' if len(failed_patents) > 5 else ''}")
    
    print(f"\n🎯 KEY FINDINGS:")
    print(f"👥 Total unique applicants: {len(all_applicants)}")
    print(f"🔬 Total unique inventors: {len(all_inventors)}")
    print(f"🇩🇪 Patents with German priorities: {len(german_priorities)}")
    print(f"🤝 Industry collaborations: {len(industry_collaborators)}")
    
    print(f"\n👥 ALL APPLICANTS:")
    for applicant in sorted(all_applicants):
        print(f"  • {applicant}")
    
    print(f"\n🔬 ALL INVENTORS:")
    for inventor in sorted(all_inventors):
        print(f"  • {inventor}")
    
    if industry_collaborators:
        print(f"\n🤝 INDUSTRY COLLABORATORS:")
        for collaborator in sorted(industry_collaborators):
            print(f"  • {collaborator}")
    
    if german_priorities:
        print(f"\n🇩🇪 GERMAN PRIORITY PATENTS:")
        for gp in german_priorities:
            print(f"  {gp['german_priority']} → {gp['ep_patent']} | {', '.join(gp['applicants'])}")
    
    # Export results
    if results:
        # Export detailed results
        results_df = pd.DataFrame(results)
        results_file = "./output/tu_chemnitz_complete_analysis.csv"
        results_df.to_csv(results_file, index=False)
        print(f"\n💾 EXPORTS:")
        print(f"📄 Complete analysis: {results_file}")
        
        # Export applicant summary
        applicants_df = pd.DataFrame({
            'applicant': sorted(all_applicants),
            'type': ['University' if any(term in app.lower() for term in ['university', 'universität', 'technische', 'tu ', 'chemnitz']) 
                    else 'Industry/Other' for app in sorted(all_applicants)]
        })
        applicants_file = "./output/tu_chemnitz_applicants.csv"
        applicants_df.to_csv(applicants_file, index=False)
        print(f"👥 Applicant summary: {applicants_file}")
        
        # Export inventor summary
        inventors_df = pd.DataFrame({'inventor': sorted(all_inventors)})
        inventors_file = "./output/tu_chemnitz_inventors.csv"
        inventors_df.to_csv(inventors_file, index=False)
        print(f"🔬 Inventor list: {inventors_file}")
        
        # Export German priorities
        if german_priorities:
            priorities_df = pd.DataFrame(german_priorities)
            priorities_file = "./output/tu_chemnitz_german_priorities.csv"
            priorities_df.to_csv(priorities_file, index=False)
            print(f"🇩🇪 German priorities: {priorities_file}")
    
    print(f"\n✅ TU CHEMNITZ ANALYSIS COMPLETE!")
    print(f"🕐 Finished: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()