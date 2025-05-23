# Open Horizon Exchange API Documentation

This directory contains the OpenAPI/Swagger specifications and documentation for the Open Horizon Exchange API.

## Contents

1. `openapi.yaml` - OpenAPI 3.0 specification for the Exchange API
2. `endpoints.md` - Detailed documentation of API endpoints
3. `examples/` - Example API usage and workflows

## API Resources

- [Open Horizon Exchange API Documentation](https://github.com/open-horizon/exchange-api)
- [Open Horizon Exchange API Reference](https://github.com/open-horizon/exchange-api/blob/master/README.md)

## Related Documentation

- [Usage Examples](../usage_examples.md)
- [Configuration Guide](../configuration_guide.md)
- [Troubleshooting Guide](../troubleshooting_guide.md)
- [AI Integration Guide](../ai_integration_guide.md)

## Authentication

The Exchange API uses API key authentication. Each request must include:
- `Authorization` header with the API key
- `Content-Type: application/json` header for POST/PUT requests

## Rate Limits

The API implements rate limiting to prevent abuse. Please refer to the specific endpoint documentation for rate limit details.

## Error Handling

The API uses standard HTTP status codes and returns error messages in JSON format:

```json
{
    "code": "error_code",
    "msg": "Error message",
    "details": "Additional error details"
}
``` 