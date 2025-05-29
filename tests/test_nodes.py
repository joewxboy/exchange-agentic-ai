#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from src.nodes import NodeManager, NodeDefinition

class TestNodeManager(unittest.TestCase):
    """Test cases for the NodeManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.node_manager = NodeManager(self.mock_client)
        
        # Sample valid node data
        self.valid_node_data = {
            'id': 'node1',
            'org_id': 'examples',
            'pattern': 'pattern1',
            'name': 'Test Node',
            'nodeType': 'device',
            'publicKey': 'key123',
            'token': 'token123',
            'registeredServices': [],
            'policy': {}
        }
    
    def test_validate_node_data_valid(self):
        """Test validation of valid node data."""
        self.assertTrue(self.node_manager.validate_node_data(self.valid_node_data))
    
    def test_validate_node_data_missing_field(self):
        """Test validation of node data with missing required field."""
        invalid_data = self.valid_node_data.copy()
        del invalid_data['id']
        
        with self.assertRaises(ValueError) as context:
            self.node_manager.validate_node_data(invalid_data)
        
        self.assertIn('Field required', str(context.exception))
    
    def test_validate_node_data_invalid_type(self):
        """Test validation of node data with invalid node type."""
        invalid_data = self.valid_node_data.copy()
        invalid_data['nodeType'] = 'invalid_type'
        
        with self.assertRaises(ValueError) as context:
            self.node_manager.validate_node_data(invalid_data)
        
        self.assertIn('Invalid node type', str(context.exception))
    
    def test_validate_node_data_invalid_services(self):
        """Test validation of node data with invalid services format."""
        invalid_data = self.valid_node_data.copy()
        invalid_data['registeredServices'] = 'not_a_list'
        
        with self.assertRaises(ValueError) as context:
            self.node_manager.validate_node_data(invalid_data)
        
        self.assertIn('Input should be a valid list', str(context.exception))
    
    def test_validate_node_data_invalid_policy(self):
        """Test validation of node data with invalid policy format."""
        invalid_data = self.valid_node_data.copy()
        invalid_data['policy'] = 'not_a_dict'
        
        with self.assertRaises(ValueError) as context:
            self.node_manager.validate_node_data(invalid_data)
        
        self.assertIn('Input should be a valid dictionary', str(context.exception))
    
    def test_register_node(self):
        """Test node registration with validation."""
        self.mock_client.create_node.return_value = {'status': 'registered'}
        
        result = self.node_manager.register_node('examples', self.valid_node_data)
        
        self.assertEqual(result, {'status': 'registered'})
        self.mock_client.create_node.assert_called_once_with('examples', self.valid_node_data)
    
    def test_get_node(self):
        """Test retrieving a node."""
        self.mock_client.get_node.return_value = self.valid_node_data
        
        result = self.node_manager.get_node('examples', 'node1')
        
        self.assertIsInstance(result, NodeDefinition)
        self.assertEqual(result.id, self.valid_node_data['id'])
        self.assertEqual(result.org_id, self.valid_node_data['org_id'])
        self.assertEqual(result.nodeType, self.valid_node_data['nodeType'])
        self.mock_client.get_node.assert_called_once_with('examples', 'node1')
    
    def test_update_node(self):
        """Test updating a node with validation."""
        self.mock_client.update_node.return_value = {'status': 'updated'}
        
        result = self.node_manager.update_node('examples', 'node1', self.valid_node_data)
        
        self.assertEqual(result, {'status': 'updated'})
        self.mock_client.update_node.assert_called_once_with('examples', 'node1', self.valid_node_data)
    
    def test_delete_node(self):
        """Test deleting a node."""
        self.mock_client.delete_node.return_value = {'status': 'deleted'}
        
        result = self.node_manager.delete_node('examples', 'node1')
        
        self.assertEqual(result, {'status': 'deleted'})
        self.mock_client.delete_node.assert_called_once_with('examples', 'node1')
    
    def test_get_node_status(self):
        """Test retrieving node status."""
        self.mock_client.get_node.return_value = {
            'id': 'node1',
            'org_id': 'examples',
            'lastHeartbeat': datetime.now(),
            'lastUpdated': datetime.now(),
            'registeredServices': [],
            'policy': {}
        }
        
        result = self.node_manager.get_node_status('examples', 'node1')
        
        self.assertIn('lastHeartbeat', result)
        self.assertIn('lastUpdated', result)
        self.assertIn('registeredServices', result)
        self.assertIn('policy', result)
        self.mock_client.get_node.assert_called_once_with('examples', 'node1')
    
    def test_from_api_response(self):
        """Test creating NodeDefinition from API response."""
        node = NodeDefinition.from_api_response(self.valid_node_data)
        self.assertEqual(node.id, self.valid_node_data['id'])
        self.assertEqual(node.org_id, self.valid_node_data['org_id'])
        self.assertEqual(node.nodeType, self.valid_node_data['nodeType'])
        self.assertEqual(node.registeredServices, self.valid_node_data['registeredServices'])
        self.assertEqual(node.policy, self.valid_node_data['policy'])

if __name__ == '__main__':
    unittest.main() 