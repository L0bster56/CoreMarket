"""
Tests for infrastructure/notifications/telegram.py

Covers:
- _fingerprint():             dedup key derivation
- _is_cooled_down():          Redis-based suppression logic
- _mark_sent():               Redis TTL write + None-safety
- send_telegram_alert():      disabled / missing config → no HTTP call
- send_telegram_alert():      correct URL, chat_id, text, parse_mode payload
- send_telegram_alert():      cooldown suppression and marking
- send_telegram_alert():      retry on timeout / non-fatal HTTP errors
- send_telegram_alert():      no retry on 4xx config errors
- send_telegram_alert():      sleeps between retries
- send_telegram_alert():      message truncated at 4096 chars
- send_telegram_alert():      never raises regardless of failure mode
- send_telegram_alert():      bot token does not appear in warning logs
- async_send_telegram_alert(): delegates to sync sender via thread executor
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import httpx
import pytest

from src.backend.infrastructure.notifications.telegram import (
    _COOLDOWN_TTL,
    _MAX_MSG_LEN,
    _RETRY_COUNT,
    _fingerprint,
    _is_cooled_down,
    _mark_sent,
    async_send_telegram_alert,
    send_telegram_alert,
)

# ── Test helpers ───────────────────────────────────────────────────────────────


def _settings(*, enabled: bool = True, token: str = "test_token", chat_id: str = "99999"):
    s = MagicMock()
    s.TELEGRAM_ALERTS_ENABLED = enabled
    s.TELEGRAM_BOT_TOKEN = token
    s.TELEGRAM_CHAT_ID = chat_id
    s.REDIS_URL = "redis://redis:6379/0"
    return s


def _ok():
    r = MagicMock()
    r.status_code = 200
    return r


def _err(code: int):
    r = MagicMock()
    r.status_code = code
    r.text = f"err {code}"
    return r


def _redis(*, exists: int = 0):
    c = MagicMock()
    c.ping.return_value = True
    c.exists.return_value = exists
    return c


def _run(
    message: str = "alert",
    *,
    post_side_effect=None,
    redis_exists: int = 0,
    redis_raise: Exception | None = None,
    sleep: bool = True,
):
    """
    Run send_telegram_alert with fully mocked httpx, redis, settings, and time.sleep.
    Returns (mock_post, mock_redis_client).
    """
    settings = _settings()
    redis_client = _redis(exists=redis_exists)

    post_mock = MagicMock()
    if post_side_effect is not None:
        post_mock.side_effect = post_side_effect
    else:
        post_mock.return_value = _ok()

    with (
        patch("src.backend.config.get_settings", return_value=settings),
        patch("src.backend.infrastructure.notifications.telegram.redis_lib") as mock_redis_mod,
        patch("src.backend.infrastructure.notifications.telegram.httpx.post", post_mock),
        patch("src.backend.infrastructure.notifications.telegram.time.sleep") as mock_sleep,
    ):
        if redis_raise is not None:
            mock_redis_mod.Redis.from_url.side_effect = redis_raise
        else:
            mock_redis_mod.Redis.from_url.return_value = redis_client

        send_telegram_alert(message)

    return post_mock, redis_client, mock_sleep


# ── _fingerprint ───────────────────────────────────────────────────────────────


class TestFingerprint:
    def test_returns_16_char_hex_string(self):
        fp = _fingerprint("hello")
        assert len(fp) == 16
        int(fp, 16)  # raises ValueError if not valid hex

    def test_same_first_line_produces_same_fingerprint(self):
        assert _fingerprint("Error A\ndetail 1") == _fingerprint("Error A\ndetail 2")

    def test_different_first_line_produces_different_fingerprint(self):
        assert _fingerprint("Error A") != _fingerprint("Error B")

    def test_uses_only_first_line_for_dedup(self):
        assert _fingerprint("line1\nX\nY") == _fingerprint("line1\nZ")

    def test_empty_string_does_not_raise(self):
        fp = _fingerprint("")
        assert len(fp) == 16

    def test_multiline_with_same_header_same_fp(self):
        long_body = "\n".join(["Same header"] + ["x" * 100 for _ in range(20)])
        assert _fingerprint(long_body) == _fingerprint("Same header")


# ── _is_cooled_down ────────────────────────────────────────────────────────────


class TestIsCooledDown:
    def test_returns_false_when_client_is_none(self):
        assert _is_cooled_down(None, "fp") is False

    def test_returns_true_when_redis_key_exists(self):
        client = MagicMock()
        client.exists.return_value = 1
        assert _is_cooled_down(client, "fp") is True

    def test_returns_false_when_redis_key_absent(self):
        client = MagicMock()
        client.exists.return_value = 0
        assert _is_cooled_down(client, "fp") is False

    def test_returns_false_when_redis_raises(self):
        client = MagicMock()
        client.exists.side_effect = Exception("connection lost")
        assert _is_cooled_down(client, "fp") is False

    def test_checks_correct_key_prefix(self):
        client = MagicMock()
        client.exists.return_value = 0
        _is_cooled_down(client, "abc123")
        key = client.exists.call_args[0][0]
        assert "abc123" in key
        assert key.startswith("tg:cd:")


# ── _mark_sent ─────────────────────────────────────────────────────────────────


class TestMarkSent:
    def test_noop_when_client_is_none(self):
        _mark_sent(None, "fp")  # must not raise

    def test_calls_setex_with_correct_ttl(self):
        client = MagicMock()
        _mark_sent(client, "fp")
        client.setex.assert_called_once()
        key, ttl, val = client.setex.call_args[0]
        assert ttl == _COOLDOWN_TTL

    def test_calls_setex_with_correct_value(self):
        client = MagicMock()
        _mark_sent(client, "fp")
        _, _, val = client.setex.call_args[0]
        assert val == "1"

    def test_key_contains_fingerprint(self):
        client = MagicMock()
        _mark_sent(client, "abc123")
        key = client.setex.call_args[0][0]
        assert "abc123" in key

    def test_silent_when_redis_raises(self):
        client = MagicMock()
        client.setex.side_effect = Exception("redis down")
        _mark_sent(client, "fp")  # must not raise


# ── send_telegram_alert — disabled / missing config ────────────────────────────


class TestSendDisabled:
    def test_no_http_call_when_alerts_disabled(self):
        with (
            patch("src.backend.config.get_settings", return_value=_settings(enabled=False)),
            patch("src.backend.infrastructure.notifications.telegram.httpx.post") as mock_post,
        ):
            send_telegram_alert("hello")
        mock_post.assert_not_called()

    def test_no_http_call_when_token_is_empty(self):
        with (
            patch("src.backend.config.get_settings", return_value=_settings(token="")),
            patch("src.backend.infrastructure.notifications.telegram.httpx.post") as mock_post,
        ):
            send_telegram_alert("hello")
        mock_post.assert_not_called()

    def test_no_http_call_when_chat_id_is_empty(self):
        with (
            patch("src.backend.config.get_settings", return_value=_settings(chat_id="")),
            patch("src.backend.infrastructure.notifications.telegram.httpx.post") as mock_post,
        ):
            send_telegram_alert("hello")
        mock_post.assert_not_called()


# ── send_telegram_alert — payload correctness ──────────────────────────────────


class TestSendPayload:
    def test_http_post_called_once(self):
        mock_post, _, _ = _run()
        mock_post.assert_called_once()

    def test_url_contains_bot_token(self):
        mock_post, _, _ = _run()
        url = mock_post.call_args[0][0]
        assert "test_token" in url

    def test_url_contains_sendMessage(self):
        mock_post, _, _ = _run()
        url = mock_post.call_args[0][0]
        assert "sendMessage" in url

    def test_payload_chat_id_matches_config(self):
        mock_post, _, _ = _run()
        assert mock_post.call_args.kwargs["json"]["chat_id"] == "99999"

    def test_payload_text_equals_message(self):
        mock_post, _, _ = _run("my alert text")
        assert mock_post.call_args.kwargs["json"]["text"] == "my alert text"

    def test_payload_parse_mode_is_html(self):
        mock_post, _, _ = _run()
        assert mock_post.call_args.kwargs["json"]["parse_mode"] == "HTML"

    def test_message_truncated_to_max_len(self):
        long_msg = "x" * (_MAX_MSG_LEN + 500)
        mock_post, _, _ = _run(long_msg)
        sent_text = mock_post.call_args.kwargs["json"]["text"]
        assert len(sent_text) == _MAX_MSG_LEN

    def test_short_message_not_truncated(self):
        mock_post, _, _ = _run("short")
        assert mock_post.call_args.kwargs["json"]["text"] == "short"


# ── send_telegram_alert — cooldown ────────────────────────────────────────────


class TestSendCooldown:
    def test_skips_http_when_redis_key_exists(self):
        mock_post, _, _ = _run(redis_exists=1)
        mock_post.assert_not_called()

    def test_sends_when_redis_key_absent(self):
        mock_post, _, _ = _run(redis_exists=0)
        mock_post.assert_called_once()

    def test_marks_cooldown_after_successful_send(self):
        _, redis_client, _ = _run()
        redis_client.setex.assert_called_once()

    def test_does_not_mark_cooldown_after_http_error(self):
        _, redis_client, _ = _run(post_side_effect=[_err(500)] * (_RETRY_COUNT + 1))
        redis_client.setex.assert_not_called()

    def test_sends_when_redis_is_unavailable(self):
        """Redis factory raises → cooldown skipped → alert still goes out."""
        mock_post, _, _ = _run(redis_raise=ConnectionError("no redis"))
        mock_post.assert_called_once()

    def test_does_not_mark_cooldown_when_redis_unavailable(self):
        # redis_client is never created, so setex is never called — just verify no crash
        _run(redis_raise=ConnectionError("no redis"))  # must not raise


# ── send_telegram_alert — retry logic ─────────────────────────────────────────


class TestSendRetry:
    def test_retries_on_timeout_up_to_limit(self):
        effects = [httpx.TimeoutException("t")] * (_RETRY_COUNT + 1)
        mock_post, _, _ = _run(post_side_effect=effects)
        assert mock_post.call_count == _RETRY_COUNT + 1

    def test_succeeds_on_second_attempt_after_timeout(self):
        effects = [httpx.TimeoutException("t"), _ok()]
        mock_post, _, _ = _run(post_side_effect=effects)
        assert mock_post.call_count == 2

    def test_retries_on_5xx_up_to_limit(self):
        effects = [_err(500)] * (_RETRY_COUNT + 1)
        mock_post, _, _ = _run(post_side_effect=effects)
        assert mock_post.call_count == _RETRY_COUNT + 1

    def test_no_retry_on_400(self):
        mock_post, _, _ = _run(post_side_effect=[_err(400)])
        assert mock_post.call_count == 1

    def test_no_retry_on_401(self):
        mock_post, _, _ = _run(post_side_effect=[_err(401)])
        assert mock_post.call_count == 1

    def test_no_retry_on_403(self):
        mock_post, _, _ = _run(post_side_effect=[_err(403)])
        assert mock_post.call_count == 1

    def test_no_retry_when_general_exception_raised(self):
        mock_post, _, _ = _run(post_side_effect=[RuntimeError("boom")])
        assert mock_post.call_count == 1

    def test_sleeps_between_retries(self):
        effects = [httpx.TimeoutException("t"), _ok()]
        _, _, mock_sleep = _run(post_side_effect=effects)
        mock_sleep.assert_called_once()

    def test_sleeps_twice_when_both_retries_fail(self):
        effects = [httpx.TimeoutException("t")] * (_RETRY_COUNT + 1)
        _, _, mock_sleep = _run(post_side_effect=effects)
        assert mock_sleep.call_count == _RETRY_COUNT

    def test_no_sleep_on_immediate_success(self):
        _, _, mock_sleep = _run()
        mock_sleep.assert_not_called()


# ── send_telegram_alert — error safety ────────────────────────────────────────


class TestSendSafety:
    def test_does_not_raise_when_httpx_post_raises(self):
        _run(post_side_effect=[RuntimeError("network down")])  # must not raise

    def test_does_not_raise_when_get_settings_raises(self):
        with patch("src.backend.config.get_settings", side_effect=RuntimeError("cfg error")):
            send_telegram_alert("test")  # must not raise

    def test_does_not_raise_when_redis_setex_raises(self):
        settings = _settings()
        redis_client = _redis()
        redis_client.setex.side_effect = Exception("redis write error")
        with (
            patch("src.backend.config.get_settings", return_value=settings),
            patch("src.backend.infrastructure.notifications.telegram.redis_lib") as mock_redis_mod,
            patch("src.backend.infrastructure.notifications.telegram.httpx.post", return_value=_ok()),
        ):
            mock_redis_mod.Redis.from_url.return_value = redis_client
            send_telegram_alert("test")  # must not raise

    def test_does_not_raise_on_repeated_timeouts(self):
        effects = [httpx.TimeoutException("t")] * 10
        _run(post_side_effect=effects)  # must not raise

    def test_token_absent_from_warning_log_on_http_error(self, caplog):
        settings = _settings()
        redis_client = _redis()
        effects = [_err(500)] * (_RETRY_COUNT + 1)
        with (
            patch("src.backend.config.get_settings", return_value=settings),
            patch("src.backend.infrastructure.notifications.telegram.redis_lib") as mock_redis_mod,
            patch("src.backend.infrastructure.notifications.telegram.httpx.post", side_effect=effects),
            patch("src.backend.infrastructure.notifications.telegram.time.sleep"),
            caplog.at_level(logging.WARNING, logger="coremarket.notifications.telegram"),
        ):
            mock_redis_mod.Redis.from_url.return_value = redis_client
            send_telegram_alert("Test alert")

        for record in caplog.records:
            assert "test_token" not in record.getMessage()


# ── async_send_telegram_alert ──────────────────────────────────────────────────


class TestAsyncSendTelegramAlert:
    async def test_delegates_to_sync_sender(self):
        with patch(
            "src.backend.infrastructure.notifications.telegram.send_telegram_alert"
        ) as mock_sync:
            await async_send_telegram_alert("async test message")
        mock_sync.assert_called_once_with("async test message")

    async def test_does_not_raise_when_sync_sender_raises(self):
        with patch(
            "src.backend.infrastructure.notifications.telegram.send_telegram_alert",
            side_effect=RuntimeError("sync error"),
        ):
            with pytest.raises(RuntimeError):
                await async_send_telegram_alert("msg")
            # Note: async wrapper does NOT swallow — sync sender does.
            # If sync sender raises (its own try/except failed), async propagates.
            # This documents that behaviour explicitly.
