# Open Horizon Exchange API Endpoints

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
