"""
Slot Filling Accuracy Service for NLU testing.

This service provides metrics for evaluating entity extraction
and slot filling performance in NLU systems.

Key metrics:
- Slot precision, recall, and F1 score
- Per-entity type metrics
- Partial match scoring
- Slot value normalization accuracy

Example:
    >>> service = SlotFillingService()
    >>> metrics = service.get_slot_metrics(true_slots, pred_slots)
    >>> print(f"Slot F1: {metrics['overall_f1']:.3f}")
"""

from typing import List, Dict, Any, Tuple, Optional
from collections import Counter


class SlotFillingService:
    """
    Service for evaluating slot filling accuracy.

    Provides precision, recall, F1 scores, partial match scoring,
    and normalization accuracy for entity extraction tasks.

    Example:
        >>> service = SlotFillingService()
        >>> precision = service.calculate_slot_precision(tp=80, fp=20)
        >>> print(f"Precision: {precision:.3f}")
    """

    def __init__(self):
        """Initialize the slot filling service."""
        pass

    def calculate_slot_precision(
        self,
        tp: int,
        fp: int
    ) -> float:
        """
        Calculate slot precision from true positives and false positives.

        Precision = TP / (TP + FP)

        Args:
            tp: True positives (correctly extracted slots)
            fp: False positives (incorrectly extracted slots)

        Returns:
            Precision score (0.0 to 1.0)

        Example:
            >>> precision = service.calculate_slot_precision(80, 20)
            >>> print(f"Precision: {precision:.3f}")
        """
        if tp + fp == 0:
            return 0.0
        return float(tp / (tp + fp))

    def calculate_slot_recall(
        self,
        tp: int,
        fn: int
    ) -> float:
        """
        Calculate slot recall from true positives and false negatives.

        Recall = TP / (TP + FN)

        Args:
            tp: True positives (correctly extracted slots)
            fn: False negatives (missed slots)

        Returns:
            Recall score (0.0 to 1.0)

        Example:
            >>> recall = service.calculate_slot_recall(80, 10)
            >>> print(f"Recall: {recall:.3f}")
        """
        if tp + fn == 0:
            return 0.0
        return float(tp / (tp + fn))

    def calculate_slot_f1(
        self,
        precision: float,
        recall: float
    ) -> float:
        """
        Calculate slot F1 score from precision and recall.

        F1 = 2 * (precision * recall) / (precision + recall)

        Args:
            precision: Precision score
            recall: Recall score

        Returns:
            F1 score (0.0 to 1.0)

        Example:
            >>> f1 = service.calculate_slot_f1(0.8, 0.9)
            >>> print(f"F1: {f1:.3f}")
        """
        if precision + recall == 0:
            return 0.0
        return float(2 * (precision * recall) / (precision + recall))

    def calculate_per_entity_f1(
        self,
        true_slots: List[Dict[str, Any]],
        pred_slots: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate F1 score for each entity type.

        Args:
            true_slots: List of ground truth slots with 'type' and 'value'
            pred_slots: List of predicted slots with 'type' and 'value'

        Returns:
            Dictionary with per-entity F1 scores

        Example:
            >>> result = service.calculate_per_entity_f1(true_slots, pred_slots)
            >>> print(f"Date F1: {result['per_entity']['date']['f1']:.3f}")
        """
        # Get all entity types
        entity_types = set()
        for slot in true_slots + pred_slots:
            entity_types.add(slot.get('type', 'unknown'))

        per_entity = {}
        for entity_type in entity_types:
            # Count TP, FP, FN for this entity type
            true_of_type = [s for s in true_slots if s.get('type') == entity_type]
            pred_of_type = [s for s in pred_slots if s.get('type') == entity_type]

            # Match slots by value
            true_values = set(s.get('value') for s in true_of_type)
            pred_values = set(s.get('value') for s in pred_of_type)

            tp = len(true_values & pred_values)
            fp = len(pred_values - true_values)
            fn = len(true_values - pred_values)

            precision = self.calculate_slot_precision(tp, fp)
            recall = self.calculate_slot_recall(tp, fn)
            f1 = self.calculate_slot_f1(precision, recall)

            per_entity[entity_type] = {
                'precision': precision,
                'recall': recall,
                'f1': f1,
                'tp': tp,
                'fp': fp,
                'fn': fn,
                'support': len(true_of_type)
            }

        return {
            'per_entity': per_entity,
            'entity_types': list(entity_types),
            'num_entity_types': len(entity_types)
        }

    def calculate_partial_match_score(
        self,
        true_value: str,
        pred_value: str
    ) -> float:
        """
        Calculate partial match score between true and predicted values.

        Uses character-level overlap to score partial matches.

        Args:
            true_value: Ground truth slot value
            pred_value: Predicted slot value

        Returns:
            Partial match score (0.0 to 1.0)

        Example:
            >>> score = service.calculate_partial_match_score(
            ...     "New York City", "New York"
            ... )
        """
        if not true_value or not pred_value:
            return 0.0

        if true_value == pred_value:
            return 1.0

        # Character-level overlap
        true_chars = set(true_value.lower())
        pred_chars = set(pred_value.lower())

        overlap = len(true_chars & pred_chars)
        union = len(true_chars | pred_chars)

        if union == 0:
            return 0.0

        # Jaccard similarity
        jaccard = overlap / union

        # Also consider sequential match
        true_lower = true_value.lower()
        pred_lower = pred_value.lower()

        # Check if one is substring of other
        if true_lower in pred_lower or pred_lower in true_lower:
            substring_score = min(len(true_value), len(pred_value)) / max(
                len(true_value), len(pred_value)
            )
            return max(jaccard, substring_score)

        return float(jaccard)

    def evaluate_span_overlap(
        self,
        true_span: Tuple[int, int],
        pred_span: Tuple[int, int]
    ) -> Dict[str, Any]:
        """
        Evaluate overlap between true and predicted spans.

        Args:
            true_span: (start, end) tuple for ground truth
            pred_span: (start, end) tuple for prediction

        Returns:
            Dictionary with overlap metrics

        Example:
            >>> overlap = service.evaluate_span_overlap((0, 10), (5, 15))
        """
        true_start, true_end = true_span
        pred_start, pred_end = pred_span

        # Calculate overlap
        overlap_start = max(true_start, pred_start)
        overlap_end = min(true_end, pred_end)

        if overlap_start >= overlap_end:
            return {
                'overlap_chars': 0,
                'precision': 0.0,
                'recall': 0.0,
                'f1': 0.0,
                'exact_match': False
            }

        overlap_chars = overlap_end - overlap_start
        true_chars = true_end - true_start
        pred_chars = pred_end - pred_start

        precision = overlap_chars / pred_chars if pred_chars > 0 else 0.0
        recall = overlap_chars / true_chars if true_chars > 0 else 0.0
        f1 = self.calculate_slot_f1(precision, recall)

        return {
            'overlap_chars': overlap_chars,
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1),
            'exact_match': true_span == pred_span
        }

    def evaluate_normalization_accuracy(
        self,
        slot_pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Evaluate slot value normalization accuracy.

        Args:
            slot_pairs: List of (true_slot, pred_slot) tuples
                       Each slot has 'raw_value' and 'normalized_value'

        Returns:
            Dictionary with normalization accuracy metrics

        Example:
            >>> result = service.evaluate_normalization_accuracy(slot_pairs)
            >>> print(f"Normalization accuracy: {result['accuracy']:.3f}")
        """
        if not slot_pairs:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'per_type': {}
            }

        total = len(slot_pairs)
        correct = 0
        per_type_results = {}

        for true_slot, pred_slot in slot_pairs:
            entity_type = true_slot.get('type', 'unknown')
            true_norm = true_slot.get('normalized_value', '')
            pred_norm = pred_slot.get('normalized_value', '')

            if entity_type not in per_type_results:
                per_type_results[entity_type] = {'total': 0, 'correct': 0}

            per_type_results[entity_type]['total'] += 1

            if true_norm == pred_norm:
                correct += 1
                per_type_results[entity_type]['correct'] += 1

        # Calculate per-type accuracy
        per_type = {}
        for entity_type, results in per_type_results.items():
            per_type[entity_type] = {
                'accuracy': float(
                    results['correct'] / results['total']
                ) if results['total'] > 0 else 0.0,
                'total': results['total'],
                'correct': results['correct']
            }

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'per_type': per_type
        }

    def normalize_slot_value(
        self,
        value: str,
        entity_type: str
    ) -> str:
        """
        Normalize a slot value based on entity type.

        Args:
            value: Raw slot value
            entity_type: Type of entity (date, time, number, etc.)

        Returns:
            Normalized value

        Example:
            >>> normalized = service.normalize_slot_value("January 5th", "date")
        """
        if not value:
            return ""

        # Basic normalization
        normalized = value.strip().lower()

        if entity_type == 'date':
            # Remove ordinal suffixes
            for suffix in ['st', 'nd', 'rd', 'th']:
                normalized = normalized.replace(suffix, '')
            normalized = normalized.strip()

        elif entity_type == 'time':
            # Normalize time formats
            normalized = normalized.replace('.', ':')
            normalized = normalized.replace('am', ' am').replace('pm', ' pm')
            normalized = ' '.join(normalized.split())

        elif entity_type == 'number':
            # Remove commas, convert words to digits
            normalized = normalized.replace(',', '')
            word_to_num = {
                'one': '1', 'two': '2', 'three': '3', 'four': '4',
                'five': '5', 'six': '6', 'seven': '7', 'eight': '8',
                'nine': '9', 'ten': '10', 'zero': '0'
            }
            for word, num in word_to_num.items():
                normalized = normalized.replace(word, num)

        elif entity_type == 'location':
            # Standardize location abbreviations
            abbrevs = {
                'st': 'street', 'ave': 'avenue', 'blvd': 'boulevard',
                'rd': 'road', 'dr': 'drive', 'ln': 'lane'
            }
            words = normalized.split()
            normalized = ' '.join(
                abbrevs.get(w, w) for w in words
            )

        return normalized

    def get_slot_metrics(
        self,
        true_slots: List[Dict[str, Any]],
        pred_slots: List[Dict[str, Any]],
        use_partial_match: bool = False
    ) -> Dict[str, Any]:
        """
        Get comprehensive slot filling metrics.

        Args:
            true_slots: List of ground truth slots
            pred_slots: List of predicted slots
            use_partial_match: Whether to use partial matching

        Returns:
            Dictionary with all slot metrics

        Example:
            >>> metrics = service.get_slot_metrics(true_slots, pred_slots)
            >>> print(f"F1: {metrics['overall_f1']:.3f}")
        """
        # Match slots
        true_values = []
        pred_values = []

        for slot in true_slots:
            true_values.append((
                slot.get('type', 'unknown'),
                slot.get('value', '')
            ))

        for slot in pred_slots:
            pred_values.append((
                slot.get('type', 'unknown'),
                slot.get('value', '')
            ))

        true_set = set(true_values)
        pred_set = set(pred_values)

        if use_partial_match:
            # Use partial matching
            tp = 0
            matched_true = set()
            matched_pred = set()

            for true_val in true_values:
                for pred_val in pred_values:
                    if true_val[0] == pred_val[0]:  # Same type
                        score = self.calculate_partial_match_score(
                            true_val[1], pred_val[1]
                        )
                        if score > 0.5:  # Threshold for match
                            if true_val not in matched_true and pred_val not in matched_pred:
                                tp += score
                                matched_true.add(true_val)
                                matched_pred.add(pred_val)

            fp = len(pred_set) - len(matched_pred)
            fn = len(true_set) - len(matched_true)
        else:
            # Exact matching
            tp = len(true_set & pred_set)
            fp = len(pred_set - true_set)
            fn = len(true_set - pred_set)

        precision = self.calculate_slot_precision(int(tp), int(fp))
        recall = self.calculate_slot_recall(int(tp), int(fn))
        f1 = self.calculate_slot_f1(precision, recall)

        # Get per-entity metrics
        per_entity = self.calculate_per_entity_f1(true_slots, pred_slots)

        return {
            'overall_precision': precision,
            'overall_recall': recall,
            'overall_f1': f1,
            'tp': int(tp),
            'fp': int(fp),
            'fn': int(fn),
            'total_true': len(true_slots),
            'total_pred': len(pred_slots),
            'per_entity_metrics': per_entity,
            'use_partial_match': use_partial_match
        }

    def generate_slot_report(
        self,
        true_slots: List[Dict[str, Any]],
        pred_slots: List[Dict[str, Any]],
        utterances: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive slot filling report.

        Args:
            true_slots: Ground truth slots
            pred_slots: Predicted slots
            utterances: Optional list of utterance texts

        Returns:
            Dictionary with complete slot analysis

        Example:
            >>> report = service.generate_slot_report(true_slots, pred_slots)
        """
        # Get overall metrics
        metrics = self.get_slot_metrics(true_slots, pred_slots)
        partial_metrics = self.get_slot_metrics(
            true_slots, pred_slots, use_partial_match=True
        )

        # Analyze errors
        errors = self._analyze_slot_errors(true_slots, pred_slots)

        # Entity type distribution
        true_type_dist = Counter(s.get('type', 'unknown') for s in true_slots)
        pred_type_dist = Counter(s.get('type', 'unknown') for s in pred_slots)

        return {
            'summary': {
                'overall_f1': metrics['overall_f1'],
                'overall_precision': metrics['overall_precision'],
                'overall_recall': metrics['overall_recall'],
                'partial_match_f1': partial_metrics['overall_f1']
            },
            'exact_match_metrics': metrics,
            'partial_match_metrics': partial_metrics,
            'error_analysis': errors,
            'entity_distribution': {
                'true': dict(true_type_dist),
                'predicted': dict(pred_type_dist)
            },
            'recommendations': self._generate_recommendations(
                metrics, errors, true_type_dist
            )
        }

    def _analyze_slot_errors(
        self,
        true_slots: List[Dict[str, Any]],
        pred_slots: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze slot filling errors."""
        # Build lookup
        true_by_type = {}
        for slot in true_slots:
            entity_type = slot.get('type', 'unknown')
            if entity_type not in true_by_type:
                true_by_type[entity_type] = []
            true_by_type[entity_type].append(slot)

        pred_by_type = {}
        for slot in pred_slots:
            entity_type = slot.get('type', 'unknown')
            if entity_type not in pred_by_type:
                pred_by_type[entity_type] = []
            pred_by_type[entity_type].append(slot)

        # Analyze errors
        missing_slots = []  # FN
        extra_slots = []    # FP

        for entity_type, slots in true_by_type.items():
            pred_of_type = pred_by_type.get(entity_type, [])
            pred_values = {s.get('value') for s in pred_of_type}

            for slot in slots:
                value = slot.get('value')
                if value not in pred_values:
                    missing_slots.append(slot)

        for entity_type, slots in pred_by_type.items():
            true_of_type = true_by_type.get(entity_type, [])
            true_values = {s.get('value') for s in true_of_type}

            for slot in slots:
                value = slot.get('value')
                if value not in true_values:
                    extra_slots.append(slot)

        return {
            'missing_slots': missing_slots[:20],  # Limit to 20
            'extra_slots': extra_slots[:20],
            'total_missing': len(missing_slots),
            'total_extra': len(extra_slots)
        }

    def _generate_recommendations(
        self,
        metrics: Dict[str, Any],
        errors: Dict[str, Any],
        type_dist: Counter
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        # Check overall performance
        if metrics['overall_f1'] < 0.7:
            recommendations.append(
                "Overall F1 score is below 0.7 - consider adding more "
                "training data or reviewing entity definitions"
            )

        # Check precision/recall balance
        if metrics['overall_precision'] - metrics['overall_recall'] > 0.2:
            recommendations.append(
                "Recall is significantly lower than precision - "
                "model may be missing valid entities"
            )
        elif metrics['overall_recall'] - metrics['overall_precision'] > 0.2:
            recommendations.append(
                "Precision is significantly lower than recall - "
                "model may be over-extracting entities"
            )

        # Check for problematic entity types
        per_entity = metrics.get('per_entity_metrics', {}).get('per_entity', {})
        for entity_type, type_metrics in per_entity.items():
            if type_metrics['f1'] < 0.5 and type_metrics['support'] > 5:
                recommendations.append(
                    f"Entity type '{entity_type}' has low F1 ({type_metrics['f1']:.2f}) - "
                    "review training examples"
                )

        return recommendations

