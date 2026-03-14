"""Tool interface contracts.

All tools must implement these interfaces to ensure consistent behavior
and enable easy swapping of implementations (real vs fake, test vs prod).
"""

from abc import ABC, abstractmethod
from typing import Any


class MetricsClient(ABC):
    """Interface for querying metrics/telemetry data.

    Implementations:
    - FakeMetricsClient: Returns mock data (Chapter 1, tests)
    - PrometheusMetricsClient: Real Prometheus queries (Chapter 4+)
    - CloudWatchMetricsClient: AWS CloudWatch queries (Chapter 4+)
    """

    @abstractmethod
    def query_latency(
        self, service: str, environment: str, time_window: str
    ) -> dict[str, Any]:
        """Query latency metrics for a service.

        Args:
            service: Service name
            environment: Environment (production, staging, etc.)
            time_window: Time range to query (ISO format or relative)

        Returns:
            Dictionary with latency metrics including:
            - p50, p95, p99 percentiles
            - error_rate
            - request_count
            - anomalies (if detected)
        """
        pass

    @abstractmethod
    def query_error_rate(
        self, service: str, environment: str, time_window: str
    ) -> dict[str, Any]:
        """Query error rate metrics for a service.

        Args:
            service: Service name
            environment: Environment
            time_window: Time range to query

        Returns:
            Dictionary with error metrics including:
            - error_rate (percentage)
            - error_count
            - total_requests
            - error_types (breakdown by error code/type)
        """
        pass


class LogClient(ABC):
    """Interface for querying logs.

    TODO: Implement in Chapter 4+
    """

    @abstractmethod
    def search_logs(
        self, service: str, environment: str, query: str, time_window: str
    ) -> list[dict[str, Any]]:
        """Search logs for a service.

        Args:
            service: Service name
            environment: Environment
            query: Search query (e.g., "error", "exception", "timeout")
            time_window: Time range to search

        Returns:
            List of log entries matching the query
        """
        pass


class DeploymentClient(ABC):
    """Interface for querying deployment history.

    TODO: Implement in Chapter 4+
    """

    @abstractmethod
    def get_recent_deployments(
        self, service: str, environment: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get recent deployments for a service.

        Args:
            service: Service name
            environment: Environment
            limit: Maximum number of deployments to return

        Returns:
            List of deployment records with timestamps, versions, status
        """
        pass

