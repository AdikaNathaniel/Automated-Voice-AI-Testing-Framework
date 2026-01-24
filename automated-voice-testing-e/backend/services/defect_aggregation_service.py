"""
Defect aggregation utilities for clustering and pattern detection (TASK-243).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple


@dataclass(slots=True)
class DefectCluster:
    """Grouped defects that share similar characteristics."""

    key: Tuple[str, Optional[str], Optional[str], str]
    category: str
    severity: Optional[str]
    test_case_id: Optional[str]
    defects: List[Any] = field(default_factory=list)
    count: int = 0
    first_detected: Optional[datetime] = None
    last_detected: Optional[datetime] = None


@dataclass(slots=True)
class DefectPatternSummary:
    """Aggregated statistics derived from defect clusters."""

    cluster_count: int
    category_counts: Dict[str, int]
    severity_counts: Dict[str, int]
    repeating_test_cases: List[str]


class DefectAggregationService:
    """
    Group similar defects and surface recurring patterns.
    """

    def __init__(self) -> None:
        pass

    def cluster(self, defects: Iterable[Any]) -> List[DefectCluster]:
        clusters: Dict[Tuple[str, Optional[str], Optional[str], str], DefectCluster] = {}

        for defect in defects:
            record = self._extract_defect(defect)
            key = (
                record["category"],
                record["severity"],
                record["test_case_id"],
                self._normalise_title(record["title"]),
            )

            cluster = clusters.get(key)
            if cluster is None:
                cluster = DefectCluster(
                    key=key,
                    category=record["category"],
                    severity=record["severity"],
                    test_case_id=record["test_case_id"],
                )
                clusters[key] = cluster

            cluster.defects.append(defect)
            cluster.count += 1
            cluster.first_detected = self._min_datetime(cluster.first_detected, record["detected_at"])
            cluster.last_detected = self._max_datetime(cluster.last_detected, record["detected_at"])

        return sorted(clusters.values(), key=lambda c: (-c.count, c.category or "", c.test_case_id or ""))

    def summarize_patterns(self, clusters: Iterable[DefectCluster]) -> DefectPatternSummary:
        clusters_list = list(clusters)
        category_counter: Counter[str] = Counter()
        severity_counter: Counter[str] = Counter()
        repeating_cases: set[str] = set()

        for cluster in clusters_list:
            count = cluster.count or len(cluster.defects)
            category = cluster.category or "unknown"
            category_counter[category] += count

            severity = cluster.severity or "unknown"
            severity_counter[severity] += count

            if cluster.test_case_id and count > 1:
                repeating_cases.add(cluster.test_case_id)

        return DefectPatternSummary(
            cluster_count=len(clusters_list),
            category_counts=dict(category_counter),
            severity_counts=dict(severity_counter),
            repeating_test_cases=sorted(repeating_cases),
        )

    @staticmethod
    def _extract_defect(defect: Any) -> Dict[str, Any]:
        def _get(attr: str) -> Any:
            if hasattr(defect, attr):
                return getattr(defect, attr)
            if isinstance(defect, dict):
                return defect.get(attr)
            return None

        return {
            "category": (_get("category") or "unknown").strip().lower(),
            "severity": (_get("severity") or "unknown").strip().lower(),
            "test_case_id": _get("test_case_id"),
            "title": _get("title") or "",
            "detected_at": _get("detected_at"),
        }

    @staticmethod
    def _normalise_title(title: str) -> str:
        tokens = re.findall(r"[a-z0-9]+", title.lower())
        stop_words = {
            "the",
            "a",
            "an",
            "to",
            "of",
            "and",
            "for",
            "on",
            "in",
            "due",
            "with",
            "by",
        }
        filtered = [token for token in tokens if token not in stop_words]
        if not filtered:
            return " ".join(tokens)
        return " ".join(sorted(filtered))

    @staticmethod
    def _min_datetime(current: Optional[datetime], candidate: Optional[datetime]) -> Optional[datetime]:
        if current is None:
            return candidate
        if candidate is None:
            return current
        return candidate if candidate < current else current

    @staticmethod
    def _max_datetime(current: Optional[datetime], candidate: Optional[datetime]) -> Optional[datetime]:
        if current is None:
            return candidate
        if candidate is None:
            return current
        return candidate if candidate > current else current
