#!/usr/bin/env python3

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NodeDefinition:
    """Class for storing node definition data."""
    id: str
    org_id: str
    pattern: Optional[str]
    name: Optional[str]
    nodeType: Optional[str]
    publicKey: Optional[str]
    token: Optional[str]
    registeredServices: Optional[List[Dict]]
    policy: Optional[Dict]
    lastHeartbeat: Optional[datetime] = None
    lastUpdated: Optional[datetime] = None

class NodeManager:
    """Manages node-related operations and validation."""
    def __init__(self, client):
        self.client = client

    def validate_node_data(self, node_data: Dict) -> bool:
        required_fields = ['id', 'org_id']
        for field in required_fields:
            if field not in node_data:
                raise ValueError(f"Missing required field: {field}")
        return True

    def register_node(self, org_id: str, node_data: Dict) -> Dict:
        self.validate_node_data(node_data)
        return self.client.create_node(org_id, node_data)

    def get_node(self, org_id: str, node_id: str) -> Dict:
        return self.client.get_node(org_id, node_id)

    def update_node(self, org_id: str, node_id: str, node_data: Dict) -> Dict:
        self.validate_node_data(node_data)
        return self.client.update_node(org_id, node_id, node_data)

    def delete_node(self, org_id: str, node_id: str) -> Dict:
        return self.client.delete_node(org_id, node_id)

    def get_node_status(self, org_id: str, node_id: str) -> Dict:
        node = self.client.get_node(org_id, node_id)
        # Example: return heartbeat and status info if available
        return {
            'lastHeartbeat': node.get('lastHeartbeat'),
            'lastUpdated': node.get('lastUpdated'),
            'registeredServices': node.get('registeredServices'),
            'policy': node.get('policy'),
        } 