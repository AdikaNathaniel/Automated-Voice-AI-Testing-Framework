"""
Resource Utilization Monitoring Service for system metrics.

This service provides resource monitoring capabilities for
tracking CPU, memory, network, and disk usage.

Key features:
- CPU utilization monitoring
- Memory consumption tracking
- Network I/O monitoring
- Disk I/O monitoring

Example:
    >>> service = ResourceUtilizationService()
    >>> service.record_cpu_sample('api', 45.5)
    >>> usage = service.get_cpu_usage()
    >>> print(f"CPU: {usage['average']}%")
"""

from typing import List, Dict, Any
from datetime import datetime
import statistics


class ResourceUtilizationService:
    """
    Service for resource utilization monitoring.

    Provides CPU, memory, network, and disk monitoring
    capabilities for system performance analysis.

    Example:
        >>> service = ResourceUtilizationService()
        >>> service.record_cpu_sample('worker', 75.0)
        >>> summary = service.get_resource_summary()
        >>> print(f"CPU avg: {summary['cpu']['average']}%")
    """

    def __init__(self):
        """Initialize the resource utilization service."""
        self._cpu_samples: Dict[str, List[Dict[str, Any]]] = {}
        self._memory_samples: Dict[str, List[Dict[str, Any]]] = {}
        self._network_samples: List[Dict[str, Any]] = []
        self._disk_samples: List[Dict[str, Any]] = []

    # CPU Utilization Methods

    def get_cpu_usage(self) -> Dict[str, Any]:
        """
        Get current CPU usage.

        Returns:
            Dictionary with CPU usage metrics

        Example:
            >>> usage = service.get_cpu_usage()
        """
        all_samples = []
        for service_samples in self._cpu_samples.values():
            all_samples.extend([s['value'] for s in service_samples])

        if not all_samples:
            return {
                'current': 0.0,
                'average': 0.0,
                'max': 0.0,
                'sample_count': 0
            }

        return {
            'current': float(all_samples[-1]) if all_samples else 0.0,
            'average': float(statistics.mean(all_samples)),
            'max': float(max(all_samples)),
            'sample_count': len(all_samples)
        }

    def get_cpu_per_service(self) -> Dict[str, Any]:
        """
        Get CPU usage per service.

        Returns:
            Dictionary with per-service CPU metrics

        Example:
            >>> per_service = service.get_cpu_per_service()
        """
        result = {}
        for service_name, samples in self._cpu_samples.items():
            values = [s['value'] for s in samples]
            if values:
                result[service_name] = {
                    'current': float(values[-1]),
                    'average': float(statistics.mean(values)),
                    'max': float(max(values)),
                    'sample_count': len(values)
                }
        return result

    def record_cpu_sample(
        self,
        service_name: str,
        usage_percent: float
    ) -> Dict[str, Any]:
        """
        Record a CPU sample.

        Args:
            service_name: Name of the service
            usage_percent: CPU usage percentage

        Returns:
            Dictionary with recorded sample

        Example:
            >>> service.record_cpu_sample('api', 65.5)
        """
        if service_name not in self._cpu_samples:
            self._cpu_samples[service_name] = []

        sample = {
            'service': service_name,
            'value': usage_percent,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._cpu_samples[service_name].append(sample)

        return {
            'recorded': True,
            'sample': sample,
            'total_samples': len(self._cpu_samples[service_name])
        }

    def get_cpu_history(
        self,
        service_name: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get CPU usage history.

        Args:
            service_name: Optional service filter
            limit: Maximum results

        Returns:
            List of CPU samples

        Example:
            >>> history = service.get_cpu_history('api')
        """
        if service_name:
            samples = self._cpu_samples.get(service_name, [])
        else:
            samples = []
            for service_samples in self._cpu_samples.values():
                samples.extend(service_samples)
            samples.sort(key=lambda x: x['timestamp'])

        return samples[-limit:]

    # Memory Consumption Methods

    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage.

        Returns:
            Dictionary with memory usage metrics

        Example:
            >>> usage = service.get_memory_usage()
        """
        all_samples = []
        for service_samples in self._memory_samples.values():
            all_samples.extend([s['value'] for s in service_samples])

        if not all_samples:
            return {
                'current_mb': 0.0,
                'average_mb': 0.0,
                'max_mb': 0.0,
                'sample_count': 0
            }

        return {
            'current_mb': float(all_samples[-1]) if all_samples else 0.0,
            'average_mb': float(statistics.mean(all_samples)),
            'max_mb': float(max(all_samples)),
            'sample_count': len(all_samples)
        }

    def get_memory_per_service(self) -> Dict[str, Any]:
        """
        Get memory usage per service.

        Returns:
            Dictionary with per-service memory metrics

        Example:
            >>> per_service = service.get_memory_per_service()
        """
        result = {}
        for service_name, samples in self._memory_samples.items():
            values = [s['value'] for s in samples]
            if values:
                result[service_name] = {
                    'current_mb': float(values[-1]),
                    'average_mb': float(statistics.mean(values)),
                    'max_mb': float(max(values)),
                    'sample_count': len(values)
                }
        return result

    def record_memory_sample(
        self,
        service_name: str,
        usage_mb: float
    ) -> Dict[str, Any]:
        """
        Record a memory sample.

        Args:
            service_name: Name of the service
            usage_mb: Memory usage in MB

        Returns:
            Dictionary with recorded sample

        Example:
            >>> service.record_memory_sample('api', 512.5)
        """
        if service_name not in self._memory_samples:
            self._memory_samples[service_name] = []

        sample = {
            'service': service_name,
            'value': usage_mb,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._memory_samples[service_name].append(sample)

        return {
            'recorded': True,
            'sample': sample,
            'total_samples': len(self._memory_samples[service_name])
        }

    def get_memory_history(
        self,
        service_name: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get memory usage history.

        Args:
            service_name: Optional service filter
            limit: Maximum results

        Returns:
            List of memory samples

        Example:
            >>> history = service.get_memory_history('api')
        """
        if service_name:
            samples = self._memory_samples.get(service_name, [])
        else:
            samples = []
            for service_samples in self._memory_samples.values():
                samples.extend(service_samples)
            samples.sort(key=lambda x: x['timestamp'])

        return samples[-limit:]

    # Network I/O Methods

    def get_network_io(self) -> Dict[str, Any]:
        """
        Get current network I/O metrics.

        Returns:
            Dictionary with network I/O metrics

        Example:
            >>> io = service.get_network_io()
        """
        if not self._network_samples:
            return {
                'bytes_sent': 0,
                'bytes_received': 0,
                'packets_sent': 0,
                'packets_received': 0
            }

        latest = self._network_samples[-1]
        return {
            'bytes_sent': latest.get('bytes_sent', 0),
            'bytes_received': latest.get('bytes_received', 0),
            'packets_sent': latest.get('packets_sent', 0),
            'packets_received': latest.get('packets_received', 0),
            'timestamp': latest.get('timestamp')
        }

    def record_network_sample(
        self,
        bytes_sent: int,
        bytes_received: int,
        packets_sent: int = 0,
        packets_received: int = 0
    ) -> Dict[str, Any]:
        """
        Record a network I/O sample.

        Args:
            bytes_sent: Bytes sent
            bytes_received: Bytes received
            packets_sent: Packets sent
            packets_received: Packets received

        Returns:
            Dictionary with recorded sample

        Example:
            >>> service.record_network_sample(1024, 2048)
        """
        sample = {
            'bytes_sent': bytes_sent,
            'bytes_received': bytes_received,
            'packets_sent': packets_sent,
            'packets_received': packets_received,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._network_samples.append(sample)

        return {
            'recorded': True,
            'sample': sample,
            'total_samples': len(self._network_samples)
        }

    def get_network_throughput(self) -> Dict[str, Any]:
        """
        Get network throughput metrics.

        Returns:
            Dictionary with throughput metrics

        Example:
            >>> throughput = service.get_network_throughput()
        """
        if len(self._network_samples) < 2:
            return {
                'send_rate_bps': 0.0,
                'receive_rate_bps': 0.0,
                'sample_count': len(self._network_samples)
            }

        total_sent = sum(s['bytes_sent'] for s in self._network_samples)
        total_received = sum(s['bytes_received'] for s in self._network_samples)

        return {
            'total_sent_bytes': total_sent,
            'total_received_bytes': total_received,
            'avg_sent_bytes': float(total_sent / len(self._network_samples)),
            'avg_received_bytes': float(total_received / len(self._network_samples)),
            'sample_count': len(self._network_samples)
        }

    # Disk I/O Methods

    def get_disk_io(self) -> Dict[str, Any]:
        """
        Get current disk I/O metrics.

        Returns:
            Dictionary with disk I/O metrics

        Example:
            >>> io = service.get_disk_io()
        """
        if not self._disk_samples:
            return {
                'read_bytes': 0,
                'write_bytes': 0,
                'read_ops': 0,
                'write_ops': 0
            }

        latest = self._disk_samples[-1]
        return {
            'read_bytes': latest.get('read_bytes', 0),
            'write_bytes': latest.get('write_bytes', 0),
            'read_ops': latest.get('read_ops', 0),
            'write_ops': latest.get('write_ops', 0),
            'timestamp': latest.get('timestamp')
        }

    def record_disk_sample(
        self,
        read_bytes: int,
        write_bytes: int,
        read_ops: int = 0,
        write_ops: int = 0
    ) -> Dict[str, Any]:
        """
        Record a disk I/O sample.

        Args:
            read_bytes: Bytes read
            write_bytes: Bytes written
            read_ops: Read operations
            write_ops: Write operations

        Returns:
            Dictionary with recorded sample

        Example:
            >>> service.record_disk_sample(1024, 2048)
        """
        sample = {
            'read_bytes': read_bytes,
            'write_bytes': write_bytes,
            'read_ops': read_ops,
            'write_ops': write_ops,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._disk_samples.append(sample)

        return {
            'recorded': True,
            'sample': sample,
            'total_samples': len(self._disk_samples)
        }

    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Get disk usage metrics.

        Returns:
            Dictionary with disk usage metrics

        Example:
            >>> usage = service.get_disk_usage()
        """
        if not self._disk_samples:
            return {
                'total_read_bytes': 0,
                'total_write_bytes': 0,
                'total_read_ops': 0,
                'total_write_ops': 0,
                'sample_count': 0
            }

        total_read = sum(s['read_bytes'] for s in self._disk_samples)
        total_write = sum(s['write_bytes'] for s in self._disk_samples)
        total_read_ops = sum(s['read_ops'] for s in self._disk_samples)
        total_write_ops = sum(s['write_ops'] for s in self._disk_samples)

        return {
            'total_read_bytes': total_read,
            'total_write_bytes': total_write,
            'total_read_ops': total_read_ops,
            'total_write_ops': total_write_ops,
            'sample_count': len(self._disk_samples)
        }

    # Reporting Methods

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate resource utilization report.

        Returns:
            Dictionary with full resource report

        Example:
            >>> report = service.generate_report()
        """
        return {
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'network': self.get_network_io(),
            'disk': self.get_disk_io(),
            'per_service': {
                'cpu': self.get_cpu_per_service(),
                'memory': self.get_memory_per_service()
            },
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_resource_summary(self) -> Dict[str, Any]:
        """
        Get resource utilization summary.

        Returns:
            Dictionary with resource summary

        Example:
            >>> summary = service.get_resource_summary()
        """
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        network = self.get_network_io()
        disk = self.get_disk_io()

        # Determine overall health
        cpu_avg = cpu.get('average', 0)
        memory_avg = memory.get('average_mb', 0)

        if cpu_avg > 90 or memory_avg > 1000:
            health = 'critical'
        elif cpu_avg > 70 or memory_avg > 750:
            health = 'warning'
        else:
            health = 'healthy'

        return {
            'health': health,
            'cpu': {
                'average': cpu.get('average', 0),
                'max': cpu.get('max', 0)
            },
            'memory': {
                'average_mb': memory.get('average_mb', 0),
                'max_mb': memory.get('max_mb', 0)
            },
            'network': {
                'bytes_sent': network.get('bytes_sent', 0),
                'bytes_received': network.get('bytes_received', 0)
            },
            'disk': {
                'read_bytes': disk.get('read_bytes', 0),
                'write_bytes': disk.get('write_bytes', 0)
            }
        }
