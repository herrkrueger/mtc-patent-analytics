#!/usr/bin/env python3
"""
Fixed test script for priority analysis
"""

import pandas as pd
import requests
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Load credentials
load_dotenv('../ipc-ops/.env')
ops_key = os.getenv('OPS_KEY')
ops_secret = os.getenv('OPS_SECRET')

print("📚 Libraries loaded")
print(f"🕐 Started: {datetime.now().strftime('%H:%M:%S')}")

# EPO OPS Client
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
                print(f"✅ Authentication successful (expires in {token_data.get('expires_in', 'unknown')}s)")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def format_patent_number(self, patent_number):
        clean_number = patent_number.replace('EP', '').replace('A', '').replace('B', '').lstrip('0')
        return clean_number
    
    def get_application_biblio(self, patent_number):
        if not self.access_token:
            return None
        
        clean_number = self.format_patent_number(patent_number)
        endpoint = f"published-data/application/epodoc/EP{clean_number}/biblio"
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"⚠️ Patent {patent_number} not found (404)")
                return None
            else:
                print(f"❌ Error {response.status_code} for {patent_number}")
                return None
        except Exception as e:
            print(f"❌ Request failed for {patent_number}: {e}")
            return None

# Improved data extraction function
def extract_patent_data(biblio_data):
    extracted = {
        'application_number': None,
        'filing_date': None,
        'publication_number': None,
        'publication_date': None,
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
        # Navigate to bibliographic data
        world_data = biblio_data.get('ops:world-patent-data', {})
        exchange_docs = world_data.get('exchange-documents', {})
        exchange_doc = exchange_docs.get('exchange-document', [])
        
        if isinstance(exchange_doc, list) and len(exchange_doc) > 0:
            doc = exchange_doc[0]
        elif isinstance(exchange_doc, dict):
            doc = exchange_doc
        else:
            print("  ⚠️ No exchange document found")
            return extracted
        
        biblio = doc.get('bibliographic-data', {})
        
        # Extract publication reference
        pub_ref = biblio.get('publication-reference', {})
        if pub_ref:
            doc_ids = pub_ref.get('document-id', [])
            if isinstance(doc_ids, list):
                for doc_id in doc_ids:
                    if doc_id.get('@document-id-type') == 'epodoc':
                        doc_num = doc_id.get('doc-number', {}).get('$', '')
                        date = doc_id.get('date', {}).get('$', '')
                        extracted['publication_number'] = doc_num
                        extracted['publication_date'] = date
                        break
        
        # Extract application reference
        app_ref = biblio.get('application-reference', {})
        if app_ref:
            doc_ids = app_ref.get('document-id', [])
            if isinstance(doc_ids, list):
                for doc_id in doc_ids:
                    if doc_id.get('@document-id-type') == 'epodoc':
                        country = doc_id.get('country', {}).get('$', '')
                        doc_num = doc_id.get('doc-number', {}).get('$', '')
                        kind = doc_id.get('kind', {}).get('$', '')
                        date = doc_id.get('date', {}).get('$', '')
                        extracted['application_number'] = f"{country}{doc_num}{kind}"
                        extracted['filing_date'] = date
                        break
        
        # Extract title
        titles = biblio.get('invention-title', [])
        if isinstance(titles, list) and len(titles) > 0:
            title_obj = titles[0]
            if isinstance(title_obj, dict):
                extracted['title'] = title_obj.get('$', str(title_obj))
            else:
                extracted['title'] = str(title_obj)
        elif isinstance(titles, dict):
            extracted['title'] = titles.get('$', str(titles))
        
        # Extract applicants
        parties = biblio.get('parties', {})
        applicants = parties.get('applicants', {}).get('applicant', [])
        if not isinstance(applicants, list):
            applicants = [applicants]
        
        for applicant in applicants:
            if isinstance(applicant, dict):
                name_obj = applicant.get('applicant-name', {})
                if isinstance(name_obj, dict):
                    name = name_obj.get('name', {}).get('$', '')
                else:
                    name = str(name_obj)
                
                residence = applicant.get('residence', {})
                country = ''
                if isinstance(residence, dict):
                    country_obj = residence.get('country', {})
                    if isinstance(country_obj, dict):
                        country = country_obj.get('$', '')
                    else:
                        country = str(country_obj)
                
                if name:
                    full_name = f"{name} [{country}]" if country else name
                    extracted['applicants'].append(full_name)
        
        # Extract inventors
        inventors = parties.get('inventors', {}).get('inventor', [])
        if not isinstance(inventors, list):
            inventors = [inventors]
        
        for inventor in inventors:
            if isinstance(inventor, dict):
                name_obj = inventor.get('inventor-name', {})
                if isinstance(name_obj, dict):
                    name = name_obj.get('name', {}).get('$', '')
                else:
                    name = str(name_obj)
                
                residence = inventor.get('residence', {})
                country = ''
                if isinstance(residence, dict):
                    country_obj = residence.get('country', {})
                    if isinstance(country_obj, dict):
                        country = country_obj.get('$', '')
                    else:
                        country = str(country_obj)
                
                if name:
                    full_name = f"{name} [{country}]" if country else name
                    extracted['inventors'].append(full_name)
        
        # Extract priority claims
        priority_claims = biblio.get('priority-claims', {}).get('priority-claim', [])
        if not isinstance(priority_claims, list):
            priority_claims = [priority_claims]
        
        for priority in priority_claims:
            if isinstance(priority, dict):
                doc_id = priority.get('document-id', {})
                if isinstance(doc_id, dict):
                    country = doc_id.get('country', {}).get('$', '')
                    doc_num = doc_id.get('doc-number', {}).get('$', '')
                    date = doc_id.get('date', {}).get('$', '')
                    
                    if doc_num:
                        priority_claim = f"{country}{doc_num}·{date}"
                        extracted['priority_claims'].append(priority_claim)
        
        # Extract IPC classifications
        ipc_data = biblio.get('classifications-ipcr', {})
        ipc_classifications = ipc_data.get('classification-ipcr', [])
        if not isinstance(ipc_classifications, list):
            ipc_classifications = [ipc_classifications]
        
        for ipc in ipc_classifications:
            if isinstance(ipc, dict):
                text_obj = ipc.get('text', {})
                if isinstance(text_obj, dict):
                    ipc_text = text_obj.get('$', '')
                    if ipc_text:
                        # Clean up IPC text (remove extra spaces)
                        clean_ipc = ' '.join(ipc_text.split())
                        extracted['ipc_classes'].append(clean_ipc)
        
        # Extract CPC classifications
        cpc_data = biblio.get('classifications-cpc', {})
        if cpc_data:
            cpc_classifications = cpc_data.get('classification-cpc', [])
            if not isinstance(cpc_classifications, list):
                cpc_classifications = [cpc_classifications]
            
            for cpc in cpc_classifications:
                if isinstance(cpc, dict):
                    text_obj = cpc.get('text', {})
                    if isinstance(text_obj, dict):
                        cpc_text = text_obj.get('$', '')
                        if cpc_text:
                            clean_cpc = ' '.join(cpc_text.split())
                            extracted['cpc_classes'].append(clean_cpc)
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()
    
    return extracted

# Main execution
def main():
    print("🔐 Initializing OPS client...")
    ops_client = EPOOPSClient()
    
    if not ops_client.get_access_token():
        print("🛑 Cannot proceed without authentication")
        return
    
    print("📂 Loading patent data...")
    try:
        patents_df = pd.read_csv('./output/patent_technology_list.csv')
        granted_patents = patents_df[patents_df['Patent_status'] == 'EP granted']
        print(f"✅ Loaded {len(granted_patents):,} granted patents")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Find university with smallest number of applications
    uni_counts = granted_patents.groupby('University').size().sort_values()
    print(f"\n📊 Universities by patent count (smallest first):")
    for i, (uni, count) in enumerate(uni_counts.head().items()):
        print(f"  {i+1}. {uni}: {count} patents")
    
    # Try universities with recent patents (better OPS coverage)
    for uni, count in uni_counts.items():
        uni_patents = granted_patents[granted_patents['University'] == uni]
        recent_patents = uni_patents[uni_patents['Filing_Year'] >= 2010]
        if len(recent_patents) >= 1 and count <= 5:  # Small university with recent patents
            smallest_uni = uni
            smallest_uni_patents = uni_patents
            break
    else:
        # Fallback to smallest university
        smallest_uni = uni_counts.index[0]
        smallest_uni_patents = granted_patents[granted_patents['University'] == smallest_uni]
    
    print(f"\n🎯 Target University: {smallest_uni}")
    print(f"📊 Number of granted patents: {len(smallest_uni_patents)}")
    print(f"\n📋 Patents:")
    for idx, row in smallest_uni_patents.iterrows():
        print(f"  - {row['EP_Patent_Number']} ({row['Filing_Year']}) - {row['Technical_field']}")
    
    print(f"\n🔧 Starting priority analysis for {len(smallest_uni_patents)} patents...")
    
    # Analyze each patent
    priority_results = []
    all_applicants = set()
    
    for idx, row in smallest_uni_patents.iterrows():
        patent_number = row['EP_Patent_Number']
        print(f"\n🔍 Analyzing {patent_number}...")
        
        # Get bibliographic data
        biblio_data = ops_client.get_application_biblio(patent_number)
        
        if biblio_data:
            # Extract patent information
            extracted = extract_patent_data(biblio_data)
            
            print(f"  ✅ Data retrieved")
            print(f"  📋 Title: {extracted['title'][:50] if extracted['title'] else 'N/A'}...")
            print(f"  👥 Applicants: {len(extracted['applicants'])}")
            print(f"  🔬 Inventors: {len(extracted['inventors'])}")
            print(f"  🎯 Priority claims: {len(extracted['priority_claims'])}")
            print(f"  📚 IPC classes: {len(extracted['ipc_classes'])}")
            print(f"  📚 CPC classes: {len(extracted['cpc_classes'])}")
            
            # Collect unique applicants
            for applicant in extracted['applicants']:
                all_applicants.add(applicant)
            
            # Store results
            result = {
                'ep_patent': patent_number,
                'filing_year': row['Filing_Year'],
                'technical_field': row['Technical_field'],
                'title': extracted['title'],
                'applicants': extracted['applicants'],
                'inventors': extracted['inventors'],
                'priority_claims': extracted['priority_claims'],
                'ipc_classes': extracted['ipc_classes'],
                'cpc_classes': extracted['cpc_classes'],
                'application_number': extracted['application_number'],
                'filing_date': extracted['filing_date']
            }
            priority_results.append(result)
            
            # Show priority details
            if extracted['priority_claims']:
                for priority in extracted['priority_claims']:
                    print(f"    🎯 Priority: {priority}")
            else:
                print(f"    🎯 Priority: None found")
            
            # Show applicants
            for applicant in extracted['applicants']:
                print(f"    👤 Applicant: {applicant}")
            
            # Show IPC classes
            for ipc in extracted['ipc_classes']:
                print(f"    📚 IPC: {ipc}")
                
        else:
            print(f"  ❌ No data retrieved")
        
        # Rate limiting
        time.sleep(3)
    
    # Summary
    print(f"\n📊 ANALYSIS COMPLETE")
    print(f"=" * 50)
    print(f"✅ Processed: {len(priority_results)}/{len(smallest_uni_patents)} patents")
    print(f"👥 Total unique applicants found: {len(all_applicants)}")
    
    if all_applicants:
        print(f"\n👥 ALL UNIQUE APPLICANTS FOUND:")
        for i, applicant in enumerate(sorted(all_applicants), 1):
            print(f"  {i}. {applicant}")
    
    print(f"\n📋 DETAILED PATENT INFORMATION:")
    for result in priority_results:
        print(f"\n📄 {result['ep_patent']} ({result['filing_year']})")
        print(f"   Title: {result['title'][:80] if result['title'] else 'N/A'}...")
        print(f"   Technical Field: {result['technical_field']}")
        
        if result['applicants']:
            print(f"   Applicants:")
            for app in result['applicants']:
                print(f"     - {app}")
        
        if result['priority_claims']:
            print(f"   Priority Claims:")
            for priority in result['priority_claims']:
                print(f"     - {priority}")
        else:
            print(f"   Priority Claims: None found")
        
        if result['ipc_classes']:
            print(f"   IPC Classes: {', '.join(result['ipc_classes'][:3])}{'...' if len(result['ipc_classes']) > 3 else ''}")
        
        if result['cpc_classes']:
            print(f"   CPC Classes: {', '.join(result['cpc_classes'][:3])}{'...' if len(result['cpc_classes']) > 3 else ''}")
    
    # Save results
    if priority_results:
        results_df = pd.DataFrame(priority_results)
        output_file = f"./output/{smallest_uni.replace(' ', '_').replace('/', '_')}_priority_analysis.csv"
        results_df.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
    
    print(f"\n✅ Priority analysis complete!")

if __name__ == "__main__":
    main()