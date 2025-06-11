#!/usr/bin/env python3
"""
Test script for priority analysis of smallest university
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

# Data extraction function
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
    
    def deep_search(data, search_keys):
        results = []
        if isinstance(data, dict):
            for key, value in data.items():
                if any(search_key.lower() in key.lower() for search_key in search_keys):
                    results.append(value)
                if isinstance(value, (dict, list)):
                    results.extend(deep_search(value, search_keys))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    results.extend(deep_search(item, search_keys))
        return results
    
    try:
        # Extract applicants
        applicant_data = deep_search(biblio_data, ['applicant'])
        for app_item in applicant_data:
            if isinstance(app_item, dict):
                name = app_item.get('applicant-name', {})
                if isinstance(name, dict):
                    name_text = name.get('name', name.get('$', ''))
                else:
                    name_text = str(name)
                
                residence = app_item.get('residence', {})
                country = ''
                if isinstance(residence, dict):
                    country = residence.get('country', residence.get('@country', ''))
                
                if name_text:
                    full_name = f"{name_text} [{country}]" if country else name_text
                    extracted['applicants'].append(full_name)
        
        # Extract inventors
        inventor_data = deep_search(biblio_data, ['inventor'])
        for inv_item in inventor_data:
            if isinstance(inv_item, dict):
                name = inv_item.get('inventor-name', {})
                if isinstance(name, dict):
                    name_text = name.get('name', name.get('$', ''))
                else:
                    name_text = str(name)
                
                residence = inv_item.get('residence', {})
                country = ''
                if isinstance(residence, dict):
                    country = residence.get('country', residence.get('@country', ''))
                
                if name_text:
                    full_name = f"{name_text} [{country}]" if country else name_text
                    extracted['inventors'].append(full_name)
        
        # Extract priority claims
        priority_data = deep_search(biblio_data, ['priority-claim'])
        for priority_item in priority_data:
            if isinstance(priority_item, dict):
                country = priority_item.get('country', priority_item.get('@country', ''))
                doc_number = priority_item.get('doc-number', priority_item.get('@doc-number', ''))
                date = priority_item.get('date', priority_item.get('@date', ''))
                
                if doc_number:
                    priority_claim = f"{country}{doc_number}·{date}"
                    extracted['priority_claims'].append(priority_claim)
        
        # Extract application/publication references
        app_ref_data = deep_search(biblio_data, ['application-reference'])
        for app_ref in app_ref_data:
            if isinstance(app_ref, dict):
                doc_id = app_ref.get('document-id', {})
                if isinstance(doc_id, dict):
                    country = doc_id.get('country', doc_id.get('@country', ''))
                    doc_number = doc_id.get('doc-number', doc_id.get('@doc-number', ''))
                    kind = doc_id.get('kind', doc_id.get('@kind', ''))
                    date = doc_id.get('date', doc_id.get('@date', ''))
                    
                    if doc_number:
                        extracted['application_number'] = f"{country}{doc_number}{kind}".replace('None', '')
                        extracted['filing_date'] = date
        
        # Extract title
        title_data = deep_search(biblio_data, ['invention-title'])
        for title_item in title_data:
            if isinstance(title_item, str):
                extracted['title'] = title_item
                break
            elif isinstance(title_item, dict):
                title_text = title_item.get('$', title_item.get('#text', ''))
                if title_text:
                    extracted['title'] = title_text
                    break
        
        # Extract IPC classifications
        ipc_data = deep_search(biblio_data, ['classification-ipc', 'ipc'])
        for ipc_item in ipc_data:
            if isinstance(ipc_item, dict):
                # Try different possible text fields
                text = ipc_item.get('text', ipc_item.get('$', ipc_item.get('#text', str(ipc_item))))
                if text and isinstance(text, str):
                    extracted['ipc_classes'].append(text)
            elif isinstance(ipc_item, list):
                for item in ipc_item:
                    if isinstance(item, dict):
                        text = item.get('text', item.get('$', item.get('#text', str(item))))
                        if text and isinstance(text, str):
                            extracted['ipc_classes'].append(text)
            elif isinstance(ipc_item, str):
                extracted['ipc_classes'].append(ipc_item)
        
        # Extract CPC classifications  
        cpc_data = deep_search(biblio_data, ['classification-cpc', 'cpc'])
        for cpc_item in cpc_data:
            if isinstance(cpc_item, dict):
                text = cpc_item.get('text', cpc_item.get('$', cpc_item.get('#text', str(cpc_item))))
                if text and isinstance(text, str):
                    extracted['cpc_classes'].append(text)
            elif isinstance(cpc_item, list):
                for item in cpc_item:
                    if isinstance(item, dict):
                        text = item.get('text', item.get('$', item.get('#text', str(item))))
                        if text and isinstance(text, str):
                            extracted['cpc_classes'].append(text)
            elif isinstance(cpc_item, str):
                extracted['cpc_classes'].append(cpc_item)
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
    
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
            # Save raw response for debugging
            with open(f'./output/debug_{patent_number.replace("/", "_")}_response.json', 'w') as f:
                json.dump(biblio_data, f, indent=2)
            
            # Extract patent information
            extracted = extract_patent_data(biblio_data)
            
            print(f"  ✅ Data retrieved")
            print(f"  📋 Title: {extracted['title'][:50] if extracted['title'] else 'N/A'}...")
            print(f"  👥 Applicants: {len(extracted['applicants'])}")
            print(f"  🔬 Inventors: {len(extracted['inventors'])}")
            print(f"  🎯 Priority claims: {len(extracted['priority_claims'])}")
            print(f"  📚 IPC classes: {len(extracted['ipc_classes'])}")
            print(f"  📚 CPC classes: {len(extracted['cpc_classes'])}")
            
            # Debug: show top-level structure
            print(f"  🔍 Top-level keys: {list(biblio_data.keys())}")
            
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
                
        else:
            print(f"  ❌ No data retrieved")
        
        # Rate limiting
        time.sleep(3)
    
    # Summary
    print(f"\n📊 ANALYSIS COMPLETE")
    print(f"=" * 50)
    print(f"✅ Processed: {len(priority_results)}/{len(smallest_uni_patents)} patents")
    print(f"👥 Total unique applicants found: {len(all_applicants)}")
    
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