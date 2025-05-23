#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from src.exchange_client import ExchangeAPIClient
from src.credentials import CredentialManager, Credentials

# Load environment variables from config.env
load_dotenv('config.env')

# Extract credentials from environment variables
org_id = os.getenv('HZN_ORG_ID')
user_auth = os.getenv('HZN_EXCHANGE_USER_AUTH')
exchange_url = os.getenv('HZN_EXCHANGE_URL')

# Split user_auth into username and password
username, password = user_auth.split(':')

# Create a Credentials object
credentials = Credentials(
    api_key=password,  # This is the password part of joewxboy:4Weath*r
    org_id=org_id,
    username=username,  # This is the username part of joewxboy:4Weath*r
    exchange_url=exchange_url
)

# Initialize the CredentialManager with the credentials
credential_manager = CredentialManager()
credential_manager._credentials = credentials

# Initialize the ExchangeAPIClient
client = ExchangeAPIClient(credential_manager)

# Test API calls
try:
    # List services for the organization
    print("\nListing services for organization '{}':".format(org_id))
    services = client.list_services(org_id)
    print(services)

    # List nodes for the organization
    print("\nListing nodes for organization '{}':".format(org_id))
    nodes_response = client.list_nodes(org_id)
    print(nodes_response)

    # Extract the first node ID
    node_ids = list(nodes_response.get('nodes', {}).keys())
    if not node_ids:
        print("No nodes found in organization. Skipping node operations.")
    else:
        node_id = node_ids[0]
        print(f"\nUsing node ID: {node_id}\n")
        # Node Management Tests
        print("\nTesting Node Management:")
        print("\nNote: Node registration is not currently supported.")
        # Sample node data
        node_data = {
            'pattern': 'pattern1',
            'name': 'Test Node',
            'nodeType': 'device',
            'publicKey': 'key123',
            'token': 'token123',
            'registeredServices': [],
            'policy': {}
        }
        # Get node details
        print("\nGetting node details:")
        node = client.get_node(org_id, node_id)
        print(node)
        # Update a node
        print("\nUpdating a node:")
        node_data['name'] = 'Updated Test Node'
        result = client.update_node(org_id, node_id, node_data)
        print(result)
        # Get node status
        print("\nGetting node status:")
        status = client.get_node(org_id, node_id)
        print(status)
        # Delete a node
        print("\nDeleting a node:")
        try:
            result = client.delete_node(org_id, node_id)
            print(result)
        except Exception as e:
            print(f"Delete node error: {e}")

except Exception as e:
    print("Error:", e)

finally:
    # Close the client session
    client.close() 