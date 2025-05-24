# Metrics Flow Diagrams

This document provides visual representations of how metrics flow through the Open Horizon AI Integration Framework.

## Metrics Collection Flow

```mermaid
graph TD
    A[Service/Node] -->|Raw Metrics| B[Metrics Collector]
    B -->|Processed Metrics| C[Metrics History]
    C -->|Analysis| D[AI Agent]
    D -->|Alerts| E[Alert Manager]
    D -->|Recommendations| F[Action Manager]
    
    subgraph "Collection Layer"
        A
        B
    end
    
    subgraph "Storage Layer"
        C
    end
    
    subgraph "Analysis Layer"
        D
    end
    
    subgraph "Action Layer"
        E
        F
    end
```

## Service Metrics Flow

```mermaid
graph LR
    A[Service] -->|Container Stats| B[Service Metrics Collector]
    B -->|CPU Usage| C[Metrics History]
    B -->|Memory Usage| C
    B -->|Response Time| C
    B -->|Error Rate| C
    C -->|Time Window| D[Analysis]
    D -->|Trends| E[Health Status]
    D -->|Thresholds| E
    E -->|Alerts| F[Alert Manager]
    E -->|Actions| G[Service Manager]
```

## Node Metrics Flow

```mermaid
graph LR
    A[Node] -->|System Stats| B[Node Metrics Collector]
    B -->|CPU Usage| C[Metrics History]
    B -->|Memory Usage| C
    B -->|Disk Usage| C
    B -->|Temperature| C
    C -->|Time Window| D[Analysis]
    D -->|Trends| E[Health Status]
    D -->|Thresholds| E
    E -->|Alerts| F[Alert Manager]
    E -->|Actions| G[Node Manager]
```

## Metrics Analysis Flow

```mermaid
graph TD
    A[Metrics History] -->|Raw Data| B[Statistical Analysis]
    A -->|Time Series| C[Trend Detection]
    A -->|Patterns| D[Anomaly Detection]
    
    B -->|Mean/Median| E[Health Assessment]
    B -->|Std Dev| E
    B -->|Percentiles| E
    
    C -->|Increasing| E
    C -->|Decreasing| E
    C -->|Stable| E
    
    D -->|Outliers| E
    D -->|Deviations| E
    
    E -->|Status| F[Health Status]
    E -->|Alerts| G[Alert Generation]
    E -->|Actions| H[Recommendations]
```

## Alert Generation Flow

```mermaid
graph TD
    A[Health Assessment] -->|Threshold Violation| B[Alert Generator]
    A -->|Trend Change| B
    A -->|Anomaly| B
    
    B -->|Severity| C[Alert Manager]
    B -->|Context| C
    
    C -->|Critical| D[Immediate Action]
    C -->|Warning| E[Scheduled Action]
    C -->|Info| F[Monitoring]
    
    D -->|Service Restart| G[Action Executor]
    D -->|Node Reboot| G
    E -->|Scale Service| G
    E -->|Update Config| G
```

## Data Retention Flow

```mermaid
graph TD
    A[New Metrics] -->|Add| B[Metrics History]
    B -->|Check Age| C[Cleanup Manager]
    C -->|Old Data| D[Archive/Delete]
    C -->|Recent Data| B
    
    subgraph "Retention Policy"
        E[Max History: 1000]
        F[Cleanup Interval: 30m]
        G[Archive Age: 7d]
    end
    
    E --> C
    F --> C
    G --> C
```

## Configuration Flow

```mermaid
graph TD
    A[Environment Variables] -->|Load| B[Config Manager]
    B -->|Collection| C[Metrics Collectors]
    B -->|Analysis| D[Analysis Engine]
    B -->|Alerts| E[Alert System]
    
    subgraph "Collection Config"
        F[Service Window: 15m]
        G[Node Window: 60m]
    end
    
    subgraph "Analysis Config"
        H[Trend Window: 1h]
        I[Anomaly Window: 24h]
    end
    
    subgraph "Alert Config"
        J[Alert Interval: 5m]
        K[Max Alerts: 10]
    end
    
    F --> C
    G --> C
    H --> D
    I --> D
    J --> E
    K --> E
```

These diagrams illustrate:
1. How metrics are collected from services and nodes
2. How metrics flow through the system
3. How analysis is performed on the metrics
4. How alerts are generated and managed
5. How data retention works
6. How configuration flows through the system

Each diagram shows a different aspect of the metrics system, making it easier to understand the overall architecture and data flow. 