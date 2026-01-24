"""
Latency Percentile Tracking Service for performance analysis.

This service provides latency measurement, percentile calculations,
and latency analysis for voice AI system testing.

Key features:
- Latency measurement and recording
- Percentile calculations (p50, p90, p95, p99)
- Histogram generation
- Latency trend analysis

Example:
    >>> service = LatencyPercentileService()
    >>> service.record_latency(150.5)
    >>> p99 = service.get_p99()
    >>> print(f"P99 latency: {p99}ms")
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import statistics


class LatencyPercentileService:
    """
    Service for latency measurement and percentile tracking.

    Provides latency recording, percentile calculations, histogram
    generation, and latency analysis for performance monitoring.

    Example:
        >>> service = LatencyPercentileService()
        >>> for latency in [100, 150, 200, 250, 300]:
        ...     service.record_latency(latency)
        >>> stats = service.get_statistics()
        >>> print(f"Mean: {stats['mean']:.2f}ms")
    """

    def __init__(self):
        """Initialize the latency percentile service."""
        self._latencies: List[float] = []
        self._timestamps: List[str] = []
        self._baseline: Optional[Dict[str, float]] = None

    def record_latency(
        self,
        latency_ms: float,
        label: str = ""
    ) -> None:
        """
        Record a latency measurement.

        Args:
            latency_ms: Latency in milliseconds
            label: Optional label for the measurement

        Example:
            >>> service.record_latency(125.5, "api_call")
        """
        self._latencies.append(latency_ms)
        self._timestamps.append(datetime.utcnow().isoformat())

    def get_latencies(self) -> List[float]:
        """
        Get all recorded latencies.

        Returns:
            List of latency values in milliseconds

        Example:
            >>> latencies = service.get_latencies()
            >>> print(f"Recorded {len(latencies)} measurements")
        """
        return self._latencies.copy()

    def clear_latencies(self) -> None:
        """
        Clear all recorded latencies.

        Example:
            >>> service.clear_latencies()
        """
        self._latencies = []
        self._timestamps = []

    def calculate_percentile(
        self,
        percentile: float
    ) -> float:
        """
        Calculate a specific percentile.

        Args:
            percentile: Percentile to calculate (0-100)

        Returns:
            Latency value at the percentile

        Example:
            >>> p95 = service.calculate_percentile(95)
        """
        if not self._latencies:
            return 0.0

        sorted_latencies = sorted(self._latencies)
        index = int((percentile / 100) * (len(sorted_latencies) - 1))
        return sorted_latencies[index]

    def get_p50(self) -> float:
        """
        Get the 50th percentile (median) latency.

        Returns:
            P50 latency in milliseconds

        Example:
            >>> median = service.get_p50()
        """
        return self.calculate_percentile(50)

    def get_p90(self) -> float:
        """
        Get the 90th percentile latency.

        Returns:
            P90 latency in milliseconds

        Example:
            >>> p90 = service.get_p90()
        """
        return self.calculate_percentile(90)

    def get_p95(self) -> float:
        """
        Get the 95th percentile latency.

        Returns:
            P95 latency in milliseconds

        Example:
            >>> p95 = service.get_p95()
        """
        return self.calculate_percentile(95)

    def get_p99(self) -> float:
        """
        Get the 99th percentile latency.

        Returns:
            P99 latency in milliseconds

        Example:
            >>> p99 = service.get_p99()
        """
        return self.calculate_percentile(99)

    def get_all_percentiles(self) -> Dict[str, float]:
        """
        Get all common percentiles.

        Returns:
            Dictionary with p50, p90, p95, p99 values

        Example:
            >>> percentiles = service.get_all_percentiles()
            >>> print(f"P99: {percentiles['p99']}ms")
        """
        return {
            'p50': self.get_p50(),
            'p90': self.get_p90(),
            'p95': self.get_p95(),
            'p99': self.get_p99()
        }

    def generate_histogram(
        self,
        bucket_count: int = 10
    ) -> Dict[str, Any]:
        """
        Generate a histogram of latencies.

        Args:
            bucket_count: Number of buckets

        Returns:
            Dictionary with histogram data

        Example:
            >>> hist = service.generate_histogram(bucket_count=20)
            >>> for bucket in hist['buckets']:
            ...     print(f"{bucket['range']}: {bucket['count']}")
        """
        if not self._latencies:
            return {'buckets': [], 'total': 0}

        min_val = min(self._latencies)
        max_val = max(self._latencies)
        bucket_size = (max_val - min_val) / bucket_count if bucket_count > 0 else 1

        buckets = []
        for i in range(bucket_count):
            low = min_val + (i * bucket_size)
            high = min_val + ((i + 1) * bucket_size)
            count = sum(1 for latency in self._latencies if low <= latency < high)
            buckets.append({
                'range': f"{low:.1f}-{high:.1f}",
                'low': low,
                'high': high,
                'count': count
            })

        return {
            'buckets': buckets,
            'total': len(self._latencies),
            'bucket_size': bucket_size
        }

    def get_bucket_counts(
        self,
        boundaries: List[float]
    ) -> Dict[str, int]:
        """
        Get counts for custom bucket boundaries.

        Args:
            boundaries: List of bucket boundaries

        Returns:
            Dictionary with bucket counts

        Example:
            >>> counts = service.get_bucket_counts([0, 100, 200, 500])
        """
        if not boundaries:
            return {}

        counts = {}
        for i in range(len(boundaries) - 1):
            low = boundaries[i]
            high = boundaries[i + 1]
            key = f"{low}-{high}"
            counts[key] = sum(1 for latency in self._latencies if low <= latency < high)

        # Handle overflow
        last = boundaries[-1]
        counts[f"{last}+"] = sum(1 for latency in self._latencies if latency >= last)

        return counts

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get latency statistics.

        Returns:
            Dictionary with statistical measures

        Example:
            >>> stats = service.get_statistics()
            >>> print(f"Mean: {stats['mean']:.2f}ms")
        """
        if not self._latencies:
            return {
                'count': 0,
                'mean': 0.0,
                'median': 0.0,
                'min': 0.0,
                'max': 0.0,
                'stddev': 0.0
            }

        return {
            'count': len(self._latencies),
            'mean': statistics.mean(self._latencies),
            'median': statistics.median(self._latencies),
            'min': min(self._latencies),
            'max': max(self._latencies),
            'stddev': statistics.stdev(self._latencies) if len(self._latencies) > 1 else 0.0
        }

    def detect_outliers(
        self,
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect latency outliers using z-score.

        Args:
            threshold: Z-score threshold for outliers

        Returns:
            List of outlier measurements

        Example:
            >>> outliers = service.detect_outliers(threshold=3.0)
            >>> print(f"Found {len(outliers)} outliers")
        """
        if len(self._latencies) < 2:
            return []

        mean = statistics.mean(self._latencies)
        stddev = statistics.stdev(self._latencies)

        if stddev == 0:
            return []

        outliers = []
        for i, latency in enumerate(self._latencies):
            z_score = abs((latency - mean) / stddev)
            if z_score > threshold:
                outliers.append({
                    'index': i,
                    'value': latency,
                    'z_score': z_score,
                    'timestamp': self._timestamps[i] if i < len(self._timestamps) else None
                })

        return outliers

    def get_latency_trend(
        self,
        window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Get latency trend over time.

        Args:
            window_size: Size of moving average window

        Returns:
            Dictionary with trend analysis

        Example:
            >>> trend = service.get_latency_trend()
            >>> print(f"Direction: {trend['direction']}")
        """
        if len(self._latencies) < 2:
            return {
                'direction': 'stable',
                'change_percent': 0.0,
                'moving_averages': []
            }

        # Calculate moving averages
        moving_avgs = []
        for i in range(len(self._latencies) - window_size + 1):
            window = self._latencies[i:i + window_size]
            moving_avgs.append(statistics.mean(window))

        # Determine trend
        if len(moving_avgs) >= 2:
            first_half = statistics.mean(moving_avgs[:len(moving_avgs)//2])
            second_half = statistics.mean(moving_avgs[len(moving_avgs)//2:])
            change = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0

            if change > 10:
                direction = 'increasing'
            elif change < -10:
                direction = 'decreasing'
            else:
                direction = 'stable'
        else:
            direction = 'stable'
            change = 0.0

        return {
            'direction': direction,
            'change_percent': float(change),
            'moving_averages': moving_avgs
        }

    def generate_latency_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive latency report.

        Returns:
            Dictionary with full latency analysis

        Example:
            >>> report = service.generate_latency_report()
            >>> print(f"P99: {report['percentiles']['p99']}ms")
        """
        stats = self.get_statistics()
        percentiles = self.get_all_percentiles()
        trend = self.get_latency_trend()
        outliers = self.detect_outliers()

        return {
            'statistics': stats,
            'percentiles': percentiles,
            'trend': trend,
            'outlier_count': len(outliers),
            'histogram': self.generate_histogram(),
            'generated_at': datetime.utcnow().isoformat()
        }

    def compare_to_baseline(
        self,
        baseline: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compare current latencies to baseline.

        Args:
            baseline: Baseline percentile values

        Returns:
            Dictionary with comparison results

        Example:
            >>> baseline = {'p50': 100, 'p99': 500}
            >>> comparison = service.compare_to_baseline(baseline)
        """
        current = self.get_all_percentiles()
        comparisons = {}

        for key in ['p50', 'p90', 'p95', 'p99']:
            baseline_val = baseline.get(key, 0)
            current_val = current.get(key, 0)

            if baseline_val > 0:
                change = ((current_val - baseline_val) / baseline_val) * 100
            else:
                change = 0.0

            comparisons[key] = {
                'baseline': baseline_val,
                'current': current_val,
                'change_percent': float(change),
                'status': 'regression' if change > 10 else 'improvement' if change < -10 else 'stable'
            }

        return {
            'comparisons': comparisons,
            'overall_status': self._determine_overall_status(comparisons)
        }

    def _determine_overall_status(
        self,
        comparisons: Dict[str, Any]
    ) -> str:
        """Determine overall comparison status."""
        regressions = sum(
            1 for c in comparisons.values()
            if c.get('status') == 'regression'
        )
        improvements = sum(
            1 for c in comparisons.values()
            if c.get('status') == 'improvement'
        )

        if regressions > improvements:
            return 'regression'
        elif improvements > regressions:
            return 'improvement'
        return 'stable'

