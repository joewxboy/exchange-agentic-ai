#!/usr/bin/env python3

import os
import requests
import yaml
import json
from pathlib import Path
from bs4 import BeautifulSoup

def create_directory(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)

def download_file(url, output_path):
    """Download file from URL and save to output path."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_path, 'w') as f:
            f.write(response.text)
        print(f"Downloaded {url} to {output_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

def create_api_documentation():
    """Create structured API documentation."""
    base_dir = Path("docs/api")
    
    # Create API documentation structure
    api_docs = {
        "version": "1.0.0",
        "info": {
            "title": "Open Horizon Exchange API",
            "description": "API documentation for the Open Horizon Exchange Server",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "https://exchange.example.com",
                "description": "Open Horizon Exchange Server"
            }
        ],
        "paths": {
            "/orgs": {
                "get": {
                    "summary": "List organizations",
                    "description": "Get a list of all organizations",
                    "responses": {
                        "200": {
                            "description": "List of organizations"
                        }
                    }
                }
            },
            "/orgs/{orgid}": {
                "get": {
                    "summary": "Get organization",
                    "description": "Get details of a specific organization",
                    "parameters": [
                        {
                            "name": "orgid",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Organization details"
                        }
                    }
                }
            }
        }
    }
    
    # Save OpenAPI specification
    with open(base_dir / "openapi.yaml", 'w') as f:
        yaml.dump(api_docs, f, sort_keys=False)
    
    # Create endpoints documentation
    endpoints_doc = """# Open Horizon Exchange API Endpoints

## Organizations

### List Organizations
- **GET** `/orgs`
- Returns a list of all organizations

### Get Organization
- **GET** `/orgs/{orgid}`
- Returns details of a specific organization

## Services

### List Services
- **GET** `/orgs/{orgid}/services`
- Returns a list of services in an organization

### Get Service
- **GET** `/orgs/{orgid}/services/{service}`
- Returns details of a specific service

## Patterns

### List Patterns
- **GET** `/orgs/{orgid}/patterns`
- Returns a list of patterns in an organization

### Get Pattern
- **GET** `/orgs/{orgid}/patterns/{pattern}`
- Returns details of a specific pattern

## Nodes

### List Nodes
- **GET** `/orgs/{orgid}/nodes`
- Returns a list of nodes in an organization

### Get Node
- **GET** `/orgs/{orgid}/nodes/{nodeid}`
- Returns details of a specific node
"""
    
    with open(base_dir / "endpoints.md", 'w') as f:
        f.write(endpoints_doc)

def main():
    # Create necessary directories
    base_dir = Path("docs/api")
    create_directory(base_dir)
    create_directory(base_dir / "examples")

    # Create API documentation
    create_api_documentation()

    print("API documentation creation complete.")

if __name__ == "__main__":
    main() 