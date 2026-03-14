# API Examples

This document provides example requests and responses for the Ops Incident Response Agent API.

## POST /runs

### Request

```bash
curl -X POST "http://localhost:8000/runs" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "High latency on payment service",
    "description": "Payment processing is slow, customers complaining about timeouts. Started around 10:00 AM UTC.",
    "service": "payment-service",
    "environment": "production",
    "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z"
  }'
```

### Response (201 Created)

```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "trace_id": "trace_550e8400"
}
```

## GET /runs/{run_id}

### Request

```bash
curl "http://localhost:8000/runs/550e8400-e29b-41d4-a716-446655440000"
```

### Response (200 OK)

```json
{
  "run": {
    "run_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "created_at": "2024-01-15T10:30:00.123456Z",
    "updated_at": "2024-01-15T10:30:05.789012Z",
    "trace_id": "trace_550e8400"
  },
  "state": {
    "incident": {
      "title": "High latency on payment service",
      "description": "Payment processing is slow, customers complaining about timeouts. Started around 10:00 AM UTC.",
      "service": "payment-service",
      "environment": "production",
      "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z"
    },
    "signals": [
      {
        "type": "latency",
        "data": {
          "service": "payment-service",
          "environment": "production",
          "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
          "p50_ms": 100,
          "p95_ms": 200,
          "p99_ms": 300,
          "error_rate": 0.01,
          "request_count": 10000,
          "anomalies": [
            {
              "timestamp": "2024-01-15T10:30:00Z",
              "severity": "high",
              "description": "P95 latency spike detected"
            }
          ]
        }
      },
      {
        "type": "error_rate",
        "data": {
          "service": "payment-service",
          "environment": "production",
          "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
          "error_rate": 0.05,
          "error_count": 500,
          "total_requests": 10000,
          "error_types": {
            "500": 300,
            "503": 150,
            "timeout": 50
          }
        }
      }
    ],
    "hypotheses": [],
    "tool_results": [
      {
        "tool": "metrics",
        "type": "latency",
        "result_id": "latency_001",
        "data": {
          "service": "payment-service",
          "environment": "production",
          "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
          "p50_ms": 100,
          "p95_ms": 200,
          "p99_ms": 300,
          "error_rate": 0.01,
          "request_count": 10000,
          "anomalies": [
            {
              "timestamp": "2024-01-15T10:30:00Z",
              "severity": "high",
              "description": "P95 latency spike detected"
            }
          ]
        }
      },
      {
        "tool": "metrics",
        "type": "error_rate",
        "result_id": "error_rate_001",
        "data": {
          "service": "payment-service",
          "environment": "production",
          "time_window": "2024-01-15T10:00:00Z/2024-01-15T11:00:00Z",
          "error_rate": 0.05,
          "error_count": 500,
          "total_requests": 10000,
          "error_types": {
            "500": 300,
            "503": 150,
            "timeout": 50
          }
        }
      }
    ],
    "actions": [],
    "open_questions": [],
    "human_events": [],
    "status": "completed"
  },
  "result": {
    "summary": "Incident analysis for High latency on payment service. Detected high error rate in payment-service (production).",
    "most_likely_cause": "High error rate detected - likely service degradation or dependency failure",
    "confidence": 0.75,
    "supporting_evidence": [
      "error_rate_001"
    ],
    "immediate_mitigations": [
      "Enable circuit breakers for downstream dependencies",
      "Scale up service instances if resource-constrained",
      "Check for recent deployments that may have introduced bugs"
    ],
    "verification_steps": [
      "Monitor error rate and latency metrics for 15 minutes",
      "Verify that mitigations have reduced error rate below 1%",
      "Check service health endpoints"
    ],
    "comms_template": "Incident: High latency on payment service\nStatus: Investigating\nImpact: payment-service experiencing errors\nMitigation: Enable circuit breakers for downstream dependencies",
    "followups": [
      "Root cause analysis post-mortem",
      "Review monitoring and alerting thresholds",
      "Update runbooks with lessons learned"
    ],
    "risk_notes": "Medium risk - service degradation detected. If not mitigated quickly, may impact user experience."
  }
}
```

## Error Responses

### 404 Not Found

```bash
curl "http://localhost:8000/runs/nonexistent-id"
```

```json
{
  "detail": "Run nonexistent-id not found"
}
```

### 501 Not Implemented (Human Events)

```bash
curl -X POST "http://localhost:8000/runs/550e8400-e29b-41d4-a716-446655440000/events" \
  -H "Content-Type: application/json" \
  -d '{"type": "approval", "message": "Approved"}'
```

```json
{
  "detail": "Human-in-the-loop not implemented in Chapter 1"
}
```

## Example Incident Scenarios

### Scenario 1: Latency Issue

```json
{
  "title": "API response times degraded",
  "description": "P95 latency increased from 200ms to 800ms over the past hour",
  "service": "api-gateway",
  "environment": "production",
  "time_window": "2024-01-15T09:00:00Z/2024-01-15T10:00:00Z"
}
```

### Scenario 2: Error Spike

```json
{
  "title": "High error rate on checkout service",
  "description": "Error rate jumped to 15% starting at 2:00 PM. Multiple 500 and 503 errors.",
  "service": "checkout-service",
  "environment": "production",
  "time_window": "2024-01-15T14:00:00Z/2024-01-15T15:00:00Z"
}
```

### Scenario 3: Service Degradation

```json
{
  "title": "Database connection pool exhaustion",
  "description": "Service unable to process requests due to database connection issues",
  "service": "user-service",
  "environment": "staging",
  "time_window": "2024-01-15T11:00:00Z/2024-01-15T12:00:00Z"
}
```

