"""
Open Horizon Exchange API Client implementation.
"""
import os
import requests
import base64
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from urllib.parse import quote
import aiohttp

class ExchangeAPIClient:
    """Client for interacting with the Open Horizon Exchange API."""
    
    def __init__(self):
        self.org_id = os.getenv('HZN_ORG_ID')
        self.user_auth = os.getenv('HZN_EXCHANGE_USER_AUTH')
        self.exchange_url = os.getenv('HZN_EXCHANGE_URL')
        self.css_url = os.getenv('HZN_FSS_CSSURL')
        self.agbot_url = os.getenv('HZN_AGBOT_URL')
        self.fdo_url = os.getenv('HZN_FDO_SVC_URL')
        
        # Properly encode credentials for Basic Auth
        if self.user_auth and self.org_id:
            # Split and only URL encode the username
            username, password = self.user_auth.split(':')
            encoded_username = quote(username)
            
            # Use original password without encoding
            auth_string = f"{self.org_id}/{encoded_username}:{password}"
            auth_bytes = auth_string.encode('ascii')
            base64_auth = base64.b64encode(auth_bytes).decode('ascii')
            
            self.headers = {
                'Authorization': f'Basic {base64_auth}',
                'Content-Type': 'application/json'
            }
        else:
            raise ValueError("Missing required environment variables: HZN_ORG_ID or HZN_EXCHANGE_USER_AUTH")
    
    async def _make_request(self, method, endpoint, data=None):
        """Make an HTTP request to the Exchange API"""
        url = f"{self.exchange_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            print(f"Making {method} request to: {url}")
            print(f"Headers: {self.headers}")
            
            async with aiohttp.ClientSession() as session:
                async with session.request(method=method, url=url, headers=self.headers, json=data) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    print(f"Response text: {response_text}")
                    return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error making request to {url}: {str(e)}")
            return None

    async def get_services(self):
        """Get all services in the organization"""
        return await self._make_request('GET', f'orgs/{self.org_id}/services')
    
    async def get_service(self, service_id: str) -> Dict[str, Any]:
        """Get details for a specific service."""
        return await self._make_request('GET', f'orgs/{self.org_id}/services/{service_id}') 