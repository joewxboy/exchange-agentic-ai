# Configuration Guide: Open Horizon AI Integration Framework

This guide explains how to configure the framework for development and production environments.

## 1. Environment Variables

Set these variables in your `.env` or environment:

| Variable                      | Description                                 | Example Value                        |
|-------------------------------|---------------------------------------------|--------------------------------------|
| EXCHANGE_URL                  | Base URL for the Exchange API               | http://localhost:8080                |
| EXCHANGE_ORG                  | Organization ID                             | testorg                              |
| EXCHANGE_USERNAME             | Exchange username                           | user                                 |
| EXCHANGE_PASSWORD             | Exchange password or API key                | pass                                 |
| METRICS_ANALYSIS_WINDOW       | Metrics analysis window (minutes)           | 60                                   |
| METRICS_CLEANUP_INTERVAL      | Cleanup interval for old metrics (minutes)  | 30                                   |
| MAX_METRICS_HISTORY           | Maximum number of metrics to keep           | 1000                                 |
| SERVICE_METRICS_WINDOW        | Service metrics analysis window (minutes)   | 15                                   |
| SERVICE_CPU_THRESHOLD         | CPU usage threshold for services (%)        | 80                                   |
| SERVICE_MEMORY_THRESHOLD      | Memory usage threshold for services (%)     | 85                                   |
| SERVICE_ERROR_RATE_THRESHOLD  | Error rate threshold for services           | 0.05                                 |
| SERVICE_RESPONSE_TIME_THRESHOLD| Response time threshold (ms)               | 1000                                 |
| NODE_METRICS_WINDOW           | Node metrics analysis window (minutes)      | 60                                   |
| NODE_CPU_THRESHOLD            | CPU usage threshold for nodes (%)           | 80                                   |
| NODE_MEMORY_THRESHOLD         | Memory usage threshold for nodes (%)        | 85                                   |
| NODE_DISK_THRESHOLD           | Disk usage threshold for nodes (%)          | 90                                   |
| NODE_TEMPERATURE_THRESHOLD    | Temperature threshold for nodes (°C)        | 75                                   |

## 2. Example .env File

```
EXCHANGE_URL=http://localhost:8080
EXCHANGE_ORG=testorg
EXCHANGE_USERNAME=user
EXCHANGE_PASSWORD=pass
METRICS_ANALYSIS_WINDOW=60
METRICS_CLEANUP_INTERVAL=30
MAX_METRICS_HISTORY=1000
SERVICE_METRICS_WINDOW=15
SERVICE_CPU_THRESHOLD=80
SERVICE_MEMORY_THRESHOLD=85
SERVICE_ERROR_RATE_THRESHOLD=0.05
SERVICE_RESPONSE_TIME_THRESHOLD=1000
NODE_METRICS_WINDOW=60
NODE_CPU_THRESHOLD=80
NODE_MEMORY_THRESHOLD=85
NODE_DISK_THRESHOLD=90
NODE_TEMPERATURE_THRESHOLD=75
```

## 3. Agent Configuration

- **ServiceManagementAgent**: Uses `EXCHANGE_*` and `SERVICE_*` variables
- **NodeManagementAgent**: Uses `EXCHANGE_*` and `NODE_*` variables
- **MetricsCollector**: Uses `METRICS_*` variables

## 4. API Client Configuration

The `ExchangeAPIClient` can be configured via environment variables or directly in code:
```python
from src.exchange.client import ExchangeAPIClient
import os
client = ExchangeAPIClient(
    base_url=os.getenv("EXCHANGE_URL"),
    org=os.getenv("EXCHANGE_ORG"),
    username=os.getenv("EXCHANGE_USERNAME"),
    password=os.getenv("EXCHANGE_PASSWORD")
)
```

## 5. Runtime Configuration Overrides

You can override configuration at runtime using Python code:
```python
import os
os.environ['SERVICE_CPU_THRESHOLD'] = '70'  # Override threshold for this session
```
Or by directly setting attributes on objects:
```python
from src.ai.metrics import MetricsCollector
collector = MetricsCollector()
collector._analysis_window = timedelta(minutes=10)  # Change window on the fly
```

## 6. Configuration Precedence

1. **Explicit code overrides** (highest precedence)
2. **Environment variables** (including `.env` files loaded with `python-dotenv`)
3. **Default values in code** (lowest precedence)

## 7. Troubleshooting Configuration Issues

- **Missing or incorrect environment variables**: Check `.env` file and environment
- **Type errors**: Ensure all config values are the correct type (e.g., integers for thresholds)
- **API connection errors**: Verify `EXCHANGE_URL` and credentials
- **Metrics not collected**: Check analysis window and cleanup intervals
- **Unexpected alerts**: Review threshold values and adjust as needed

## 8. Security Best Practices

- **Never commit `.env` files with real credentials to version control**
- **Use environment variables for secrets in production**
- **Restrict file permissions on config files**
- **Rotate API keys and passwords regularly**
- **Audit logs for unauthorized access attempts**

## 9. Scaling and Performance Tuning

- **Increase `MAX_METRICS_HISTORY`** for longer history, but monitor memory usage
- **Adjust analysis and cleanup intervals** for your workload
- **Tune thresholds to reduce alert noise**
- **Profile memory and CPU usage with large deployments**
- **Use concurrent metrics collection for high-throughput scenarios**

## 10. Running with Configuration

- Install dependencies: `pip install -r requirements.txt`
- Set environment variables or create a `.env` file
- Run your scripts or agents as shown in the usage examples

---
For more details, see the API documentation in `docs/api/` and usage examples in `docs/usage_examples.md`. 