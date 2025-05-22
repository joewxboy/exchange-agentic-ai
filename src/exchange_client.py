#!/usr/bin/env python3

import json
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from .credentials import CredentialManager

class ExchangeAPIError(Exception):
    """Base exception for Exchange API errors."""
    pass

class ExchangeAPIClient:
    """Client for interacting with the Open Horizon Exchange API."""
    
    def __init__(self, credential_manager: CredentialManager):
        self.credential_manager = credential_manager
        self._session = None
    
    @property
    def session(self):
        """Get or create a session."""
        if self._session is None:
            self._session = requests.Session()
        return self._session
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make an API request with proper error handling."""
        if not self.credential_manager.validate_credentials():
            raise ExchangeAPIError("Invalid credentials")
        
        # Use the base_url exactly as provided, only ensure one slash between base_url and endpoint
        base_url = self.credential_manager.get_base_url().rstrip('/')
        endpoint = endpoint.lstrip('/')
        url = f"{base_url}/{endpoint}"
        headers = self.credential_manager.get_headers(method=method)
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # If the response has a JSON body, return it even for error codes
            if e.response is not None:
                try:
                    return e.response.json()
                except Exception:
                    pass
            raise ExchangeAPIError(f"API request failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ExchangeAPIError(f"API request failed: {str(e)}")
    
    # Organization endpoints
    def list_organizations(self) -> List[Dict]:
        """Get a list of all organizations."""
        return self._make_request("GET", "/orgs")
    
    def get_organization(self, org_id: str) -> Dict:
        """Get details of a specific organization."""
        return self._make_request("GET", f"/orgs/{org_id}")
    
    # Service endpoints
    def list_services(self, org_id: str) -> List[Dict]:
        """Get a list of services in an organization."""
        return self._make_request("GET", f"/orgs/{org_id}/services")
    
    def get_service(self, org_id: str, service: str) -> Dict:
        """Get details of a specific service."""
        return self._make_request("GET", f"/orgs/{org_id}/services/{service}")
    
    def create_service(self, org_id: str, service_data: Dict) -> Dict:
        """Create a new service."""
        return self._make_request("POST", f"/orgs/{org_id}/services", data=service_data)
    
    def update_service(self, org_id: str, service: str, service_data: Dict) -> Dict:
        """Update an existing service."""
        return self._make_request("PUT", f"/orgs/{org_id}/services/{service}", data=service_data)
    
    def delete_service(self, org_id: str, service: str) -> Dict:
        """Delete a service."""
        return self._make_request("DELETE", f"/orgs/{org_id}/services/{service}")
    
    # Pattern endpoints
    def list_patterns(self, org_id: str) -> List[Dict]:
        """Get a list of patterns in an organization."""
        return self._make_request("GET", f"/orgs/{org_id}/patterns")
    
    def get_pattern(self, org_id: str, pattern: str) -> Dict:
        """Get details of a specific pattern."""
        return self._make_request("GET", f"/orgs/{org_id}/patterns/{pattern}")
    
    def create_pattern(self, org_id: str, pattern_data: Dict) -> Dict:
        """Create a new pattern."""
        return self._make_request("POST", f"/orgs/{org_id}/patterns", data=pattern_data)
    
    def update_pattern(self, org_id: str, pattern: str, pattern_data: Dict) -> Dict:
        """Update an existing pattern."""
        return self._make_request("PUT", f"/orgs/{org_id}/patterns/{pattern}", data=pattern_data)
    
    def delete_pattern(self, org_id: str, pattern: str) -> Dict:
        """Delete a pattern."""
        return self._make_request("DELETE", f"/orgs/{org_id}/patterns/{pattern}")
    
    # Node endpoints
    def list_nodes(self, org_id: str) -> List[Dict]:
        """Get a list of nodes in an organization."""
        return self._make_request("GET", f"/orgs/{org_id}/nodes")
    
    def get_node(self, org_id: str, node_id: str) -> Dict:
        """Get details of a specific node."""
        return self._make_request("GET", f"/orgs/{org_id}/nodes/{node_id}")
    
    def create_node(self, org_id: str, node_data: Dict) -> Dict:
        """Create a new node."""
        return self._make_request("POST", f"/orgs/{org_id}/nodes", data=node_data)
    
    def update_node(self, org_id: str, node_id: str, node_data: Dict) -> Dict:
        """Update an existing node."""
        return self._make_request("PUT", f"/orgs/{org_id}/nodes/{node_id}", data=node_data)
    
    def delete_node(self, org_id: str, node_id: str) -> Dict:
        """Delete a node."""
        return self._make_request("DELETE", f"/orgs/{org_id}/nodes/{node_id}")
    
    def close(self):
        """Close the API client session."""
        if self._session is not None:
            self._session.close()
            self._session = None 