"""
EPO OPS API client for patent data extraction.
Based on proven working patterns from legacy analysis scripts.
"""

import requests
import time
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import os

from ...core.config import config
from ...core.exceptions import EPOOPSError, AuthenticationError, RateLimitError
from ..load.data_models import EPOOPSResponse

class EPOOPSClient:
    """
    Client for EPO OPS API with authentication and rate limiting.
    Implements proven patterns from legacy tu_dresden_analysis.py.
    """
    
    def __init__(self):
        self.base_url = config.epo_ops.base_url
        self.auth_url = config.epo_ops.auth_url
        self.timeout = config.epo_ops.timeout_seconds
        self.rate_limit = config.epo_ops.rate_limit_seconds
        self.access_token = None
        
        # Load credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load EPO OPS credentials from environment file."""
        try:
            credentials_path = config.get_credentials_path()
            load_dotenv(credentials_path)
            
            self.consumer_key = os.getenv('OPS_KEY')
            self.consumer_secret = os.getenv('OPS_SECRET')
            
            if not self.consumer_key or not self.consumer_secret:
                raise AuthenticationError(
                    f"EPO OPS credentials not found in {credentials_path}. "
                    "Please ensure OPS_KEY and OPS_SECRET are set."
                )
                
        except Exception as e:
            raise AuthenticationError(f"Failed to load EPO OPS credentials: {e}")
    
    def get_access_token(self) -> bool:
        """
        Authenticate with EPO OPS and get access token.
        Returns True if successful, False otherwise.
        """
        try:
            response = requests.post(
                self.auth_url,
                data={'grant_type': 'client_credentials'},
                auth=(self.consumer_key, self.consumer_secret),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                print(f"✅ EPO OPS authenticated (expires in {token_data.get('expires_in', 'unknown')}s)")
                return True
            else:
                raise AuthenticationError(f"Authentication failed with status {response.status_code}")
                
        except Exception as e:
            raise AuthenticationError(f"Authentication error: {e}")
    
    def format_patent_number(self, patent_number: str) -> str:
        """
        Format patent number for EPO OPS API calls.
        Implements proven logic from legacy scripts.
        """
        clean_number = patent_number.replace('EP', '').replace('A', '').replace('B', '')
        
        # Leading zero handling for different patent eras (critical for 2000s patents)
        if clean_number.startswith('0') and len(clean_number) == 8:
            return clean_number  # Keep leading zero for 2000s patents
        elif clean_number.startswith('00'):
            return clean_number.lstrip('0')
        else:
            return clean_number.lstrip('0') if clean_number.lstrip('0') else clean_number
    
    def get_application_biblio(self, patent_number: str) -> EPOOPSResponse:
        """
        Get bibliographic data for a patent application.
        Uses proven endpoint and header configuration.
        """
        if not self.access_token:
            if not self.get_access_token():
                return EPOOPSResponse(
                    ep_number=patent_number,
                    status_code=401,
                    error_message="Authentication failed"
                )
        
        clean_number = self.format_patent_number(patent_number)
        
        # Try multiple formats (proven fallback strategy)
        formats_to_try = [
            f"published-data/application/epodoc/EP{clean_number}/biblio",
            f"published-data/application/epodoc/EP{clean_number.lstrip('0')}/biblio"
        ]
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'  # CRITICAL: Required for proper JSON response
        }
        
        for endpoint in formats_to_try:
            url = f"{self.base_url}/{endpoint}"
            
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    return EPOOPSResponse(
                        ep_number=patent_number,
                        status_code=200,
                        response_data=response.json()
                    )
                elif response.status_code == 404:
                    continue  # Try next format
                elif response.status_code == 429:
                    raise RateLimitError("EPO OPS rate limit exceeded")
                else:
                    return EPOOPSResponse(
                        ep_number=patent_number,
                        status_code=response.status_code,
                        error_message=f"API error {response.status_code}"
                    )
                    
            except requests.RequestException as e:
                return EPOOPSResponse(
                    ep_number=patent_number,
                    status_code=0,
                    error_message=f"Request failed: {e}"
                )
        
        # All formats failed
        return EPOOPSResponse(
            ep_number=patent_number,
            status_code=404,
            error_message="Patent not found with any format"
        )
    
    def fetch_with_rate_limit(self, patent_number: str) -> EPOOPSResponse:
        """
        Fetch patent data with automatic rate limiting.
        Implements EPO OPS compliant delays.
        """
        response = self.get_application_biblio(patent_number)
        
        # Apply rate limiting after each request
        time.sleep(self.rate_limit)
        
        return response
    
    def test_connection(self, test_patent: str = "EP19196837A") -> bool:
        """
        Test EPO OPS connection with a known working patent.
        Returns True if connection is working.
        """
        try:
            response = self.get_application_biblio(test_patent)
            return response.status_code == 200
        except Exception:
            return False