"""Fake metrics client for Chapter 1 and testing.

This implementation returns mock data to enable development and testing
without requiring real metrics infrastructure.
"""

from typing import Any

from ops_agent.agentic.tools.contracts import MetricsClient


class FakeMetricsClient(MetricsClient):
    """Fake implementation of MetricsClient that returns mock data."""

    def query_latency(
        self, service: str, environment: str, time_window: str
    ) -> dict[str, Any]:
        """Return mock latency metrics."""
        # Simulate some variance based on service name
        base_latency = 100 if "api" in service.lower() else 50
        return {
            "service": service,
            "environment": environment,
            "time_window": time_window,
            "p50_ms": base_latency,
            "p95_ms": base_latency * 2,
            "p99_ms": base_latency * 3,
            "error_rate": 0.01,
            "request_count": 10000,
            "anomalies": [
                {
                    "timestamp": "2024-01-15T10:30:00Z",
                    "severity": "high",
                    "description": "P95 latency spike detected",
                }
            ],
        }

    def query_error_rate(
        self, service: str, environment: str, time_window: str
    ) -> dict[str, Any]:
        """Return mock error rate metrics."""
        return {
            "service": service,
            "environment": environment,
            "time_window": time_window,
            "error_rate": 0.05,  # 5% error rate
            "error_count": 500,
            "total_requests": 10000,
            "error_types": {
                "500": 300,
                "503": 150,
                "timeout": 50,
            },
        }

