#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
from src.credentials import CredentialManager, Credentials

class TestCredentialManager(unittest.TestCase):
    def setUp(self):
        self.credential_manager = CredentialManager()
    
    def test_initial_state(self):
        """Test initial state of credential manager."""
        self.assertIsNone(self.credential_manager.get_credentials())
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_request_credentials(self, mock_getpass, mock_input):
        """Test requesting credentials from user."""
        # Mock user input
        mock_input.side_effect = [
            "https://exchange.example.com",
            "test-org",
            "test-user"
        ]
        mock_getpass.return_value = "test-api-key"
        
        # Request credentials
        credentials = self.credential_manager.request_credentials()
        
        # Verify credentials
        self.assertIsNotNone(credentials)
        self.assertEqual(credentials.exchange_url, "https://exchange.example.com")
        self.assertEqual(credentials.org_id, "test-org")
        self.assertEqual(credentials.username, "test-user")
        self.assertEqual(credentials.api_key, "test-api-key")
    
    def test_clear_credentials(self):
        """Test clearing credentials."""
        # Set some credentials
        self.credential_manager._credentials = Credentials(
            api_key="test-key",
            org_id="test-org",
            username="test-user",
            exchange_url="https://exchange.example.com"
        )
        
        # Clear credentials
        self.credential_manager.clear_credentials()
        
        # Verify credentials are cleared
        self.assertIsNone(self.credential_manager.get_credentials())
    
    def test_validate_credentials(self):
        """Test credential validation."""
        # Test with no credentials
        self.assertFalse(self.credential_manager.validate_credentials())
        
        # Test with valid credentials
        self.credential_manager._credentials = Credentials(
            api_key="test-key",
            org_id="test-org",
            username="test-user",
            exchange_url="https://exchange.example.com"
        )
        self.assertTrue(self.credential_manager.validate_credentials())
        
        # Test with invalid credentials (empty values)
        self.credential_manager._credentials = Credentials(
            api_key="",
            org_id="test-org",
            username="test-user",
            exchange_url="https://exchange.example.com"
        )
        self.assertFalse(self.credential_manager.validate_credentials())
    
    def test_get_headers(self):
        """Test getting API headers."""
        # Set credentials
        self.credential_manager._credentials = Credentials(
            api_key="test-key",
            org_id="test-org",
            username="test-user",
            exchange_url="https://exchange.example.com"
        )
        
        # Get headers
        headers = self.credential_manager.get_headers()
        
        # Verify headers
        self.assertEqual(headers["Authorization"], "Basic test-key")
        self.assertEqual(headers["Content-Type"], "application/json")
        
        # Test with no credentials
        self.credential_manager.clear_credentials()
        with self.assertRaises(ValueError):
            self.credential_manager.get_headers()
    
    def test_get_base_url(self):
        """Test getting base URL."""
        # Set credentials
        self.credential_manager._credentials = Credentials(
            api_key="test-key",
            org_id="test-org",
            username="test-user",
            exchange_url="https://exchange.example.com/"
        )
        
        # Get base URL
        base_url = self.credential_manager.get_base_url()
        
        # Verify base URL
        self.assertEqual(base_url, "https://exchange.example.com")
        
        # Test with no credentials
        self.credential_manager.clear_credentials()
        with self.assertRaises(ValueError):
            self.credential_manager.get_base_url()

if __name__ == '__main__':
    unittest.main() 