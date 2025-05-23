#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from src.services import ServiceManager, ServiceDefinition

class TestServiceManager(unittest.TestCase):
    """Test cases for the ServiceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.service_manager = ServiceManager(self.mock_client)
        
        # Sample valid service data
        self.valid_service_data = {
            'owner': 'test-org/test-user',
            'label': 'Test Service',
            'description': 'A test service',
            'public': True,
            'documentation': 'https://example.com/docs',
            'url': 'test-service',
            'version': '1.0.0',
            'arch': 'amd64',
            'sharable': 'singleton',
            'matchHardware': {},
            'requiredServices': [],
            'userInput': [],
            'deployment': {
                'services': {
                    'test-service': {
                        'image': 'test-image:latest'
                    }
                }
            }
        }
    
    def test_validate_service_data_valid(self):
        """Test validation of valid service data."""
        self.assertTrue(self.service_manager.validate_service_data(self.valid_service_data))
    
    def test_validate_service_data_missing_field(self):
        """Test validation of service data with missing required field."""
        invalid_data = self.valid_service_data.copy()
        del invalid_data['owner']
        
        with self.assertRaises(ValueError) as context:
            self.service_manager.validate_service_data(invalid_data)
        
        self.assertIn('Missing required field: owner', str(context.exception))
    
    def test_validate_service_data_invalid_version(self):
        """Test validation of service data with invalid version."""
        invalid_data = self.valid_service_data.copy()
        invalid_data['version'] = '1.0'
        
        with self.assertRaises(ValueError) as context:
            self.service_manager.validate_service_data(invalid_data)
        
        self.assertIn('Invalid version format', str(context.exception))
    
    def test_validate_service_data_invalid_arch(self):
        """Test validation of service data with invalid architecture."""
        invalid_data = self.valid_service_data.copy()
        invalid_data['arch'] = 'invalid-arch'
        
        with self.assertRaises(ValueError) as context:
            self.service_manager.validate_service_data(invalid_data)
        
        self.assertIn('Invalid architecture', str(context.exception))
    
    def test_validate_service_data_invalid_sharable(self):
        """Test validation of service data with invalid sharable value."""
        invalid_data = self.valid_service_data.copy()
        invalid_data['sharable'] = 'invalid'
        
        with self.assertRaises(ValueError) as context:
            self.service_manager.validate_service_data(invalid_data)
        
        self.assertIn('Invalid sharable value', str(context.exception))
    
    def test_validate_service_data_invalid_deployment(self):
        """Test validation of service data with invalid deployment format."""
        invalid_data = self.valid_service_data.copy()
        invalid_data['deployment'] = {'invalid': 'format'}
        
        with self.assertRaises(ValueError) as context:
            self.service_manager.validate_service_data(invalid_data)
        
        self.assertIn('Invalid deployment format', str(context.exception))
    
    def test_create_service(self):
        """Test service creation with validation."""
        self.mock_client.create_service.return_value = {'status': 'created'}
        
        result = self.service_manager.create_service('test-org', self.valid_service_data)
        
        self.assertEqual(result, {'status': 'created'})
        self.mock_client.create_service.assert_called_once_with('test-org', self.valid_service_data)
    
    def test_update_service(self):
        """Test service update with validation."""
        self.mock_client.update_service.return_value = {'status': 'updated'}
        
        result = self.service_manager.update_service('test-org', 'test-service', self.valid_service_data)
        
        self.assertEqual(result, {'status': 'updated'})
        self.mock_client.update_service.assert_called_once_with('test-org', 'test-service', self.valid_service_data)
    
    def test_search_services(self):
        """Test service search functionality."""
        mock_services = [
            {'label': 'Test Service 1', 'description': 'First test service'},
            {'label': 'Another Service', 'description': 'Second test service'},
            {'label': 'Third Service', 'description': 'Not a test service'}
        ]
        self.mock_client.list_services.return_value = mock_services
        
        # Search for 'test'
        results = self.service_manager.search_services('test-org', 'test')
        self.assertEqual(len(results), 3)
        
        # Search for 'another'
        results = self.service_manager.search_services('test-org', 'another')
        self.assertEqual(len(results), 1)
        
        # Empty search
        results = self.service_manager.search_services('test-org', '')
        self.assertEqual(len(results), 3)
    
    def test_get_service_versions(self):
        """Test getting service versions."""
        mock_services = [
            {'url': 'test-service', 'version': '1.0.0'},
            {'url': 'test-service', 'version': '1.1.0'},
            {'url': 'test-service', 'version': '2.0.0'},
            {'url': 'other-service', 'version': '1.0.0'}
        ]
        self.mock_client.list_services.return_value = mock_services
        
        versions = self.service_manager.get_service_versions('test-org', 'test-service')
        self.assertEqual(versions, ['1.0.0', '1.1.0', '2.0.0'])

if __name__ == '__main__':
    unittest.main() 