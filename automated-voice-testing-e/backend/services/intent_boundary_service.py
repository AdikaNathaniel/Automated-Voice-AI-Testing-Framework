"""
Intent Boundary Testing Service for NLU testing.

This service provides metrics for evaluating how well an NLU system
handles boundary cases between similar intents.

Key metrics:
- Similar intent disambiguation
- Intent overlap measurement
- Edge case utterance identification and evaluation

Example:
    >>> service = IntentBoundaryService()
    >>> similarity = service.calculate_intent_similarity(intent_a, intent_b)
    >>> print(f"Similarity: {similarity:.3f}")
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from collections import Counter


class IntentBoundaryService:
    """
    Service for evaluating intent boundary performance.

    Provides metrics for similar intent disambiguation, overlap
    measurement, and edge case utterance evaluation.

    Example:
        >>> service = IntentBoundaryService()
        >>> overlap = service.calculate_overlap(intent_a, intent_b, predictions)
        >>> print(f"Overlap: {overlap['overlap_ratio']:.3f}")
    """

    def __init__(self):
        """Initialize the intent boundary service."""
        pass

    def calculate_intent_similarity(
        self,
        intent_a_utterances: List[str],
        intent_b_utterances: List[str],
        predictions: List[Tuple[str, List[Tuple[str, float]]]]
    ) -> float:
        """
        Calculate similarity between two intents based on predictions.

        Measures how often utterances from one intent are confused with another.

        Args:
            intent_a_utterances: Utterances belonging to intent A
            intent_b_utterances: Utterances belonging to intent B
            predictions: List of (utterance, [(intent, confidence)]) tuples

        Returns:
            Similarity score (0.0 to 1.0), higher means more confusion

        Example:
            >>> similarity = service.calculate_intent_similarity(
            ...     ['turn on lights', 'lights on'],
            ...     ['turn off lights', 'lights off'],
            ...     predictions
            ... )
        """
        if not intent_a_utterances or not intent_b_utterances:
            return 0.0

        # Build prediction lookup
        pred_lookup = {utt: preds for utt, preds in predictions}

        # Count confusions
        a_confused_with_b = 0
        b_confused_with_a = 0

        # Check intent A utterances
        for utt in intent_a_utterances:
            if utt in pred_lookup:
                preds = pred_lookup[utt]
                for intent, conf in preds:
                    if intent in [u for u in intent_b_utterances]:
                        a_confused_with_b += conf

        # Check intent B utterances
        for utt in intent_b_utterances:
            if utt in pred_lookup:
                preds = pred_lookup[utt]
                for intent, conf in preds:
                    if intent in [u for u in intent_a_utterances]:
                        b_confused_with_a += conf

        # Calculate similarity based on confidence distribution
        total_utterances = len(intent_a_utterances) + len(intent_b_utterances)
        similarity = (a_confused_with_b + b_confused_with_a) / total_utterances

        return min(1.0, float(similarity))

    def find_similar_intents(
        self,
        intent_names: List[str],
        confusion_matrix: List[List[int]],
        threshold: float = 0.1
    ) -> List[Tuple[str, str, float]]:
        """
        Find pairs of similar intents based on confusion matrix.

        Args:
            intent_names: List of intent names
            confusion_matrix: Confusion matrix with counts
            threshold: Minimum similarity threshold

        Returns:
            List of (intent_a, intent_b, similarity) tuples

        Example:
            >>> similar = service.find_similar_intents(
            ...     ['play_music', 'stop_music', 'volume_up'],
            ...     confusion_matrix
            ... )
        """
        similar_pairs = []
        n_intents = len(intent_names)

        for i in range(n_intents):
            for j in range(i + 1, n_intents):
                # Calculate confusion between intents i and j
                row_total_i = sum(confusion_matrix[i])
                row_total_j = sum(confusion_matrix[j])

                if row_total_i > 0 and row_total_j > 0:
                    # Confusion from i to j
                    conf_i_to_j = confusion_matrix[i][j] / row_total_i
                    # Confusion from j to i
                    conf_j_to_i = confusion_matrix[j][i] / row_total_j
                    # Average confusion
                    similarity = (conf_i_to_j + conf_j_to_i) / 2

                    if similarity >= threshold:
                        similar_pairs.append((
                            intent_names[i],
                            intent_names[j],
                            float(similarity)
                        ))

        # Sort by similarity descending
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        return similar_pairs

    def calculate_disambiguation_score(
        self,
        true_labels: List[str],
        predictions: List[List[Tuple[str, float]]],
        similar_intent_pairs: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Calculate disambiguation score for similar intent pairs.

        Args:
            true_labels: Ground truth labels
            predictions: List of [(intent, confidence)] for each sample
            similar_intent_pairs: List of (intent_a, intent_b) pairs

        Returns:
            Dictionary with disambiguation metrics

        Example:
            >>> result = service.calculate_disambiguation_score(
            ...     labels, predictions, [('play', 'pause')]
            ... )
        """
        # Create set of similar intents
        similar_intents = set()
        for a, b in similar_intent_pairs:
            similar_intents.add(a)
            similar_intents.add(b)

        # Track metrics
        total_similar = 0
        correct_similar = 0
        confidence_gaps = []

        for true_label, preds in zip(true_labels, predictions):
            if true_label in similar_intents:
                total_similar += 1

                # Check if top prediction is correct
                if preds and preds[0][0] == true_label:
                    correct_similar += 1

                    # Calculate confidence gap to second choice
                    if len(preds) > 1:
                        gap = preds[0][1] - preds[1][1]
                        confidence_gaps.append(gap)

        # Calculate metrics
        accuracy = correct_similar / total_similar if total_similar > 0 else 0.0
        avg_gap = np.mean(confidence_gaps) if confidence_gaps else 0.0

        return {
            'disambiguation_accuracy': float(accuracy),
            'total_similar_samples': total_similar,
            'correct_predictions': correct_similar,
            'average_confidence_gap': float(avg_gap),
            'confidence_gap_std': float(np.std(confidence_gaps)) if confidence_gaps else 0.0
        }

    def calculate_overlap(
        self,
        intent_a: str,
        intent_b: str,
        predictions: List[Tuple[str, List[Tuple[str, float]]]]
    ) -> Dict[str, Any]:
        """
        Calculate overlap between two intents.

        Measures the degree to which intent boundaries overlap.

        Args:
            intent_a: First intent name
            intent_b: Second intent name
            predictions: List of (true_label, [(pred, conf)]) tuples

        Returns:
            Dictionary with overlap metrics

        Example:
            >>> overlap = service.calculate_overlap(
            ...     'turn_on', 'turn_off', predictions
            ... )
        """
        a_to_b = 0  # A predicted as B
        b_to_a = 0  # B predicted as A
        total_a = 0
        total_b = 0

        for true_label, preds in predictions:
            top_pred = preds[0][0] if preds else None

            if true_label == intent_a:
                total_a += 1
                if top_pred == intent_b:
                    a_to_b += 1
            elif true_label == intent_b:
                total_b += 1
                if top_pred == intent_a:
                    b_to_a += 1

        # Calculate overlap ratios
        overlap_a_to_b = a_to_b / total_a if total_a > 0 else 0.0
        overlap_b_to_a = b_to_a / total_b if total_b > 0 else 0.0
        total_overlap = (a_to_b + b_to_a) / (total_a + total_b) if (total_a + total_b) > 0 else 0.0

        return {
            'intent_a': intent_a,
            'intent_b': intent_b,
            'overlap_a_to_b': float(overlap_a_to_b),
            'overlap_b_to_a': float(overlap_b_to_a),
            'total_overlap': float(total_overlap),
            'samples_a': total_a,
            'samples_b': total_b,
            'confusions_a_to_b': a_to_b,
            'confusions_b_to_a': b_to_a
        }

    def identify_overlap_regions(
        self,
        intent_names: List[str],
        confusion_matrix: List[List[int]]
    ) -> List[Dict[str, Any]]:
        """
        Identify regions of high overlap between intents.

        Args:
            intent_names: List of intent names
            confusion_matrix: Confusion matrix

        Returns:
            List of overlap region dictionaries

        Example:
            >>> regions = service.identify_overlap_regions(intents, matrix)
        """
        regions = []
        n_intents = len(intent_names)

        for i in range(n_intents):
            row_total = sum(confusion_matrix[i])
            if row_total == 0:
                continue

            # Find significant confusions
            confusions = []
            for j in range(n_intents):
                if i != j:
                    conf_rate = confusion_matrix[i][j] / row_total
                    if conf_rate > 0.05:  # 5% threshold
                        confusions.append({
                            'confused_with': intent_names[j],
                            'confusion_rate': float(conf_rate),
                            'count': confusion_matrix[i][j]
                        })

            if confusions:
                regions.append({
                    'intent': intent_names[i],
                    'total_samples': row_total,
                    'correct_rate': float(confusion_matrix[i][i] / row_total),
                    'confusions': sorted(
                        confusions,
                        key=lambda x: x['confusion_rate'],
                        reverse=True
                    )
                })

        return regions

    def calculate_boundary_sharpness(
        self,
        predictions: List[Tuple[str, List[Tuple[str, float]]]]
    ) -> Dict[str, Any]:
        """
        Calculate how sharp the decision boundaries are.

        Sharp boundaries have large gaps between top predictions.

        Args:
            predictions: List of (true_label, [(pred, conf)]) tuples

        Returns:
            Dictionary with boundary sharpness metrics

        Example:
            >>> sharpness = service.calculate_boundary_sharpness(predictions)
        """
        confidence_gaps = []
        entropy_values = []

        for _, preds in predictions:
            if len(preds) >= 2:
                # Gap between top two predictions
                gap = preds[0][1] - preds[1][1]
                confidence_gaps.append(gap)

                # Calculate entropy of prediction distribution
                confidences = [p[1] for p in preds]
                total = sum(confidences)
                if total > 0:
                    probs = [c / total for c in confidences]
                    entropy = -sum(p * np.log2(p + 1e-10) for p in probs)
                    entropy_values.append(entropy)

        # Calculate metrics
        avg_gap = np.mean(confidence_gaps) if confidence_gaps else 0.0
        avg_entropy = np.mean(entropy_values) if entropy_values else 0.0

        # Sharpness score: high gap = sharp, low entropy = sharp
        sharpness = avg_gap * (1 - avg_entropy / np.log2(10))

        return {
            'sharpness_score': float(max(0, sharpness)),
            'average_confidence_gap': float(avg_gap),
            'gap_std': float(np.std(confidence_gaps)) if confidence_gaps else 0.0,
            'average_entropy': float(avg_entropy),
            'entropy_std': float(np.std(entropy_values)) if entropy_values else 0.0,
            'total_samples': len(predictions)
        }

    def identify_edge_cases(
        self,
        true_labels: List[str],
        predictions: List[List[Tuple[str, float]]],
        confidence_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Identify edge case utterances based on predictions.

        Edge cases are samples with low confidence or close alternatives.

        Args:
            true_labels: Ground truth labels
            predictions: List of [(intent, confidence)] for each sample
            confidence_threshold: Threshold for identifying edge cases

        Returns:
            List of edge case dictionaries

        Example:
            >>> edge_cases = service.identify_edge_cases(labels, predictions)
        """
        edge_cases = []

        for idx, (true_label, preds) in enumerate(zip(true_labels, predictions)):
            if not preds:
                continue

            top_conf = preds[0][1]
            top_pred = preds[0][0]

            # Check if this is an edge case
            is_edge_case = False
            edge_reason = []

            # Low confidence
            if top_conf < confidence_threshold:
                is_edge_case = True
                edge_reason.append('low_confidence')

            # Close alternatives
            if len(preds) >= 2 and (preds[0][1] - preds[1][1]) < 0.1:
                is_edge_case = True
                edge_reason.append('close_alternative')

            # Misclassified
            if top_pred != true_label:
                is_edge_case = True
                edge_reason.append('misclassified')

            if is_edge_case:
                edge_cases.append({
                    'index': idx,
                    'true_label': true_label,
                    'top_prediction': top_pred,
                    'confidence': float(top_conf),
                    'alternatives': [(p, float(c)) for p, c in preds[1:3]],
                    'reasons': edge_reason
                })

        return edge_cases

    def evaluate_edge_case_performance(
        self,
        edge_cases: List[Dict[str, Any]],
        true_labels: List[str],
        predictions: List[List[Tuple[str, float]]]
    ) -> Dict[str, Any]:
        """
        Evaluate model performance on identified edge cases.

        Args:
            edge_cases: List of edge case dictionaries
            true_labels: Ground truth labels
            predictions: Predictions for all samples

        Returns:
            Dictionary with edge case performance metrics

        Example:
            >>> perf = service.evaluate_edge_case_performance(
            ...     edge_cases, labels, predictions
            ... )
        """
        if not edge_cases:
            return {
                'edge_case_count': 0,
                'edge_case_accuracy': 0.0,
                'total_samples': len(true_labels),
                'edge_case_ratio': 0.0
            }

        # Count correct predictions among edge cases
        correct = sum(
            1 for ec in edge_cases
            if ec['top_prediction'] == ec['true_label']
        )

        # Analyze by reason
        reason_counts = Counter()
        for ec in edge_cases:
            for reason in ec['reasons']:
                reason_counts[reason] += 1

        return {
            'edge_case_count': len(edge_cases),
            'edge_case_accuracy': float(correct / len(edge_cases)),
            'total_samples': len(true_labels),
            'edge_case_ratio': float(len(edge_cases) / len(true_labels)),
            'correct_predictions': correct,
            'reason_distribution': dict(reason_counts)
        }

    def generate_edge_case_report(
        self,
        true_labels: List[str],
        predictions: List[List[Tuple[str, float]]],
        utterances: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive edge case report.

        Args:
            true_labels: Ground truth labels
            predictions: Predictions for all samples
            utterances: Optional list of utterance texts

        Returns:
            Dictionary with complete edge case analysis

        Example:
            >>> report = service.generate_edge_case_report(
            ...     labels, predictions, utterances
            ... )
        """
        # Identify edge cases
        edge_cases = self.identify_edge_cases(true_labels, predictions)

        # Evaluate performance
        performance = self.evaluate_edge_case_performance(
            edge_cases, true_labels, predictions
        )

        # Group by intent
        by_intent = {}
        for ec in edge_cases:
            intent = ec['true_label']
            if intent not in by_intent:
                by_intent[intent] = []
            by_intent[intent].append(ec)

        # Add utterance text if provided
        if utterances:
            for ec in edge_cases:
                ec['utterance'] = utterances[ec['index']]

        return {
            'summary': performance,
            'edge_cases': edge_cases[:50],  # Limit to top 50
            'by_intent': {
                intent: {
                    'count': len(cases),
                    'accuracy': float(
                        sum(1 for c in cases if c['top_prediction'] == c['true_label'])
                        / len(cases)
                    ) if cases else 0.0
                }
                for intent, cases in by_intent.items()
            },
            'recommendations': self._generate_recommendations(edge_cases, by_intent)
        }

    def _generate_recommendations(
        self,
        edge_cases: List[Dict[str, Any]],
        by_intent: Dict[str, List[Dict[str, Any]]]
    ) -> List[str]:
        """Generate recommendations based on edge case analysis."""
        recommendations = []

        # Check for intents with many edge cases
        for intent, cases in by_intent.items():
            if len(cases) > 5:
                recommendations.append(
                    f"Intent '{intent}' has {len(cases)} edge cases - "
                    "consider adding more training examples"
                )

        # Check for common confusion patterns
        confusion_pairs = Counter()
        for ec in edge_cases:
            if ec['top_prediction'] != ec['true_label']:
                pair = tuple(sorted([ec['true_label'], ec['top_prediction']]))
                confusion_pairs[pair] += 1

        for pair, count in confusion_pairs.most_common(3):
            if count >= 3:
                recommendations.append(
                    f"Frequent confusion between '{pair[0]}' and '{pair[1]}' "
                    f"({count} cases) - review intent definitions"
                )

        return recommendations

    def analyze_decision_boundary(
        self,
        intent_a: str,
        intent_b: str,
        predictions: List[Tuple[str, List[Tuple[str, float]]]]
    ) -> Dict[str, Any]:
        """
        Analyze the decision boundary between two intents.

        Args:
            intent_a: First intent
            intent_b: Second intent
            predictions: List of (true_label, [(pred, conf)]) tuples

        Returns:
            Dictionary with boundary analysis

        Example:
            >>> analysis = service.analyze_decision_boundary(
            ...     'play', 'pause', predictions
            ... )
        """
        # Collect confidence differences
        a_samples = []
        b_samples = []

        for true_label, preds in predictions:
            # Get confidences for both intents
            conf_a = 0.0
            conf_b = 0.0
            for intent, conf in preds:
                if intent == intent_a:
                    conf_a = conf
                elif intent == intent_b:
                    conf_b = conf

            if true_label == intent_a:
                a_samples.append(conf_a - conf_b)
            elif true_label == intent_b:
                b_samples.append(conf_b - conf_a)

        # Calculate boundary statistics
        a_margin = np.mean(a_samples) if a_samples else 0.0
        b_margin = np.mean(b_samples) if b_samples else 0.0

        # Decision boundary quality
        boundary_clarity = (a_margin + b_margin) / 2

        return {
            'intent_a': intent_a,
            'intent_b': intent_b,
            'a_average_margin': float(a_margin),
            'b_average_margin': float(b_margin),
            'a_margin_std': float(np.std(a_samples)) if a_samples else 0.0,
            'b_margin_std': float(np.std(b_samples)) if b_samples else 0.0,
            'boundary_clarity': float(boundary_clarity),
            'samples_a': len(a_samples),
            'samples_b': len(b_samples),
            'quality': (
                'excellent' if boundary_clarity > 0.5
                else 'good' if boundary_clarity > 0.3
                else 'fair' if boundary_clarity > 0.1
                else 'poor'
            )
        }

    def get_boundary_metrics(
        self,
        true_labels: List[str],
        predictions: List[List[Tuple[str, float]]],
        confusion_matrix: Optional[List[List[int]]] = None,
        intent_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive boundary metrics.

        Args:
            true_labels: Ground truth labels
            predictions: List of [(intent, confidence)] for each sample
            confusion_matrix: Optional confusion matrix
            intent_names: Optional list of intent names

        Returns:
            Dictionary with all boundary metrics

        Example:
            >>> metrics = service.get_boundary_metrics(labels, predictions)
        """
        # Convert predictions format for some methods
        pred_tuples = list(zip(true_labels, predictions))

        # Calculate sharpness
        sharpness = self.calculate_boundary_sharpness(pred_tuples)

        # Identify edge cases
        edge_cases = self.identify_edge_cases(true_labels, predictions)
        edge_performance = self.evaluate_edge_case_performance(
            edge_cases, true_labels, predictions
        )

        # Get similar intents if confusion matrix provided
        similar_intents = []
        overlap_regions = []
        if confusion_matrix and intent_names:
            similar_intents = self.find_similar_intents(
                intent_names, confusion_matrix
            )
            overlap_regions = self.identify_overlap_regions(
                intent_names, confusion_matrix
            )

        return {
            'sharpness': sharpness,
            'edge_case_analysis': edge_performance,
            'similar_intent_pairs': similar_intents[:10],  # Top 10
            'overlap_regions': overlap_regions,
            'total_samples': len(true_labels),
            'total_edge_cases': len(edge_cases),
            'boundary_quality': (
                'excellent' if sharpness['sharpness_score'] > 0.4
                else 'good' if sharpness['sharpness_score'] > 0.2
                else 'fair' if sharpness['sharpness_score'] > 0.1
                else 'poor'
            )
        }

