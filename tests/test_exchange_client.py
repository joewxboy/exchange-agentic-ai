#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import requests
from src.exchange_client import ExchangeAPIClient, ExchangeAPIError
from src.credentials import CredentialManager, Credentials

class TestExchangeAPIClient(unittest.TestCase):
    def setUp(self):
        self.credential_manager = CredentialManager()
        self.credential_manager._credentials = Credentials(
            api_key="test-key",
            org_id="test-org",
            username="test-user",
            exchange_url="https://exchange.example.com"
        )
        self.client = ExchangeAPIClient(self.credential_manager)
    
    def tearDown(self):
        self.client.close()
    
    @patch('src.exchange_client.ExchangeAPIClient.session', new_callable=PropertyMock)
    def test_list_organizations(self, mock_session):
        """Test listing organizations."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "org1"}, {"id": "org2"}]
        mock_session.return_value.request.return_value = mock_response
        
        # Test
        orgs = self.client.list_organizations()
        
        # Verify
        self.assertEqual(len(orgs), 2)
        self.assertEqual(orgs[0]["id"], "org1")
        self.assertEqual(orgs[1]["id"], "org2")
        
        # Verify request was made correctly
        mock_session.return_value.request.assert_called_once_with(
            method="GET",
            url="https://exchange.example.com/orgs",
            headers={
                "Authorization": "Basic test-key",
                "Content-Type": "application/json"
            },
            json=None
        )
    
    @patch('src.exchange_client.ExchangeAPIClient.session', new_callable=PropertyMock)
    def test_get_organization(self, mock_session):
        """Test getting organization details."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "test-org", "name": "Test Org"}
        mock_session.return_value.request.return_value = mock_response
        
        # Test
        org = self.client.get_organization("test-org")
        
        # Verify
        self.assertEqual(org["id"], "test-org")
        self.assertEqual(org["name"], "Test Org")
        
        # Verify request was made correctly
        mock_session.return_value.request.assert_called_once_with(
            method="GET",
            url="https://exchange.example.com/orgs/test-org",
            headers={
                "Authorization": "Basic test-key",
                "Content-Type": "application/json"
            },
            json=None
        )
    
    @patch('src.exchange_client.ExchangeAPIClient.session', new_callable=PropertyMock)
    def test_list_services(self, mock_session):
        """Test listing services."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "service1"}, {"id": "service2"}]
        mock_session.return_value.request.return_value = mock_response
        
        # Test
        services = self.client.list_services("test-org")
        
        # Verify
        self.assertEqual(len(services), 2)
        self.assertEqual(services[0]["id"], "service1")
        self.assertEqual(services[1]["id"], "service2")
        
        # Verify request was made correctly
        mock_session.return_value.request.assert_called_once_with(
            method="GET",
            url="https://exchange.example.com/orgs/test-org/services",
            headers={
                "Authorization": "Basic test-key",
                "Content-Type": "application/json"
            },
            json=None
        )
    
    @patch('src.exchange_client.ExchangeAPIClient.session', new_callable=PropertyMock)
    def test_create_service(self, mock_session):
        """Test creating a service."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "new-service", "name": "New Service"}
        mock_session.return_value.request.return_value = mock_response
        
        # Test
        service_data = {"name": "New Service", "version": "1.0.0"}
        service = self.client.create_service("test-org", service_data)
        
        # Verify
        self.assertEqual(service["id"], "new-service")
        self.assertEqual(service["name"], "New Service")
        
        # Verify request was made correctly
        mock_session.return_value.request.assert_called_once_with(
            method="POST",
            url="https://exchange.example.com/orgs/test-org/services",
            headers={
                "Authorization": "Basic test-key",
                "Content-Type": "application/json"
            },
            json=service_data
        )
    
    @patch('src.exchange_client.ExchangeAPIClient.session', new_callable=PropertyMock)
    def test_list_patterns(self, mock_session):
        """Test listing patterns."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "pattern1"}, {"id": "pattern2"}]
        mock_session.return_value.request.return_value = mock_response
        
        # Test
        patterns = self.client.list_patterns("test-org")
        
        # Verify
        self.assertEqual(len(patterns), 2)
        self.assertEqual(patterns[0]["id"], "pattern1")
        self.assertEqual(patterns[1]["id"], "pattern2")
        
        # Verify request was made correctly
        mock_session.return_value.request.assert_called_once_with(
            method="GET",
            url="https://exchange.example.com/orgs/test-org/patterns",
            headers={
                "Authorization": "Basic test-key",
                "Content-Type": "application/json"
            },
            json=None
        )
    
    @patch('src.exchange_client.ExchangeAPIClient.session', new_callable=PropertyMock)
    def test_list_nodes(self, mock_session):
        """Test listing nodes."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": "node1"}, {"id": "node2"}]
        mock_session.return_value.request.return_value = mock_response
        
        # Test
        nodes = self.client.list_nodes("test-org")
        
        # Verify
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes[0]["id"], "node1")
        self.assertEqual(nodes[1]["id"], "node2")
        
        # Verify request was made correctly
        mock_session.return_value.request.assert_called_once_with(
            method="GET",
            url="https://exchange.example.com/orgs/test-org/nodes",
            headers={
                "Authorization": "Basic test-key",
                "Content-Type": "application/json"
            },
            json=None
        )
    
    def test_invalid_credentials(self):
        """Test behavior with invalid credentials."""
        self.credential_manager.clear_credentials()
        with self.assertRaises(ExchangeAPIError):
            self.client.list_organizations()
    
    @patch('src.exchange_client.ExchangeAPIClient.session', new_callable=PropertyMock)
    def test_api_error_handling(self, mock_session):
        """Test handling of API errors."""
        # Mock response with error
        mock_session.return_value.request.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        # Test
        with self.assertRaises(ExchangeAPIError):
            self.client.list_organizations()

if __name__ == '__main__':
    unittest.main() 