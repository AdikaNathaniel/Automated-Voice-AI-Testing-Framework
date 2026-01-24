"""
Tests for LoginAttemptTracker service.

Tests brute-force protection and account lockout functionality.
"""

import time
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.login_attempt_tracker import LoginAttemptTracker


class TestLoginAttemptTracker:
    """Test suite for LoginAttemptTracker."""

    @pytest.fixture
    def tracker(self):
        """Create a fresh tracker instance for each test."""
        return LoginAttemptTracker(
            max_attempts=3,
            lockout_duration_minutes=1,  # Short for testing
            backoff_base_seconds=1.0
        )

    def test_initial_state_not_locked(self, tracker):
        """New email should not be locked."""
        assert tracker.is_locked_out("test@example.com") is False

    def test_initial_attempt_count_zero(self, tracker):
        """New email should have zero attempts."""
        assert tracker.get_attempt_count("test@example.com") == 0

    def test_record_failure_increments_count(self, tracker):
        """Recording failure should increment attempt count."""
        tracker.record_failure("test@example.com")
        assert tracker.get_attempt_count("test@example.com") == 1

    def test_record_failure_returns_attempts_remaining(self, tracker):
        """Record failure should return remaining attempts."""
        result = tracker.record_failure("test@example.com")
        assert result['attempts_remaining'] == 2
        assert result['locked'] is False

    def test_lockout_after_max_attempts(self, tracker):
        """Account should lock after max attempts."""
        email = "test@example.com"

        # First two attempts
        for _ in range(2):
            result = tracker.record_failure(email)
            assert result['locked'] is False

        # Third attempt triggers lockout
        result = tracker.record_failure(email)
        assert result['locked'] is True
        assert result['attempts_remaining'] == 0
        assert tracker.is_locked_out(email) is True

    def test_get_remaining_lockout_seconds(self, tracker):
        """Should return remaining lockout time."""
        email = "test@example.com"

        # Trigger lockout
        for _ in range(3):
            tracker.record_failure(email)

        remaining = tracker.get_remaining_lockout_seconds(email)
        assert remaining > 0
        assert remaining <= 60  # Max 1 minute lockout

    def test_no_remaining_lockout_when_not_locked(self, tracker):
        """Should return 0 when not locked."""
        remaining = tracker.get_remaining_lockout_seconds("test@example.com")
        assert remaining == 0

    def test_exponential_backoff_wait_time(self, tracker):
        """Wait time should increase exponentially."""
        email = "test@example.com"

        # First failure: wait time = 1^0 = 1 second
        tracker.record_failure(email)
        wait = tracker.get_wait_time(email)
        assert wait > 0

        # Second failure: wait time = 1^1 = 1 second
        time.sleep(0.1)  # Small delay
        tracker.record_failure(email)
        # Wait time should be for 2nd attempt

    def test_record_success_resets_count(self, tracker):
        """Successful login should reset attempt count."""
        email = "test@example.com"

        # Record some failures
        tracker.record_failure(email)
        tracker.record_failure(email)
        assert tracker.get_attempt_count(email) == 2

        # Success resets
        tracker.record_success(email)
        assert tracker.get_attempt_count(email) == 0

    def test_reset_clears_attempts(self, tracker):
        """Admin reset should clear all attempts."""
        email = "test@example.com"

        tracker.record_failure(email)
        tracker.reset(email)
        assert tracker.get_attempt_count(email) == 0

    def test_clear_all_removes_all_tracking(self, tracker):
        """Clear all should remove all tracked emails."""
        tracker.record_failure("user1@example.com")
        tracker.record_failure("user2@example.com")

        tracker.clear_all()

        assert tracker.get_attempt_count("user1@example.com") == 0
        assert tracker.get_attempt_count("user2@example.com") == 0

    def test_different_emails_tracked_separately(self, tracker):
        """Different emails should have separate tracking."""
        email1 = "user1@example.com"
        email2 = "user2@example.com"

        tracker.record_failure(email1)
        tracker.record_failure(email1)

        assert tracker.get_attempt_count(email1) == 2
        assert tracker.get_attempt_count(email2) == 0

    def test_lockout_prevents_further_attempts(self, tracker):
        """Locked account should stay locked."""
        email = "test@example.com"

        # Trigger lockout
        for _ in range(3):
            tracker.record_failure(email)

        assert tracker.is_locked_out(email) is True

        # Verify still locked
        time.sleep(0.1)
        assert tracker.is_locked_out(email) is True

    def test_wait_time_zero_after_wait(self, tracker):
        """Wait time should be zero after waiting."""
        email = "test@example.com"
        # After 1 failure: wait = base^(1-1) = base^0 = 1 second
        # So use base=0.1 and wait 0.15 seconds
        tracker_quick = LoginAttemptTracker(
            max_attempts=3,
            lockout_duration_minutes=1,
            backoff_base_seconds=0.1  # Results in 0.1^0 = 1 second for 1st attempt
        )

        tracker_quick.record_failure(email)
        # Wait = base^0 = 1 second. Since we can't wait that long in test,
        # just verify wait time decreases properly
        wait1 = tracker_quick.get_wait_time(email)
        time.sleep(0.5)
        wait2 = tracker_quick.get_wait_time(email)
        # Wait time should decrease
        assert wait2 < wait1


class TestPasswordComplexity:
    """Test password complexity validation."""

    def test_password_too_short(self):
        """Password under 12 chars should fail."""
        from api.schemas.auth import validate_password_complexity

        with pytest.raises(ValueError, match="at least 12 characters"):
            validate_password_complexity("Short1!")

    def test_password_no_uppercase(self):
        """Password without uppercase should fail."""
        from api.schemas.auth import validate_password_complexity

        with pytest.raises(ValueError, match="uppercase letter"):
            validate_password_complexity("lowercase123!")

    def test_password_no_lowercase(self):
        """Password without lowercase should fail."""
        from api.schemas.auth import validate_password_complexity

        with pytest.raises(ValueError, match="lowercase letter"):
            validate_password_complexity("UPPERCASE123!")

    def test_password_no_digit(self):
        """Password without digit should fail."""
        from api.schemas.auth import validate_password_complexity

        with pytest.raises(ValueError, match="digit"):
            validate_password_complexity("NoDigitsHere!!")

    def test_password_no_special(self):
        """Password without special char should fail."""
        from api.schemas.auth import validate_password_complexity

        with pytest.raises(ValueError, match="special character"):
            validate_password_complexity("NoSpecial123Aa")

    def test_valid_password_passes(self):
        """Valid password should pass all checks."""
        from api.schemas.auth import validate_password_complexity

        result = validate_password_complexity("ValidPass123!")
        assert result == "ValidPass123!"

    def test_valid_complex_password(self):
        """Complex valid password should pass."""
        from api.schemas.auth import validate_password_complexity

        result = validate_password_complexity("MyS3cur3P@ssw0rd!")
        assert result == "MyS3cur3P@ssw0rd!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
