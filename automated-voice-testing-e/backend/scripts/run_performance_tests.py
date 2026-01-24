"""
Performance Testing Script

This script runs load tests against the Voice AI Testing Framework API
to measure performance metrics including response times, throughput,
and system behavior under concurrent load.

Features:
- Concurrent load testing with configurable users
- Response time measurement (mean, median, p95, p99)
- Throughput measurement (requests per second)
- Success rate tracking
- Performance report generation

Usage:
    python -m scripts.run_performance_tests

Example:
    >>> from scripts.run_performance_tests import run_load_test
    >>> results = run_load_test()
    >>> print(f"Mean response time: {results['mean_response_time']:.3f}s")
"""

import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests


# Load test configuration
LOAD_TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "concurrent_users": 100,  # Number of concurrent users
    "duration_seconds": 30,   # Duration of load test
    "endpoints": [
        {"path": "/health", "method": "GET", "weight": 10},
        {"path": "/api/openapi.json", "method": "GET", "weight": 5},
    ],
    "timeout_seconds": 10,
    "ramp_up_seconds": 5  # Gradual ramp-up of users
}


class PerformanceMetrics:
    """
    Tracks and calculates performance metrics during load testing.

    Attributes:
        response_times (List[float]): List of response times in seconds
        requests_per_second (float): Calculated throughput
        success_count (int): Number of successful requests
        failure_count (int): Number of failed requests
        start_time (float): Test start timestamp
        end_time (float): Test end timestamp

    Example:
        >>> metrics = PerformanceMetrics()
        >>> metrics.record_success(0.150)
        >>> metrics.record_failure()
        >>> stats = metrics.calculate_statistics()
    """

    def __init__(self):
        """Initialize performance metrics"""
        self.response_times: List[float] = []
        self.requests_per_second: float = 0.0
        self.success_count: int = 0
        self.failure_count: int = 0
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.errors: List[str] = []

    def record_success(self, response_time: float):
        """
        Record a successful request.

        Args:
            response_time: Response time in seconds
        """
        self.response_times.append(response_time)
        self.success_count += 1

    def record_failure(self, error: str = "Unknown error"):
        """
        Record a failed request.

        Args:
            error: Error message describing the failure
        """
        self.failure_count += 1
        self.errors.append(error)

    def start_timer(self):
        """Start the performance test timer"""
        self.start_time = time.time()

    def stop_timer(self):
        """Stop the performance test timer"""
        self.end_time = time.time()
        self._calculate_throughput()

    def _calculate_throughput(self):
        """Calculate requests per second"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            total_requests = self.success_count + self.failure_count
            self.requests_per_second = total_requests / duration if duration > 0 else 0.0

    def calculate_statistics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive performance statistics.

        Returns:
            Dictionary containing performance metrics:
            - mean_response_time: Average response time
            - median_response_time: Median response time
            - min_response_time: Minimum response time
            - max_response_time: Maximum response time
            - p95_response_time: 95th percentile response time
            - p99_response_time: 99th percentile response time
            - success_rate: Percentage of successful requests
            - requests_per_second: Throughput

        Example:
            >>> metrics = PerformanceMetrics()
            >>> stats = metrics.calculate_statistics()
            >>> print(f"P95: {stats['p95_response_time']:.3f}s")
        """
        if not self.response_times:
            return {
                "mean_response_time": 0.0,
                "median_response_time": 0.0,
                "min_response_time": 0.0,
                "max_response_time": 0.0,
                "p95_response_time": 0.0,
                "p99_response_time": 0.0,
                "success_rate": 0.0,
                "requests_per_second": 0.0,
                "total_requests": self.success_count + self.failure_count,
                "success_count": self.success_count,
                "failure_count": self.failure_count
            }

        sorted_times = sorted(self.response_times)
        total_requests = self.success_count + self.failure_count

        return {
            "mean_response_time": statistics.mean(self.response_times),
            "median_response_time": statistics.median(self.response_times),
            "min_response_time": min(self.response_times),
            "max_response_time": max(self.response_times),
            "p95_response_time": sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0.0,
            "p99_response_time": sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0.0,
            "success_rate": (self.success_count / total_requests * 100) if total_requests > 0 else 0.0,
            "requests_per_second": self.requests_per_second,
            "total_requests": total_requests,
            "success_count": self.success_count,
            "failure_count": self.failure_count
        }


def measure_response_time(url: str, method: str = "GET", timeout: int = 10) -> Optional[float]:
    """
    Measure response time for a single HTTP request.

    Args:
        url: Full URL to test
        method: HTTP method (GET, POST, etc.)
        timeout: Request timeout in seconds

    Returns:
        Response time in seconds, or None if request failed

    Example:
        >>> response_time = measure_response_time("http://localhost:8000/health")
        >>> print(f"Response time: {response_time:.3f}s")
    """
    try:
        start = time.time()
        if method.upper() == "GET":
            response = requests.get(url, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, timeout=timeout)
        else:
            return None

        end = time.time()

        if response.status_code < 400:
            return end - start
        else:
            return None

    except Exception:
        return None


def concurrent_worker(
    endpoint: Dict[str, Any],
    base_url: str,
    metrics: PerformanceMetrics,
    stop_time: float,
    timeout: int = 10
) -> None:
    """
    Worker function for concurrent load testing.

    Continuously makes requests to the endpoint until stop_time is reached.

    Args:
        endpoint: Endpoint configuration with path and method
        base_url: Base URL of the API
        metrics: PerformanceMetrics instance to record results
        stop_time: Timestamp when to stop making requests
        timeout: Request timeout in seconds

    Example:
        >>> from concurrent.futures import ThreadPoolExecutor
        >>> metrics = PerformanceMetrics()
        >>> stop_time = time.time() + 10
        >>> with ThreadPoolExecutor(max_workers=10) as executor:
        ...     executor.submit(concurrent_worker, endpoint, base_url, metrics, stop_time)
    """
    url = f"{base_url}{endpoint['path']}"
    method = endpoint.get('method', 'GET')

    while time.time() < stop_time:
        response_time = measure_response_time(url, method, timeout)

        if response_time is not None:
            metrics.record_success(response_time)
        else:
            metrics.record_failure(f"Failed request to {endpoint['path']}")

        # Small delay to prevent overwhelming the system
        time.sleep(0.01)


def run_load_test(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run load test with concurrent users.

    Args:
        config: Load test configuration dictionary. If None, uses LOAD_TEST_CONFIG.

    Returns:
        Dictionary containing test results and performance statistics

    Example:
        >>> results = run_load_test()
        >>> print(f"Throughput: {results['requests_per_second']:.2f} req/s")
        >>> print(f"P95 response time: {results['p95_response_time']:.3f}s")
    """
    if config is None:
        config = LOAD_TEST_CONFIG

    metrics = PerformanceMetrics()
    base_url = config['base_url']
    concurrent_users = config['concurrent_users']
    duration = config['duration_seconds']
    endpoints = config['endpoints']
    timeout = config.get('timeout_seconds', 10)

    print(f"\n{'='*70}")
    print("Starting Load Test")
    print(f"{'='*70}")
    print(f"Base URL: {base_url}")
    print(f"Concurrent Users: {concurrent_users}")
    print(f"Duration: {duration} seconds")
    print(f"Endpoints: {len(endpoints)}")
    print(f"{'='*70}\n")

    # Start metrics timer
    metrics.start_timer()
    stop_time = time.time() + duration

    # Create thread pool and submit workers
    with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = []

        # Submit workers for each endpoint based on weight
        for endpoint in endpoints:
            weight = endpoint.get('weight', 1)
            for _ in range(weight):
                future = executor.submit(
                    concurrent_worker,
                    endpoint,
                    base_url,
                    metrics,
                    stop_time,
                    timeout
                )
                futures.append(future)

        # Wait for all workers to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                metrics.record_failure(str(e))

    # Stop metrics timer
    metrics.stop_timer()

    # Calculate statistics
    stats = metrics.calculate_statistics()

    return stats


def generate_report(stats: Dict[str, Any]) -> str:
    """
    Generate a formatted performance test report.

    Args:
        stats: Performance statistics dictionary from run_load_test

    Returns:
        Formatted report string

    Example:
        >>> stats = run_load_test()
        >>> report = generate_report(stats)
        >>> print(report)
    """
    report = f"""
{'='*70}
PERFORMANCE TEST REPORT
{'='*70}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY STATISTICS
------------------
Total Requests:        {stats['total_requests']:,}
Successful Requests:   {stats['success_count']:,}
Failed Requests:       {stats['failure_count']:,}
Success Rate:          {stats['success_rate']:.2f}%
Throughput:            {stats['requests_per_second']:.2f} requests/second

RESPONSE TIME STATISTICS
-------------------------
Mean Response Time:    {stats['mean_response_time']:.3f}s
Median Response Time:  {stats['median_response_time']:.3f}s
Min Response Time:     {stats['min_response_time']:.3f}s
Max Response Time:     {stats['max_response_time']:.3f}s
P95 Response Time:     {stats['p95_response_time']:.3f}s
P99 Response Time:     {stats['p99_response_time']:.3f}s

{'='*70}
"""
    return report


if __name__ == "__main__":
    # Run load test
    print("Starting performance test...\n")
    results = run_load_test()

    # Generate and print report
    report = generate_report(results)
    print(report)

    # Save report to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"performance_report_{timestamp}.txt"

    with open(report_file, 'w') as f:
        f.write(report)

    print("\n✅ Performance test complete!")
    print(f"📊 Report saved to: {report_file}")
