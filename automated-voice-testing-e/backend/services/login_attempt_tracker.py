"""
Login Attempt Tracker Service

Provides brute-force protection through rate limiting and account lockout.

Features:
    - Track failed login attempts per email
    - Exponential backoff between attempts
    - Account lockout after max failures
    - Auto-reset after lockout duration

Configuration:
    - MAX_ATTEMPTS: Maximum failures before lockout (default: 5)
    - LOCKOUT_DURATION: Lockout duration in minutes (default: 15)
    - BACKOFF_BASE: Base seconds for exponential backoff (default: 2)
"""

import time
from datetime import datetime, timezone
import threading


class LoginAttemptTracker:
    """
    Track login attempts and enforce rate limiting.

    Uses in-memory storage with thread-safe operations.
    For production, consider using Redis for distributed deployments.
    """

    def __init__(
        self,
        max_attempts: int = 5,
        lockout_duration_minutes: int = 15,
        backoff_base_seconds: float = 2.0
    ):
        """
        Initialize the login attempt tracker.

        Args:
            max_attempts: Maximum failed attempts before lockout
            lockout_duration_minutes: Duration of lockout in minutes
            backoff_base_seconds: Base seconds for exponential backoff
        """
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration_minutes * 60  # Convert to seconds
        self.backoff_base = backoff_base_seconds
        self._attempts: dict = {}  # email -> {'count': int, 'last_attempt': float, 'locked_until': float}
        self._lock = threading.Lock()

    def _get_attempt_data(self, email: str) -> dict:
        """Get or create attempt data for an email."""
        if email not in self._attempts:
            self._attempts[email] = {
                'count': 0,
                'last_attempt': 0.0,
                'locked_until': 0.0
            }
        return self._attempts[email]

    def is_locked_out(self, email: str) -> bool:
        """
        Check if an email is currently locked out.

        Args:
            email: Email to check

        Returns:
            bool: True if locked out
        """
        with self._lock:
            data = self._get_attempt_data(email)
            if data['locked_until'] > 0:
                if time.time() < data['locked_until']:
                    return True
                # Lockout expired, reset
                data['count'] = 0
                data['locked_until'] = 0.0
            return False

    def get_remaining_lockout_seconds(self, email: str) -> int:
        """
        Get remaining lockout time in seconds.

        Args:
            email: Email to check

        Returns:
            int: Remaining seconds, 0 if not locked
        """
        with self._lock:
            data = self._get_attempt_data(email)
            if data['locked_until'] > 0:
                remaining = data['locked_until'] - time.time()
                return max(0, int(remaining))
            return 0

    def get_wait_time(self, email: str) -> float:
        """
        Calculate wait time before next attempt (exponential backoff).

        Args:
            email: Email to check

        Returns:
            float: Seconds to wait before next attempt
        """
        with self._lock:
            data = self._get_attempt_data(email)
            if data['count'] == 0:
                return 0.0

            # Exponential backoff: base^(attempts-1) seconds
            wait_time = self.backoff_base ** (data['count'] - 1)
            elapsed = time.time() - data['last_attempt']

            if elapsed < wait_time:
                return wait_time - elapsed
            return 0.0

    def record_failure(self, email: str) -> dict:
        """
        Record a failed login attempt.

        Args:
            email: Email that failed login

        Returns:
            dict: Status with 'locked', 'attempts_remaining', 'wait_seconds'
        """
        with self._lock:
            data = self._get_attempt_data(email)
            data['count'] += 1
            data['last_attempt'] = time.time()

            attempts_remaining = max(0, self.max_attempts - data['count'])

            if data['count'] >= self.max_attempts:
                # Lock the account
                data['locked_until'] = time.time() + self.lockout_duration
                return {
                    'locked': True,
                    'attempts_remaining': 0,
                    'wait_seconds': self.lockout_duration,
                    'lockout_until': datetime.fromtimestamp(
                        data['locked_until'], tz=timezone.utc
                    ).isoformat()
                }

            # Calculate backoff wait time
            wait_time = self.backoff_base ** (data['count'] - 1)

            return {
                'locked': False,
                'attempts_remaining': attempts_remaining,
                'wait_seconds': wait_time,
                'lockout_until': None
            }

    def record_success(self, email: str) -> None:
        """
        Record a successful login, resetting attempt counter.

        Args:
            email: Email that logged in successfully
        """
        with self._lock:
            if email in self._attempts:
                self._attempts[email] = {
                    'count': 0,
                    'last_attempt': 0.0,
                    'locked_until': 0.0
                }

    def get_attempt_count(self, email: str) -> int:
        """
        Get current attempt count for an email.

        Args:
            email: Email to check

        Returns:
            int: Number of failed attempts
        """
        with self._lock:
            data = self._get_attempt_data(email)
            return data['count']

    def reset(self, email: str) -> None:
        """
        Reset attempt tracking for an email (admin function).

        Args:
            email: Email to reset
        """
        with self._lock:
            if email in self._attempts:
                del self._attempts[email]

    def clear_all(self) -> None:
        """Clear all tracked attempts (testing/admin function)."""
        with self._lock:
            self._attempts.clear()


# Global instance
login_attempt_tracker = LoginAttemptTracker()


__all__ = ['LoginAttemptTracker', 'login_attempt_tracker']
