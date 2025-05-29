import asyncio
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from src.exchange.client import ExchangeAPIClient
from openhorizon_client.service import ServiceManager, ServiceInfo, ServiceListType

load_dotenv("config.env")

# Extract username and password for use in the script, but do not overwrite HZN_EXCHANGE_USER_AUTH
def get_username_password():
    user_auth = os.getenv("HZN_EXCHANGE_USER_AUTH")
    if user_auth and ":" in user_auth:
        return user_auth.split(":", 1)
    return user_auth, None

async def test_catalog_services(client: ExchangeAPIClient) -> List[ServiceInfo]:
    """Test retrieving services from the catalog."""
    manager = ServiceManager(client)
    services = await manager.get_service_list(ServiceListType.CATALOG)
    print(f"\nCatalog Services ({len(services)} found):")
    for service in services[:5]:  # Show first 5 services
        print(f"- {service.name} (ID: {service.id}, Owner: {service.owner})")
    return services

async def test_user_services(client: ExchangeAPIClient, username: str) -> List[ServiceInfo]:
    """Test retrieving services published by a specific user."""
    manager = ServiceManager(client)
    services = await manager.get_user_services(username)
    print(f"\nUser Services for {username} ({len(services)} found):")
    for service in services[:5]:  # Show first 5 services
        print(f"- {service.name} (ID: {service.id}, Public: {service.public})")
    return services

async def test_public_services(client: ExchangeAPIClient) -> List[ServiceInfo]:
    """Test retrieving public services."""
    manager = ServiceManager(client)
    services = await manager.get_public_services()
    print(f"\nPublic Services ({len(services)} found):")
    for service in services[:5]:  # Show first 5 services
        print(f"- {service.name} (ID: {service.id}, Owner: {service.owner})")
    return services

async def test_org_services(client: ExchangeAPIClient) -> List[ServiceInfo]:
    """Test retrieving services available to the organization."""
    manager = ServiceManager(client)
    services = await manager.get_org_services()
    print(f"\nOrganization Services ({len(services)} found):")
    for service in services[:5]:  # Show first 5 services
        print(f"- {service.name} (ID: {service.id}, Public: {service.public})")
    return services

async def test_node_services(client: ExchangeAPIClient, node_id: str) -> List[ServiceInfo]:
    """Test retrieving services running on a specific node."""
    manager = ServiceManager(client)
    services = await manager.get_node_services(node_id)
    print(f"\nNode Services for {node_id} ({len(services)} found):")
    for service in services[:5]:  # Show first 5 services
        print(f"- {service.name} (ID: {service.id}, State: {service.state})")
    return services

async def main():
    # Get credentials from environment variables
    org_id = os.getenv("HZN_ORG_ID")
    username, password = get_username_password()
    exchange_url = os.getenv("HZN_EXCHANGE_URL", "https://exchange.edge-fabric.com/v1")
    
    if not all([org_id, username, password]):
        print("Error: Missing required environment variables")
        print("Please set HZN_ORG_ID, HZN_EXCHANGE_USER_AUTH (username:password format)")
        return
    
    # Create client
    client = ExchangeAPIClient()
    
    try:
        # Test catalog services
        catalog_services = await test_catalog_services(client)
        if not catalog_services:
            print("Warning: No services found in catalog")
        
        # Test user services
        user_services = await test_user_services(client, username)
        if not user_services:
            print("Warning: No services found for user")
        
        # Test public services
        public_services = await test_public_services(client)
        if not public_services:
            print("Warning: No public services found")
        
        # Test organization services
        org_services = await test_org_services(client)
        if not org_services:
            print("Warning: No organization services found")
        
        # Test node services (if we have a node ID)
        node_id = os.getenv("HZN_NODE_ID")
        if node_id:
            node_services = await test_node_services(client, node_id)
            if not node_services:
                print("Warning: No services found on node")
        else:
            print("\nSkipping node services test (HZN_NODE_ID not set)")
        
    except Exception as e:
        print(f"Error testing endpoints: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 