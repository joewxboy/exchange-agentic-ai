#!/usr/bin/env python3

import os
import getpass
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import base64

@dataclass
class Credentials:
    """Class for storing API credentials."""
    api_key: str
    org_id: str
    username: str
    exchange_url: str
    expires_at: Optional[datetime] = None

class CredentialManager:
    """Manages API credentials with secure storage and validation."""
    
    def __init__(self):
        self._credentials: Optional[Credentials] = None
        self._env_prefix = "HZN_"
    
    def request_credentials(self) -> Credentials:
        """Securely request credentials from the user."""
        print("\nPlease provide your Open Horizon Exchange credentials:")
        
        # Get exchange URL
        exchange_url = input("Exchange URL (e.g., https://exchange.example.com): ").strip()
        while not exchange_url.startswith(('http://', 'https://')):
            print("Error: URL must start with http:// or https://")
            exchange_url = input("Exchange URL: ").strip()
        
        # Get organization ID
        org_id = input("Organization ID: ").strip()
        while not org_id:
            print("Error: Organization ID cannot be empty")
            org_id = input("Organization ID: ").strip()
        
        # Get username
        username = input("Username: ").strip()
        while not username:
            print("Error: Username cannot be empty")
            username = input("Username: ").strip()
        
        # Get API key securely
        api_key = getpass.getpass("API Key: ").strip()
        while not api_key:
            print("Error: API key cannot be empty")
            api_key = getpass.getpass("API Key: ").strip()
        
        # Create credentials object
        self._credentials = Credentials(
            api_key=api_key,
            org_id=org_id,
            username=username,
            exchange_url=exchange_url
        )
        
        return self._credentials
    
    def get_credentials(self) -> Optional[Credentials]:
        """Get the current credentials."""
        return self._credentials
    
    def clear_credentials(self):
        """Clear stored credentials."""
        self._credentials = None
    
    def validate_credentials(self) -> bool:
        """Validate the current credentials."""
        if not self._credentials:
            return False
        
        # TODO: Implement actual API validation
        # For now, just check if the credentials are not empty
        return bool(
            self._credentials.api_key and
            self._credentials.org_id and
            self._credentials.username and
            self._credentials.exchange_url
        )
    
    def get_headers(self, method: str = "GET") -> Dict[str, str]:
        """Get headers for API requests."""
        if not self._credentials:
            raise ValueError("No credentials available")
        
        # Match exactly how curl handles Basic Auth
        auth_string = f"{self._credentials.org_id}/{self._credentials.username}:{self._credentials.api_key}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "User-Agent": "curl/7.64.1"
        }
        if method != "GET":
            headers["Content-Type"] = "application/json"
        return headers
    
    def get_base_url(self) -> str:
        """Get the base URL for API requests."""
        if not self._credentials:
            raise ValueError("No credentials available")
        
        return self._credentials.exchange_url 