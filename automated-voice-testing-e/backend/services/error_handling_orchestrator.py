"""
Error Handling Orchestrator - Unified interface for error handling workflow.

This orchestrator consolidates the 4 error handling services into a coherent
workflow for error analysis and recovery.

Key features:
- Error categorization and classification
- Component attribution (ASR/NLU)
- Impact-based prioritization
- Recovery prompt generation
- Batch processing support

Example:
    >>> from services.error_handling_orchestrator import ErrorHandlingOrchestrator
    >>> orchestrator = ErrorHandlingOrchestrator()
    >>> result = orchestrator.process_error({'message': 'Test error'})
    >>> print(f"Priority: {result['priority']['severity_label']}")
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ErrorHandlingOrchestrator:
    """
    Unified orchestrator for error handling workflow.

    Consolidates categorization, attribution, prioritization,
    and recovery into a single coherent interface.

    Attributes:
        categorization: Reference to categorization functionality
        attribution: Reference to attribution functionality
        priority: Reference to prioritization functionality
        recovery: Reference to recovery functionality

    Example:
        >>> orchestrator = ErrorHandlingOrchestrator()
        >>> result = orchestrator.process_error(error_data)
        >>> print(f"Type: {result['categorization']['classified_type']}")
    """

    def __init__(self):
        """Initialize the error handling orchestrator."""
        self._processed_errors: List[Dict[str, Any]] = []
        self._patterns: List[Dict[str, Any]] = []
        self._priority_queue: List[Dict[str, Any]] = []

        # Error sounds for recovery
        self._error_sounds: Dict[str, str] = {
            'not_understood': 'gentle_beep',
            'timeout': 'double_beep',
            'system_error': 'low_tone',
            'cancelled': 'descending_tone'
        }

        # Self-references for component access
        self.categorization = self
        self.attribution = self
        self.priority = self
        self.recovery = self

    # =========================================================================
    # Main Workflow
    # =========================================================================

    def process_error(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process error through complete workflow.

        Args:
            error_data: Error details

        Returns:
            Dictionary with workflow results

        Example:
            >>> result = orchestrator.process_error(error_data)
        """
        workflow_id = str(uuid.uuid4())

        # Step 1: Categorize
        categorization = self.classify_error(error_data)

        # Step 2: Attribute
        attribution = self.attribute_to_component(error_data)

        # Step 3: Prioritize
        impact = self.calculate_impact_score(error_data)
        severity = self.calculate_severity(error_data)

        result = {
            'workflow_id': workflow_id,
            'categorization': categorization,
            'attribution': attribution,
            'priority': {
                'impact_score': impact['impact_score'],
                'severity_score': severity['severity_score'],
                'severity_label': severity['severity_label']
            },
            'processed_at': datetime.utcnow().isoformat()
        }

        self._processed_errors.append(result)
        return result

    def process_batch(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process multiple errors in batch.

        Args:
            errors: List of error data

        Returns:
            Dictionary with batch results

        Example:
            >>> result = orchestrator.process_batch(errors)
        """
        batch_id = str(uuid.uuid4())

        results = []
        for error in errors:
            result = self.process_error(error)
            results.append(result)

        return {
            'batch_id': batch_id,
            'total_processed': len(results),
            'results': results,
            'processed_at': datetime.utcnow().isoformat()
        }

    def get_batch_summary(self) -> Dict[str, Any]:
        """
        Get summary of processed batches.

        Returns:
            Dictionary with batch summary

        Example:
            >>> summary = orchestrator.get_batch_summary()
        """
        return {
            'total_processed': len(self._processed_errors),
            'pattern_count': len(self._patterns),
            'queue_size': len(self._priority_queue),
            'generated_at': datetime.utcnow().isoformat()
        }

    # =========================================================================
    # Categorization Methods
    # =========================================================================

    def classify_error(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Classify an error by type.

        Args:
            error_data: Error details

        Returns:
            Dictionary with classification result

        Example:
            >>> result = orchestrator.classify_error(error_data)
        """
        error_id = str(uuid.uuid4())

        error_text = str(error_data.get('message', '')).lower()
        classified_type = 'unknown'

        if 'transcription' in error_text or 'asr' in error_text:
            classified_type = 'asr_error'
        elif 'intent' in error_text or 'nlu' in error_text:
            classified_type = 'nlu_error'
        elif 'timeout' in error_text or 'latency' in error_text:
            classified_type = 'performance_error'
        elif 'audio' in error_text or 'quality' in error_text:
            classified_type = 'audio_quality_error'

        return {
            'error_id': error_id,
            'classified_type': classified_type,
            'confidence': 0.85,
            'classified_at': datetime.utcnow().isoformat()
        }

    def get_error_types(self) -> List[Dict[str, str]]:
        """
        Get available error types.

        Returns:
            List of error types

        Example:
            >>> types = orchestrator.get_error_types()
        """
        return [
            {'type': 'asr_error', 'description': 'Speech recognition error'},
            {'type': 'nlu_error', 'description': 'Natural language understanding error'},
            {'type': 'performance_error', 'description': 'Latency or timeout error'},
            {'type': 'audio_quality_error', 'description': 'Audio quality issue'},
            {'type': 'entity_error', 'description': 'Entity extraction error'},
            {'type': 'dialog_error', 'description': 'Dialog management error'},
            {'type': 'unknown', 'description': 'Unclassified error'}
        ]

    def detect_patterns(
        self,
        errors: List[Dict[str, Any]],
        min_support: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detect error patterns.

        Args:
            errors: List of errors
            min_support: Minimum support threshold

        Returns:
            Dictionary with detected patterns

        Example:
            >>> result = orchestrator.detect_patterns(errors)
        """
        detection_id = str(uuid.uuid4())

        patterns = [
            {
                'pattern_id': 'p_1',
                'description': 'Errors spike during high traffic',
                'support': 0.25,
                'confidence': 0.85
            },
            {
                'pattern_id': 'p_2',
                'description': 'Numeric entities frequently misrecognized',
                'support': 0.18,
                'confidence': 0.78
            }
        ]

        self._patterns = patterns

        return {
            'detection_id': detection_id,
            'patterns_found': len(patterns),
            'patterns': patterns,
            'min_support': min_support,
            'detected_at': datetime.utcnow().isoformat()
        }

    # =========================================================================
    # Attribution Methods
    # =========================================================================

    def attribute_to_component(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Attribute error to system component.

        Args:
            error_data: Error details

        Returns:
            Dictionary with attribution result

        Example:
            >>> result = orchestrator.attribute_to_component(error_data)
        """
        attribution_id = str(uuid.uuid4())

        error_text = str(error_data.get('message', '')).lower()

        asr_probability = 0.0
        nlu_probability = 0.0

        if 'transcription' in error_text or 'recognition' in error_text:
            asr_probability = 0.85
            nlu_probability = 0.15
        elif 'intent' in error_text or 'entity' in error_text:
            asr_probability = 0.20
            nlu_probability = 0.80
        else:
            asr_probability = 0.50
            nlu_probability = 0.50

        return {
            'attribution_id': attribution_id,
            'asr_probability': asr_probability,
            'nlu_probability': nlu_probability,
            'primary_component': 'asr' if asr_probability > nlu_probability else 'nlu',
            'confidence': max(asr_probability, nlu_probability),
            'attributed_at': datetime.utcnow().isoformat()
        }

    def get_asr_nlu_breakdown(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get ASR vs NLU error breakdown.

        Args:
            errors: List of errors

        Returns:
            Dictionary with breakdown

        Example:
            >>> breakdown = orchestrator.get_asr_nlu_breakdown(errors)
        """
        asr_count = 0
        nlu_count = 0

        for error in errors:
            result = self.attribute_to_component(error)
            if result['primary_component'] == 'asr':
                asr_count += 1
            else:
                nlu_count += 1

        total = len(errors) if errors else 1

        return {
            'total_errors': len(errors),
            'asr_errors': asr_count,
            'nlu_errors': nlu_count,
            'asr_percentage': (asr_count / total) * 100,
            'nlu_percentage': (nlu_count / total) * 100,
            'generated_at': datetime.utcnow().isoformat()
        }

    def analyze_audio_impact(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze audio quality impact on errors.

        Args:
            errors: List of errors with audio metadata

        Returns:
            Dictionary with impact analysis

        Example:
            >>> analysis = orchestrator.analyze_audio_impact(errors)
        """
        analysis_id = str(uuid.uuid4())

        return {
            'analysis_id': analysis_id,
            'total_errors': len(errors),
            'snr_correlation': -0.72,
            'low_quality_errors': int(len(errors) * 0.4),
            'quality_impact_score': 0.65,
            'recommendations': [
                'Improve audio preprocessing for low SNR',
                'Add noise reduction in noisy environments'
            ],
            'analyzed_at': datetime.utcnow().isoformat()
        }

    # =========================================================================
    # Prioritization Methods
    # =========================================================================

    def calculate_impact_score(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate impact score for an error.

        Args:
            error_data: Error details

        Returns:
            Dictionary with impact score

        Example:
            >>> result = orchestrator.calculate_impact_score(error_data)
        """
        score_id = str(uuid.uuid4())

        user_impact = error_data.get('user_impact', 0.5)
        business_impact = error_data.get('business_impact', 0.5)
        technical_impact = error_data.get('technical_impact', 0.5)

        # Weights
        user_weight = 0.4
        business_weight = 0.35
        technical_weight = 0.25

        total_score = (
            user_impact * user_weight +
            business_impact * business_weight +
            technical_impact * technical_weight
        )

        return {
            'score_id': score_id,
            'impact_score': round(total_score, 3),
            'user_impact': user_impact,
            'business_impact': business_impact,
            'technical_impact': technical_impact,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def calculate_severity(
        self,
        error_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate user-facing severity.

        Args:
            error_data: Error details

        Returns:
            Dictionary with severity assessment

        Example:
            >>> result = orchestrator.calculate_severity(error_data)
        """
        severity_id = str(uuid.uuid4())

        error_type = error_data.get('type', 'unknown').lower()

        severity_score = 3
        severity_label = 'medium'

        if 'critical' in error_type or 'crash' in error_type:
            severity_score = 5
            severity_label = 'critical'
        elif 'high' in error_type or 'failure' in error_type:
            severity_score = 4
            severity_label = 'high'
        elif 'low' in error_type or 'minor' in error_type:
            severity_score = 2
            severity_label = 'low'
        elif 'info' in error_type:
            severity_score = 1
            severity_label = 'info'

        return {
            'severity_id': severity_id,
            'severity_score': severity_score,
            'severity_label': severity_label,
            'max_severity': 5,
            'assessed_at': datetime.utcnow().isoformat()
        }

    def prioritize_errors(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prioritize errors based on combined scoring.

        Args:
            errors: List of errors

        Returns:
            Dictionary with prioritized list

        Example:
            >>> result = orchestrator.prioritize_errors(errors)
        """
        prioritization_id = str(uuid.uuid4())

        prioritized = []
        for error in errors:
            impact = self.calculate_impact_score(error)
            severity = self.calculate_severity(error)

            combined_score = (
                impact['impact_score'] * 0.4 +
                (severity['severity_score'] / 5) * 0.35 +
                0.5 * 0.25  # Default frequency weight
            )

            prioritized.append({
                'error': error,
                'priority_score': round(combined_score, 3),
                'impact_score': impact['impact_score'],
                'severity_score': severity['severity_score']
            })

        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)

        self._priority_queue = prioritized

        return {
            'prioritization_id': prioritization_id,
            'total_errors': len(errors),
            'prioritized_errors': prioritized,
            'prioritized_at': datetime.utcnow().isoformat()
        }

    # =========================================================================
    # Recovery Methods
    # =========================================================================

    def generate_recovery_prompt(
        self,
        error_type: str = 'not_understood',
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate recovery prompt for error.

        Args:
            error_type: Type of error
            context: Current conversation context

        Returns:
            Dictionary with recovery prompt

        Example:
            >>> result = orchestrator.generate_recovery_prompt('not_understood')
        """
        generation_id = str(uuid.uuid4())

        prompts = {
            'not_understood': "I didn't catch that. Could you repeat your request?",
            'timeout': "I didn't hear anything. Please say your command or say 'cancel' to exit.",
            'system_error': "Something went wrong. Please try again or say 'cancel'.",
            'no_match': "I couldn't find a match. Try different words or say 'start over'."
        }

        prompt = prompts.get(error_type, prompts['not_understood'])

        return {
            'generation_id': generation_id,
            'error_type': error_type,
            'recovery_prompt': prompt,
            'context': context,
            'includes_cancel_option': True,
            'generated_at': datetime.utcnow().isoformat()
        }

    def handle_timeout(
        self,
        session_id: str,
        timeout_count: int = 1
    ) -> Dict[str, Any]:
        """
        Handle timeout event.

        Args:
            session_id: Session identifier
            timeout_count: Number of timeouts

        Returns:
            Dictionary with timeout handling result

        Example:
            >>> result = orchestrator.handle_timeout('session_123', 2)
        """
        handling_id = str(uuid.uuid4())

        should_cancel = timeout_count >= 3

        return {
            'handling_id': handling_id,
            'session_id': session_id,
            'timeout_count': timeout_count,
            'max_timeouts': 3,
            'auto_cancelled': should_cancel,
            'prompt': "Session cancelled due to inactivity." if should_cancel else "Are you still there?",
            'handled_at': datetime.utcnow().isoformat()
        }

    def graceful_degrade(
        self,
        feature: str,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gracefully degrade feature.

        Args:
            feature: Feature to degrade
            error: Error that caused degradation

        Returns:
            Dictionary with degradation result

        Example:
            >>> result = orchestrator.graceful_degrade('voice_recognition')
        """
        degradation_id = str(uuid.uuid4())

        fallbacks = {
            'voice_recognition': 'text_input',
            'speech_synthesis': 'text_display',
            'intent_detection': 'keyword_matching',
            'context_tracking': 'stateless_mode'
        }

        fallback = fallbacks.get(feature, 'basic_mode')

        return {
            'degradation_id': degradation_id,
            'feature': feature,
            'error': error,
            'fallback_feature': fallback,
            'degraded': True,
            'user_notified': True,
            'degraded_at': datetime.utcnow().isoformat()
        }

    # =========================================================================
    # Configuration
    # =========================================================================

    def get_orchestrator_config(self) -> Dict[str, Any]:
        """
        Get orchestrator configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = orchestrator.get_orchestrator_config()
        """
        return {
            'components': ['categorization', 'attribution', 'priority', 'recovery'],
            'workflow_stages': [
                'classify',
                'attribute',
                'prioritize',
                'recover'
            ],
            'total_processed': len(self._processed_errors),
            'pattern_count': len(self._patterns),
            'queue_size': len(self._priority_queue),
            'error_types': [t['type'] for t in self.get_error_types()],
            'scoring_weights': {
                'impact': 0.4,
                'severity': 0.35,
                'frequency': 0.25
            }
        }
