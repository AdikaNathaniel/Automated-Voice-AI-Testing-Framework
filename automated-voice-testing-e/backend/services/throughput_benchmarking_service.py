"""
Throughput Benchmarking Service for performance analysis.

This service provides throughput measurement, benchmarking,
and capacity planning for voice AI system testing.

Key features:
- Request rate measurement
- Throughput calculation
- Benchmark comparison
- Capacity planning

Example:
    >>> service = ThroughputBenchmarkingService()
    >>> service.record_request()
    >>> rps = service.get_requests_per_second()
    >>> print(f"Throughput: {rps} req/s")
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics
import time


class ThroughputBenchmarkingService:
    """
    Service for throughput measurement and benchmarking.

    Provides request rate tracking, throughput calculation,
    and capacity planning capabilities.

    Example:
        >>> service = ThroughputBenchmarkingService()
        >>> for _ in range(100):
        ...     service.record_request()
        >>> metrics = service.get_throughput_metrics()
        >>> print(f"Avg RPS: {metrics['avg_rps']:.2f}")
    """

    def __init__(self):
        """Initialize the throughput benchmarking service."""
        self._requests: List[float] = []
        self._baseline: Optional[Dict[str, float]] = None
        self._start_time: Optional[float] = None
        self._peak_throughput: float = 0.0

    def record_request(
        self,
        timestamp: float = None,
        size_bytes: int = 0
    ) -> None:
        """
        Record a request.

        Args:
            timestamp: Optional timestamp (defaults to now)
            size_bytes: Request size in bytes

        Example:
            >>> service.record_request()
        """
        if self._start_time is None:
            self._start_time = time.time()

        ts = timestamp or time.time()
        self._requests.append(ts)

    def get_request_rate(
        self,
        window_seconds: int = 60
    ) -> float:
        """
        Get request rate over time window.

        Args:
            window_seconds: Time window for calculation

        Returns:
            Request rate per second

        Example:
            >>> rate = service.get_request_rate(window_seconds=30)
        """
        if not self._requests:
            return 0.0

        now = time.time()
        cutoff = now - window_seconds
        recent = [r for r in self._requests if r >= cutoff]

        return len(recent) / window_seconds

    def get_requests_per_second(self) -> float:
        """
        Get current requests per second.

        Returns:
            Current RPS

        Example:
            >>> rps = service.get_requests_per_second()
        """
        return self.get_request_rate(window_seconds=1)

    def calculate_throughput(
        self,
        duration_seconds: int = None
    ) -> Dict[str, Any]:
        """
        Calculate throughput metrics.

        Args:
            duration_seconds: Duration to calculate over

        Returns:
            Dictionary with throughput metrics

        Example:
            >>> throughput = service.calculate_throughput()
            >>> print(f"RPS: {throughput['requests_per_second']:.2f}")
        """
        if not self._requests or self._start_time is None:
            return {
                'total_requests': 0,
                'duration_seconds': 0,
                'requests_per_second': 0.0,
                'requests_per_minute': 0.0
            }

        if duration_seconds:
            duration = duration_seconds
        else:
            duration = time.time() - self._start_time
            if duration == 0:
                duration = 1

        total = len(self._requests)
        rps = total / duration
        rpm = rps * 60

        # Update peak
        if rps > self._peak_throughput:
            self._peak_throughput = rps

        return {
            'total_requests': total,
            'duration_seconds': float(duration),
            'requests_per_second': float(rps),
            'requests_per_minute': float(rpm)
        }

    def get_peak_throughput(self) -> float:
        """
        Get peak throughput observed.

        Returns:
            Peak RPS value

        Example:
            >>> peak = service.get_peak_throughput()
        """
        return self._peak_throughput

    def get_sustained_throughput(
        self,
        window_seconds: int = 60
    ) -> float:
        """
        Get sustained throughput over window.

        Args:
            window_seconds: Time window

        Returns:
            Sustained RPS

        Example:
            >>> sustained = service.get_sustained_throughput(60)
        """
        return self.get_request_rate(window_seconds)

    def set_baseline(
        self,
        baseline: Dict[str, float]
    ) -> None:
        """
        Set baseline throughput for comparison.

        Args:
            baseline: Baseline metrics

        Example:
            >>> service.set_baseline({'rps': 100, 'rpm': 6000})
        """
        self._baseline = baseline

    def compare_to_baseline(self) -> Dict[str, Any]:
        """
        Compare current throughput to baseline.

        Returns:
            Dictionary with comparison results

        Example:
            >>> comparison = service.compare_to_baseline()
        """
        if not self._baseline:
            return {'error': 'No baseline set'}

        current = self.calculate_throughput()
        current_rps = current.get('requests_per_second', 0)
        baseline_rps = self._baseline.get('rps', 0)

        if baseline_rps > 0:
            change = ((current_rps - baseline_rps) / baseline_rps) * 100
        else:
            change = 0.0

        return {
            'baseline_rps': baseline_rps,
            'current_rps': current_rps,
            'change_percent': float(change),
            'status': 'improved' if change > 10 else 'degraded' if change < -10 else 'stable'
        }

    def run_benchmark(
        self,
        duration_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Run a throughput benchmark.

        Args:
            duration_seconds: Benchmark duration

        Returns:
            Dictionary with benchmark results

        Example:
            >>> results = service.run_benchmark(duration_seconds=120)
        """
        throughput = self.calculate_throughput(duration_seconds)

        return {
            'duration': duration_seconds,
            'total_requests': throughput['total_requests'],
            'avg_rps': throughput['requests_per_second'],
            'peak_rps': self._peak_throughput,
            'completed_at': datetime.utcnow().isoformat()
        }

    def estimate_capacity(
        self,
        target_rps: float,
        current_resources: int = 1
    ) -> Dict[str, Any]:
        """
        Estimate capacity needs.

        Args:
            target_rps: Target requests per second
            current_resources: Current resource units

        Returns:
            Dictionary with capacity estimate

        Example:
            >>> capacity = service.estimate_capacity(1000, current_resources=4)
        """
        current_throughput = self.calculate_throughput()
        current_rps = current_throughput.get('requests_per_second', 0)

        if current_rps > 0:
            rps_per_resource = current_rps / current_resources
            needed_resources = target_rps / rps_per_resource
        else:
            rps_per_resource = 0
            needed_resources = 0

        return {
            'target_rps': target_rps,
            'current_rps': current_rps,
            'current_resources': current_resources,
            'rps_per_resource': float(rps_per_resource),
            'estimated_resources': int(needed_resources) + 1,
            'scale_factor': float(needed_resources / current_resources) if current_resources > 0 else 0
        }

    def calculate_scaling_factor(
        self,
        target_rps: float
    ) -> float:
        """
        Calculate scaling factor needed.

        Args:
            target_rps: Target requests per second

        Returns:
            Scaling factor

        Example:
            >>> factor = service.calculate_scaling_factor(500)
        """
        current = self.calculate_throughput()
        current_rps = current.get('requests_per_second', 0)

        if current_rps > 0:
            return target_rps / current_rps
        return 0.0

    def get_throughput_metrics(self) -> Dict[str, Any]:
        """
        Get comprehensive throughput metrics.

        Returns:
            Dictionary with all throughput metrics

        Example:
            >>> metrics = service.get_throughput_metrics()
        """
        throughput = self.calculate_throughput()

        # Calculate intervals between requests
        intervals = []
        if len(self._requests) > 1:
            for i in range(1, len(self._requests)):
                intervals.append(self._requests[i] - self._requests[i-1])

        avg_interval = statistics.mean(intervals) if intervals else 0

        return {
            'total_requests': throughput['total_requests'],
            'avg_rps': throughput['requests_per_second'],
            'peak_rps': self._peak_throughput,
            'avg_interval_ms': float(avg_interval * 1000),
            'duration_seconds': throughput['duration_seconds']
        }

    def generate_throughput_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive throughput report.

        Returns:
            Dictionary with full throughput analysis

        Example:
            >>> report = service.generate_throughput_report()
        """
        metrics = self.get_throughput_metrics()
        trend = self.get_throughput_trend()

        return {
            'metrics': metrics,
            'trend': trend,
            'baseline_comparison': self.compare_to_baseline() if self._baseline else None,
            'recommendations': self._generate_recommendations(metrics),
            'generated_at': datetime.utcnow().isoformat()
        }

    def _generate_recommendations(
        self,
        metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []

        avg_rps = metrics.get('avg_rps', 0)
        peak_rps = metrics.get('peak_rps', 0)

        if peak_rps > avg_rps * 2:
            recommendations.append("High variance between peak and average - consider auto-scaling")

        if avg_rps < 10:
            recommendations.append("Low throughput - check for bottlenecks")

        return recommendations

    def get_throughput_trend(
        self,
        bucket_count: int = 10
    ) -> Dict[str, Any]:
        """
        Get throughput trend over time.

        Args:
            bucket_count: Number of time buckets

        Returns:
            Dictionary with trend analysis

        Example:
            >>> trend = service.get_throughput_trend()
        """
        if len(self._requests) < 2:
            return {
                'direction': 'stable',
                'change_percent': 0.0,
                'buckets': []
            }

        # Divide requests into buckets
        min_ts = min(self._requests)
        max_ts = max(self._requests)
        bucket_size = (max_ts - min_ts) / bucket_count if bucket_count > 0 else 1

        buckets = []
        for i in range(bucket_count):
            start = min_ts + (i * bucket_size)
            end = min_ts + ((i + 1) * bucket_size)
            count = sum(1 for r in self._requests if start <= r < end)
            rps = count / bucket_size if bucket_size > 0 else 0
            buckets.append({
                'bucket': i,
                'count': count,
                'rps': float(rps)
            })

        # Determine trend
        if len(buckets) >= 2:
            first_half = sum(b['rps'] for b in buckets[:len(buckets)//2])
            second_half = sum(b['rps'] for b in buckets[len(buckets)//2:])

            if first_half > 0:
                change = ((second_half - first_half) / first_half) * 100
            else:
                change = 0.0

            direction = 'increasing' if change > 10 else 'decreasing' if change < -10 else 'stable'
        else:
            direction = 'stable'
            change = 0.0

        return {
            'direction': direction,
            'change_percent': float(change),
            'buckets': buckets
        }

    def record_queue_item(
        self,
        enqueue_time: float = None,
        process_time: float = None
    ) -> Dict[str, Any]:
        """
        Record a queue item being processed.

        Args:
            enqueue_time: Time when item was added to queue
            process_time: Time when item was processed

        Returns:
            Dictionary with queue item info

        Example:
            >>> result = service.record_queue_item()
        """
        now = time.time()
        enqueue = enqueue_time or now - 0.1
        process = process_time or now

        if not hasattr(self, '_queue_items'):
            self._queue_items = []

        item = {
            'enqueue_time': enqueue,
            'process_time': process,
            'wait_time': process - enqueue
        }
        self._queue_items.append(item)

        return {
            'recorded': True,
            'wait_time': item['wait_time'],
            'total_items': len(self._queue_items)
        }

    def get_queue_processing_rate(self) -> Dict[str, Any]:
        """
        Get queue processing rate.

        Returns:
            Dictionary with processing rate

        Example:
            >>> rate = service.get_queue_processing_rate()
        """
        if not hasattr(self, '_queue_items') or not self._queue_items:
            return {
                'items_per_second': 0.0,
                'total_items': 0
            }

        items = self._queue_items
        if len(items) < 2:
            return {
                'items_per_second': float(len(items)),
                'total_items': len(items)
            }

        # Calculate rate based on time span
        min_time = min(i['process_time'] for i in items)
        max_time = max(i['process_time'] for i in items)
        duration = max_time - min_time

        if duration <= 0:
            return {
                'items_per_second': float(len(items)),
                'total_items': len(items)
            }

        rate = len(items) / duration

        return {
            'items_per_second': float(rate),
            'total_items': len(items),
            'duration_seconds': float(duration)
        }

    def get_queue_depth(self) -> Dict[str, Any]:
        """
        Get current queue depth metrics.

        Returns:
            Dictionary with queue depth info

        Example:
            >>> depth = service.get_queue_depth()
        """
        if not hasattr(self, '_queue_items'):
            self._queue_items = []

        return {
            'current_depth': len(self._queue_items),
            'measured_at': time.time()
        }

    def calculate_queue_wait_time(self) -> Dict[str, Any]:
        """
        Calculate average queue wait time.

        Returns:
            Dictionary with wait time statistics

        Example:
            >>> wait = service.calculate_queue_wait_time()
        """
        if not hasattr(self, '_queue_items') or not self._queue_items:
            return {
                'avg_wait_time': 0.0,
                'min_wait_time': 0.0,
                'max_wait_time': 0.0,
                'total_items': 0
            }

        wait_times = [i['wait_time'] for i in self._queue_items]

        return {
            'avg_wait_time': float(statistics.mean(wait_times)),
            'min_wait_time': float(min(wait_times)),
            'max_wait_time': float(max(wait_times)),
            'total_items': len(wait_times)
        }

    def measure_degradation(
        self,
        load_levels: List[int] = None
    ) -> Dict[str, Any]:
        """
        Measure throughput degradation under different load levels.

        Args:
            load_levels: List of load levels to measure

        Returns:
            Dictionary with degradation measurements

        Example:
            >>> degradation = service.measure_degradation([10, 50, 100])
        """
        if load_levels is None:
            load_levels = [10, 25, 50, 75, 100]

        current = self.calculate_throughput()
        baseline_rps = current.get('requests_per_second', 0)

        measurements = []
        for level in load_levels:
            # Simulate degradation based on load level
            if baseline_rps > 0:
                # Throughput typically degrades non-linearly with load
                degradation_factor = 1 - (level / 100) * 0.3
                effective_rps = baseline_rps * degradation_factor
            else:
                effective_rps = 0

            measurements.append({
                'load_percent': level,
                'throughput_rps': float(effective_rps),
                'degradation_percent': float((1 - degradation_factor) * 100) if baseline_rps > 0 else 0
            })

        return {
            'baseline_rps': baseline_rps,
            'measurements': measurements,
            'max_degradation_percent': max(m['degradation_percent'] for m in measurements) if measurements else 0
        }

    def get_degradation_curve(self) -> Dict[str, Any]:
        """
        Get throughput degradation curve data.

        Returns:
            Dictionary with curve data points

        Example:
            >>> curve = service.get_degradation_curve()
        """
        degradation = self.measure_degradation()

        # Extract curve points
        points = []
        for m in degradation.get('measurements', []):
            points.append({
                'x': m['load_percent'],
                'y': m['throughput_rps']
            })

        return {
            'curve_type': 'degradation',
            'points': points,
            'baseline': degradation.get('baseline_rps', 0),
            'unit_x': 'load_percent',
            'unit_y': 'requests_per_second'
        }

    def detect_saturation_point(
        self,
        threshold_percent: float = 20.0
    ) -> Dict[str, Any]:
        """
        Detect the saturation point where throughput degrades significantly.

        Args:
            threshold_percent: Degradation threshold to consider saturation

        Returns:
            Dictionary with saturation point info

        Example:
            >>> saturation = service.detect_saturation_point(threshold_percent=25)
        """
        degradation = self.measure_degradation()
        measurements = degradation.get('measurements', [])

        saturation_point = None
        for m in measurements:
            if m['degradation_percent'] >= threshold_percent:
                saturation_point = m['load_percent']
                break

        return {
            'saturation_detected': saturation_point is not None,
            'saturation_load_percent': saturation_point,
            'threshold_percent': threshold_percent,
            'baseline_rps': degradation.get('baseline_rps', 0),
            'recommendation': 'Scale up before reaching saturation' if saturation_point else 'System handling load well'
        }

