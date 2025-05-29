#!/usr/bin/env python3

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class NodeDefinition(BaseModel):
    """Model for node definition data."""
    id: str
    org_id: str
    pattern: Optional[str] = None
    name: Optional[str] = None
    nodeType: Optional[str] = None
    publicKey: Optional[str] = None
    token: Optional[str] = None
    registeredServices: List[Dict] = Field(default_factory=list)
    policy: Dict = Field(default_factory=dict)
    lastHeartbeat: Optional[datetime] = None
    lastUpdated: Optional[datetime] = None

    @validator('nodeType')
    def validate_node_type(cls, v):
        """Validate node type."""
        if v is not None and v not in {'device', 'cluster', 'edge'}:
            raise ValueError(f"Invalid node type: {v}")
        return v

    @validator('registeredServices')
    def validate_services(cls, v):
        """Validate registered services."""
        if not isinstance(v, list):
            raise ValueError("registeredServices must be a list")
        return v

    @validator('policy')
    def validate_policy(cls, v):
        """Validate node policy."""
        if not isinstance(v, dict):
            raise ValueError("policy must be a dictionary")
        return v

    @classmethod
    def from_api_response(cls, data: Dict) -> 'NodeDefinition':
        """Create a NodeDefinition instance from API response data."""
        return cls(**data)

class NodeManager:
    """Manages node-related operations and validation."""
    def __init__(self, client):
        self.client = client

    def validate_node_data(self, node_data: Dict) -> bool:
        """Validate node data before registration or update."""
        try:
            NodeDefinition(**node_data)
            return True
        except Exception as e:
            raise ValueError(f"Node validation failed: {str(e)}")

    def register_node(self, org_id: str, node_data: Dict) -> Dict:
        """Register a new node with validation."""
        self.validate_node_data(node_data)
        return self.client.create_node(org_id, node_data)

    def get_node(self, org_id: str, node_id: str) -> NodeDefinition:
        """Get node details."""
        response = self.client.get_node(org_id, node_id)
        return NodeDefinition.from_api_response(response)

    def update_node(self, org_id: str, node_id: str, node_data: Dict) -> Dict:
        """Update an existing node with validation."""
        self.validate_node_data(node_data)
        return self.client.update_node(org_id, node_id, node_data)

    def delete_node(self, org_id: str, node_id: str) -> Dict:
        """Delete a node."""
        return self.client.delete_node(org_id, node_id)

    def get_node_status(self, org_id: str, node_id: str) -> Dict:
        """Get node status information."""
        node = self.get_node(org_id, node_id)
        return {
            'lastHeartbeat': node.lastHeartbeat,
            'lastUpdated': node.lastUpdated,
            'registeredServices': node.registeredServices,
            'policy': node.policy
        } 