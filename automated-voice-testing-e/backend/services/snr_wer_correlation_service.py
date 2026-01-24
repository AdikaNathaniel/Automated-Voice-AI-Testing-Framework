"""
SNR-WER Correlation Report Service for audio quality analysis.

This service generates reports correlating Signal-to-Noise
Ratio (SNR) to Word Error Rate (WER) for voice AI testing.

Key features:
- Data recording
- Correlation calculation
- Report generation
- Statistical analysis

Example:
    >>> service = SNRWERCorrelationService()
    >>> service.record_measurement(25.0, 0.05)
    >>> service.record_measurement(15.0, 0.15)
    >>> report = service.generate_report()
    >>> print(report['correlation'])
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import math


class SNRWERCorrelationService:
    """
    Service for SNR-WER correlation analysis.

    Provides data recording, correlation calculation,
    report generation, and statistical analysis.

    Example:
        >>> service = SNRWERCorrelationService()
        >>> service.record_measurement(20.0, 0.10)
        >>> stats = service.get_statistics()
    """

    def __init__(self):
        """Initialize the SNR-WER correlation service."""
        self._measurements: List[Dict[str, Any]] = []
        self._snr_ranges = [
            (0, 10, "Very Low"),
            (10, 20, "Low"),
            (20, 30, "Medium"),
            (30, 40, "High"),
            (40, 100, "Very High")
        ]

    def record_measurement(
        self,
        snr: float,
        wer: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Record a SNR-WER measurement.

        Args:
            snr: Signal-to-Noise Ratio in dB
            wer: Word Error Rate (0-1)
            metadata: Optional additional metadata

        Returns:
            Dictionary with recorded measurement

        Example:
            >>> result = service.record_measurement(25.0, 0.08)
        """
        measurement_id = str(uuid.uuid4())
        now = datetime.utcnow()

        measurement = {
            'id': measurement_id,
            'snr': snr,
            'wer': wer,
            'metadata': metadata or {},
            'recorded_at': now.isoformat()
        }
        self._measurements.append(measurement)

        return {
            'id': measurement_id,
            'snr': snr,
            'wer': wer,
            'recorded': True
        }

    def record_batch(
        self,
        measurements: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Record multiple measurements at once.

        Args:
            measurements: List of {snr, wer} dictionaries

        Returns:
            Dictionary with batch recording result

        Example:
            >>> result = service.record_batch([
            ...     {'snr': 25.0, 'wer': 0.05},
            ...     {'snr': 15.0, 'wer': 0.15}
            ... ])
        """
        recorded = []
        for m in measurements:
            result = self.record_measurement(
                m.get('snr', 0),
                m.get('wer', 0),
                m.get('metadata')
            )
            recorded.append(result['id'])

        return {
            'count': len(recorded),
            'ids': recorded,
            'recorded': True
        }

    def get_measurements(
        self,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recorded measurements.

        Args:
            limit: Optional limit on results

        Returns:
            List of measurements

        Example:
            >>> measurements = service.get_measurements(limit=100)
        """
        if limit:
            return self._measurements[-limit:]
        return self._measurements.copy()

    def clear_measurements(self) -> Dict[str, Any]:
        """
        Clear all recorded measurements.

        Returns:
            Dictionary with clear result

        Example:
            >>> result = service.clear_measurements()
        """
        count = len(self._measurements)
        self._measurements = []

        return {
            'cleared': count,
            'success': True
        }

    def calculate_correlation(self) -> Dict[str, Any]:
        """
        Calculate Pearson correlation coefficient.

        Returns:
            Dictionary with correlation coefficient

        Example:
            >>> corr = service.calculate_correlation()
        """
        if len(self._measurements) < 2:
            return {
                'correlation': 0.0,
                'error': 'Insufficient data'
            }

        snr_values = [m['snr'] for m in self._measurements]
        wer_values = [m['wer'] for m in self._measurements]

        n = len(snr_values)
        mean_snr = sum(snr_values) / n
        mean_wer = sum(wer_values) / n

        # Calculate covariance and standard deviations
        covariance = sum(
            (snr_values[i] - mean_snr) * (wer_values[i] - mean_wer)
            for i in range(n)
        ) / n

        std_snr = math.sqrt(
            sum((x - mean_snr) ** 2 for x in snr_values) / n
        )
        std_wer = math.sqrt(
            sum((y - mean_wer) ** 2 for y in wer_values) / n
        )

        if std_snr == 0 or std_wer == 0:
            return {
                'correlation': 0.0,
                'error': 'Zero variance'
            }

        correlation = covariance / (std_snr * std_wer)

        return {
            'correlation': correlation,
            'n': n,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def calculate_regression(self) -> Dict[str, Any]:
        """
        Calculate linear regression coefficients.

        Returns:
            Dictionary with slope and intercept

        Example:
            >>> reg = service.calculate_regression()
        """
        if len(self._measurements) < 2:
            return {
                'slope': 0.0,
                'intercept': 0.0,
                'error': 'Insufficient data'
            }

        snr_values = [m['snr'] for m in self._measurements]
        wer_values = [m['wer'] for m in self._measurements]

        n = len(snr_values)
        mean_snr = sum(snr_values) / n
        mean_wer = sum(wer_values) / n

        # Calculate slope
        numerator = sum(
            (snr_values[i] - mean_snr) * (wer_values[i] - mean_wer)
            for i in range(n)
        )
        denominator = sum(
            (x - mean_snr) ** 2 for x in snr_values
        )

        if denominator == 0:
            return {
                'slope': 0.0,
                'intercept': mean_wer,
                'error': 'Zero variance in SNR'
            }

        slope = numerator / denominator
        intercept = mean_wer - slope * mean_snr

        return {
            'slope': slope,
            'intercept': intercept,
            'equation': f'WER = {slope:.4f} * SNR + {intercept:.4f}'
        }

    def get_r_squared(self) -> Dict[str, Any]:
        """
        Calculate R-squared (coefficient of determination).

        Returns:
            Dictionary with R-squared value

        Example:
            >>> r2 = service.get_r_squared()
        """
        corr_result = self.calculate_correlation()
        correlation = corr_result.get('correlation', 0)

        r_squared = correlation ** 2

        return {
            'r_squared': r_squared,
            'correlation': correlation,
            'variance_explained': f'{r_squared * 100:.1f}%'
        }

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive correlation report.

        Returns:
            Dictionary with full report

        Example:
            >>> report = service.generate_report()
        """
        correlation = self.calculate_correlation()
        regression = self.calculate_regression()
        r_squared = self.get_r_squared()
        statistics = self.get_statistics()

        return {
            'report_id': str(uuid.uuid4()),
            'generated_at': datetime.utcnow().isoformat(),
            'measurement_count': len(self._measurements),
            'correlation': correlation,
            'regression': regression,
            'r_squared': r_squared,
            'statistics': statistics
        }

    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate brief summary of correlation.

        Returns:
            Dictionary with summary

        Example:
            >>> summary = service.generate_summary()
        """
        corr = self.calculate_correlation().get('correlation', 0)
        stats = self.get_statistics()

        # Interpret correlation
        if abs(corr) >= 0.7:
            strength = 'strong'
        elif abs(corr) >= 0.4:
            strength = 'moderate'
        else:
            strength = 'weak'

        direction = 'negative' if corr < 0 else 'positive'

        return {
            'measurement_count': len(self._measurements),
            'correlation': corr,
            'interpretation': f'{strength} {direction} correlation',
            'mean_snr': stats.get('mean_snr', 0),
            'mean_wer': stats.get('mean_wer', 0)
        }

    def export_csv(self) -> str:
        """
        Export measurements as CSV string.

        Returns:
            CSV formatted string

        Example:
            >>> csv_data = service.export_csv()
        """
        lines = ['id,snr,wer,recorded_at']

        for m in self._measurements:
            line = f"{m['id']},{m['snr']},{m['wer']},{m['recorded_at']}"
            lines.append(line)

        return '\n'.join(lines)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistical summary of measurements.

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = service.get_statistics()
        """
        if not self._measurements:
            return {
                'count': 0,
                'mean_snr': 0,
                'mean_wer': 0
            }

        snr_values = [m['snr'] for m in self._measurements]
        wer_values = [m['wer'] for m in self._measurements]

        n = len(self._measurements)

        return {
            'count': n,
            'mean_snr': sum(snr_values) / n,
            'mean_wer': sum(wer_values) / n,
            'min_snr': min(snr_values),
            'max_snr': max(snr_values),
            'min_wer': min(wer_values),
            'max_wer': max(wer_values),
            'std_snr': self._std(snr_values),
            'std_wer': self._std(wer_values)
        }

    def group_by_snr_range(self) -> Dict[str, Any]:
        """
        Group measurements by SNR range.

        Returns:
            Dictionary with grouped data

        Example:
            >>> groups = service.group_by_snr_range()
        """
        groups = {}

        for low, high, label in self._snr_ranges:
            measurements = [
                m for m in self._measurements
                if low <= m['snr'] < high
            ]

            if measurements:
                wer_values = [m['wer'] for m in measurements]
                groups[label] = {
                    'range': f'{low}-{high} dB',
                    'count': len(measurements),
                    'mean_wer': sum(wer_values) / len(wer_values),
                    'min_wer': min(wer_values),
                    'max_wer': max(wer_values)
                }

        return {
            'groups': groups,
            'total_measurements': len(self._measurements)
        }

    def get_percentiles(self) -> Dict[str, Any]:
        """
        Get percentile values for SNR and WER.

        Returns:
            Dictionary with percentiles

        Example:
            >>> percentiles = service.get_percentiles()
        """
        if not self._measurements:
            return {'error': 'No measurements'}

        snr_values = sorted([m['snr'] for m in self._measurements])
        wer_values = sorted([m['wer'] for m in self._measurements])

        return {
            'snr': {
                'p25': self._percentile(snr_values, 25),
                'p50': self._percentile(snr_values, 50),
                'p75': self._percentile(snr_values, 75),
                'p90': self._percentile(snr_values, 90)
            },
            'wer': {
                'p25': self._percentile(wer_values, 25),
                'p50': self._percentile(wer_values, 50),
                'p75': self._percentile(wer_values, 75),
                'p90': self._percentile(wer_values, 90)
            }
        }

    def get_scatter_data(self) -> Dict[str, Any]:
        """
        Get data formatted for scatter plot.

        Returns:
            Dictionary with scatter plot data

        Example:
            >>> scatter = service.get_scatter_data()
        """
        points = [
            {'x': m['snr'], 'y': m['wer']}
            for m in self._measurements
        ]

        return {
            'points': points,
            'x_label': 'SNR (dB)',
            'y_label': 'WER',
            'count': len(points)
        }

    def get_trend_line(self) -> Dict[str, Any]:
        """
        Get trend line data for visualization.

        Returns:
            Dictionary with trend line points

        Example:
            >>> trend = service.get_trend_line()
        """
        if not self._measurements:
            return {'points': []}

        regression = self.calculate_regression()
        slope = regression.get('slope', 0)
        intercept = regression.get('intercept', 0)

        snr_values = [m['snr'] for m in self._measurements]
        min_snr = min(snr_values)
        max_snr = max(snr_values)

        # Generate trend line points
        points = [
            {
                'x': min_snr,
                'y': slope * min_snr + intercept
            },
            {
                'x': max_snr,
                'y': slope * max_snr + intercept
            }
        ]

        return {
            'points': points,
            'slope': slope,
            'intercept': intercept
        }

    def get_histogram_data(
        self,
        bins: int = 10
    ) -> Dict[str, Any]:
        """
        Get histogram data for SNR and WER.

        Args:
            bins: Number of histogram bins

        Returns:
            Dictionary with histogram data

        Example:
            >>> histogram = service.get_histogram_data(bins=10)
        """
        if not self._measurements:
            return {'snr_histogram': [], 'wer_histogram': []}

        snr_values = [m['snr'] for m in self._measurements]
        wer_values = [m['wer'] for m in self._measurements]

        return {
            'snr_histogram': self._histogram(snr_values, bins),
            'wer_histogram': self._histogram(wer_values, bins)
        }

    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if not values:
            return 0.0
        n = len(values)
        mean = sum(values) / n
        variance = sum((x - mean) ** 2 for x in values) / n
        return math.sqrt(variance)

    def _percentile(self, values: List[float], p: int) -> float:
        """Calculate percentile value."""
        if not values:
            return 0.0
        k = (len(values) - 1) * p / 100
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return values[int(k)]
        return values[int(f)] * (c - k) + values[int(c)] * (k - f)

    def _histogram(
        self,
        values: List[float],
        bins: int
    ) -> List[Dict[str, Any]]:
        """Generate histogram bins."""
        if not values:
            return []

        min_val = min(values)
        max_val = max(values)
        bin_width = (max_val - min_val) / bins if max_val != min_val else 1

        histogram = []
        for i in range(bins):
            low = min_val + i * bin_width
            high = low + bin_width
            count = sum(1 for v in values if low <= v < high)
            if i == bins - 1:  # Include max in last bin
                count = sum(1 for v in values if low <= v <= high)

            histogram.append({
                'bin': i,
                'low': low,
                'high': high,
                'count': count
            })

        return histogram
