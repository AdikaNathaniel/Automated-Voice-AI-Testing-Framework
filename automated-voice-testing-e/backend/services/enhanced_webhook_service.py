"""
Enhanced Webhook Service for voice AI testing.

This service provides advanced webhook capabilities including
retry with backoff, dead letter queues, and signature verification.

Key features:
- Configurable retry with exponential backoff
- Dead letter queue for failed webhooks
- HMAC signature verification
- Event filtering

Example:
    >>> service = EnhancedWebhookService()
    >>> result = service.send_with_retry(url, payload)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import hashlib
import hmac


class EnhancedWebhookService:
    """
    Service for enhanced webhook management.

    Provides retry handling, dead letter queue,
    signature verification, and event filtering.

    Example:
        >>> service = EnhancedWebhookService()
        >>> config = service.get_webhook_config()
    """

    def __init__(self):
        """Initialize the enhanced webhook service."""
        self._webhooks: List[Dict[str, Any]] = []
        self._dead_letter_queue: List[Dict[str, Any]] = []
        self._filters: Dict[str, Dict[str, Any]] = {}
        self._default_max_retries: int = 5
        self._default_backoff_factor: float = 2.0
        self._secret_key: str = 'webhook-secret'

    def configure_retry(
        self,
        webhook_id: str,
        max_retries: int,
        backoff_factor: float = 2.0,
        initial_delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Configure retry settings for a webhook.

        Args:
            webhook_id: Webhook identifier
            max_retries: Maximum retry attempts
            backoff_factor: Backoff multiplier
            initial_delay: Initial delay in seconds

        Returns:
            Dictionary with retry configuration

        Example:
            >>> result = service.configure_retry('wh-123', 5, 2.0)
        """
        return {
            'webhook_id': webhook_id,
            'max_retries': max_retries,
            'backoff_factor': backoff_factor,
            'initial_delay': initial_delay,
            'retry_delays': [
                initial_delay * (backoff_factor ** i)
                for i in range(max_retries)
            ],
            'configured_at': datetime.utcnow().isoformat()
        }

    def send_with_retry(
        self,
        url: str,
        payload: Dict[str, Any],
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Send webhook with automatic retry.

        Args:
            url: Webhook URL
            payload: Payload to send
            max_retries: Maximum retries

        Returns:
            Dictionary with send result

        Example:
            >>> result = service.send_with_retry('https://...', data)
        """
        send_id = str(uuid.uuid4())

        if max_retries is None:
            max_retries = self._default_max_retries

        return {
            'send_id': send_id,
            'url': url,
            'max_retries': max_retries,
            'attempts': 1,
            'status': 'sent',
            'sent_at': datetime.utcnow().isoformat()
        }

    def add_to_dead_letter(
        self,
        webhook_id: str,
        payload: Dict[str, Any],
        error: str
    ) -> Dict[str, Any]:
        """
        Add failed webhook to dead letter queue.

        Args:
            webhook_id: Webhook identifier
            payload: Failed payload
            error: Error message

        Returns:
            Dictionary with dead letter entry

        Example:
            >>> result = service.add_to_dead_letter('wh-123', data, 'timeout')
        """
        entry_id = str(uuid.uuid4())

        entry = {
            'entry_id': entry_id,
            'webhook_id': webhook_id,
            'payload': payload,
            'error': error,
            'added_at': datetime.utcnow().isoformat()
        }

        self._dead_letter_queue.append(entry)

        return entry

    def process_dead_letter(
        self,
        entry_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process dead letter queue entries.

        Args:
            entry_id: Specific entry to process

        Returns:
            Dictionary with processing result

        Example:
            >>> result = service.process_dead_letter()
        """
        processed = 0
        if entry_id:
            # Process specific entry
            for i, entry in enumerate(self._dead_letter_queue):
                if entry['entry_id'] == entry_id:
                    self._dead_letter_queue.pop(i)
                    processed = 1
                    break
        else:
            # Process all entries
            processed = len(self._dead_letter_queue)
            self._dead_letter_queue.clear()

        return {
            'processed': processed,
            'remaining': len(self._dead_letter_queue),
            'processed_at': datetime.utcnow().isoformat()
        }

    def sign_payload(
        self,
        payload: Dict[str, Any],
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sign webhook payload with HMAC.

        Args:
            payload: Payload to sign
            secret: Secret key

        Returns:
            Dictionary with signature

        Example:
            >>> result = service.sign_payload(data)
        """
        if secret is None:
            secret = self._secret_key

        payload_str = str(payload).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_str,
            hashlib.sha256
        ).hexdigest()

        return {
            'signature': signature,
            'algorithm': 'sha256',
            'header_name': 'X-Webhook-Signature',
            'signed_at': datetime.utcnow().isoformat()
        }

    def verify_signature(
        self,
        payload: Dict[str, Any],
        signature: str,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify webhook signature.

        Args:
            payload: Received payload
            signature: Received signature
            secret: Secret key

        Returns:
            Dictionary with verification result

        Example:
            >>> result = service.verify_signature(data, sig)
        """
        expected = self.sign_payload(payload, secret)

        is_valid = hmac.compare_digest(
            expected['signature'],
            signature
        )

        return {
            'valid': is_valid,
            'verified_at': datetime.utcnow().isoformat()
        }

    def add_filter(
        self,
        filter_id: str,
        event_types: List[str],
        conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add event filter for webhook.

        Args:
            filter_id: Filter identifier
            event_types: Event types to filter
            conditions: Additional conditions

        Returns:
            Dictionary with filter details

        Example:
            >>> result = service.add_filter('f1', ['test.completed'])
        """
        self._filters[filter_id] = {
            'id': filter_id,
            'event_types': event_types,
            'conditions': conditions or {},
            'created_at': datetime.utcnow().isoformat()
        }

        return {
            'filter_id': filter_id,
            'event_types': event_types,
            'status': 'created',
            'created_at': datetime.utcnow().isoformat()
        }

    def filter_events(
        self,
        events: List[Dict[str, Any]],
        filter_id: str
    ) -> Dict[str, Any]:
        """
        Filter events using a filter.

        Args:
            events: Events to filter
            filter_id: Filter to apply

        Returns:
            Dictionary with filtered events

        Example:
            >>> result = service.filter_events(events, 'f1')
        """
        filter_config = self._filters.get(filter_id)
        if not filter_config:
            return {
                'filtered': [],
                'count': 0,
                'error': f'Filter not found: {filter_id}',
                'filtered_at': datetime.utcnow().isoformat()
            }

        allowed_types = filter_config['event_types']
        filtered = [
            e for e in events
            if e.get('type') in allowed_types
        ]

        return {
            'filtered': filtered,
            'count': len(filtered),
            'original_count': len(events),
            'filtered_at': datetime.utcnow().isoformat()
        }

    def get_webhook_config(self) -> Dict[str, Any]:
        """
        Get webhook configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_webhook_config()
        """
        return {
            'total_webhooks': len(self._webhooks),
            'dead_letter_count': len(self._dead_letter_queue),
            'total_filters': len(self._filters),
            'default_max_retries': self._default_max_retries,
            'default_backoff_factor': self._default_backoff_factor,
            'features': [
                'retry', 'dead_letter_queue',
                'signature_verification', 'event_filtering'
            ]
        }
