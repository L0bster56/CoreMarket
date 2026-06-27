"""Tests for notification tasks (send_welcome_email)."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestSendWelcomeEmail:
    def test_task_skips_when_user_not_found(self):
        from src.backend.application.tasks.notifications import send_welcome_email

        with patch(
            "src.backend.application.tasks.notifications.asyncio.run",
            return_value=None,
        ):
            result = send_welcome_email.apply(args=["nonexistent-user-id"])
            assert result.result == {"status": "skipped", "reason": "user_not_found"}

    def test_task_calls_send_email_when_user_found(self):
        from src.backend.application.tasks.notifications import send_welcome_email

        fake_row = ("user@example.com", "testuser")

        with patch(
            "src.backend.application.tasks.notifications.asyncio.run",
            return_value=fake_row,
        ), patch(
            "src.backend.application.tasks.notifications._send_email",
        ) as mock_send:
            result = send_welcome_email.apply(args=["user-uuid-123"])
            assert result.result["status"] == "sent"
            assert result.result["to"] == "user@example.com"
            mock_send.assert_called_once_with("user@example.com", "testuser")

    def test_task_returns_sent_status(self):
        from src.backend.application.tasks.notifications import send_welcome_email

        fake_row = ("another@example.com", "alice")

        with patch(
            "src.backend.application.tasks.notifications.asyncio.run",
            return_value=fake_row,
        ), patch("src.backend.application.tasks.notifications._send_email"):
            result = send_welcome_email.apply(args=["alice-uuid"])
            assert result.successful()
            assert result.result["status"] == "sent"

    def test_task_logs_on_success(self, caplog):
        import logging

        from src.backend.application.tasks.notifications import send_welcome_email

        fake_row = ("log@example.com", "loguser")

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.notifications"):
            with patch(
                "src.backend.application.tasks.notifications.asyncio.run",
                return_value=fake_row,
            ), patch("src.backend.application.tasks.notifications._send_email"):
                send_welcome_email.apply(args=["log-uuid"])

        assert any("task_started" in r.message for r in caplog.records)
        assert any("task_completed" in r.message for r in caplog.records)

    def test_task_name_is_correct(self):
        from src.backend.application.tasks.notifications import send_welcome_email

        assert send_welcome_email.name == "coremarket.tasks.send_welcome_email"

    def test_send_email_skips_when_no_smtp(self):
        """_send_email logs and skips when SMTP_HOST is not configured."""
        from src.backend.application.tasks.notifications import _send_email

        # get_settings is a local import inside _send_email, so patch at the config module.
        with patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(SMTP_HOST=None)
            # Should not raise and should not attempt SMTP connection
            _send_email("x@example.com", "xuser")
