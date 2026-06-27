# Telegram Alerts

CoreMarket sends Telegram messages for backend errors, Celery task failures, and Grafana alert rule violations.

---

## Architecture

```
Backend 500 error  ──► main.py exception handler
                           │
Celery task fails  ──► celery_app.py task_failure signal
                           │
                           ▼
                   infrastructure/notifications/telegram.py
                   ├── Redis cooldown check (5 min per alert)
                   └── httpx POST → Telegram Bot API

Grafana alert fires ──► Grafana Unified Alerting
                           └── Telegram contact point (native)
                               └── Telegram Bot API
```

Two independent paths:
- **Backend/Celery → Python sender** — catches runtime errors directly in code
- **Grafana → Telegram contact point** — fires on metric/log thresholds (5xx rate, Celery failures, ERROR log spike, backend down, high latency)

---

## Setup

### Step 1 — Create a Telegram bot

1. Open Telegram and message **@BotFather**
2. Send `/newbot`, follow the prompts
3. Copy the **bot token** (format: `123456789:ABCdef...`)

### Step 2 — Get your chat ID

Option A — @userinfobot:
1. Message **@userinfobot** on Telegram
2. It replies with your `id` — that is your chat ID

Option B — API:
1. Send any message to your new bot
2. Open `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Find `result[0].message.chat.id`

For a **group/channel**: add the bot as an admin, send a message, then check `getUpdates` for the group's chat ID (it will be negative, e.g. `-1001234567890`).

### Step 3 — Set environment variables

In your `.env` file:

```dotenv
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=987654321
TELEGRAM_ALERTS_ENABLED=true
```

### Step 4 — Restart services

```bash
docker compose up -d --force-recreate backend celery_worker grafana
```

---

## Testing

### Test the Python sender directly

```python
# Run from inside the backend container or with correct env vars
from src.backend.infrastructure.notifications.telegram import send_telegram_alert

send_telegram_alert(
    "🧪 <b>CoreMarket Test Alert</b>\n\n"
    "<b>Service:</b> backend\n"
    "<b>Message:</b> Telegram alerts are working!"
)
```

Or via a one-liner inside the running container:

```bash
docker compose exec backend python -c "
from src.backend.infrastructure.notifications.telegram import send_telegram_alert
send_telegram_alert('🧪 Test from CoreMarket backend')
"
```

### Test a Celery task failure

```bash
docker compose exec backend python -c "
from src.backend.celery_app import celery_app

@celery_app.task(name='test.fail')
def _fail():
    raise RuntimeError('intentional test failure')

_fail.apply()
"
```

### Test a Grafana alert

Open Grafana at http://localhost:3001, go to **Alerting → Alert rules**, find any CoreMarket rule, and click **Test rule**. If the contact point is configured correctly, a message will arrive in Telegram.

---

## Alert types

| Source | Trigger | Cooldown |
|--------|---------|---------|
| Python (backend) | Unhandled HTTP 500 exception | 5 min per unique error |
| Python (Celery) | Task failure signal | 5 min per task + error combo |
| Grafana | HTTP 5xx rate > 0.05 req/s for 5 min | 4 h (repeat_interval) |
| Grafana | Any Celery failure in 5 min | 4 h |
| Grafana | > 5 ERROR log lines in 5 min (Loki) | 4 h |
| Grafana | Backend `/metrics` unreachable for 2 min | 4 h |
| Grafana | p95 latency > 2 s for 5 min | 4 h |

---

## Anti-spam

The Python sender deduplicates alerts using Redis (db 2):
- Key: `tg:cd:<sha256_of_first_line[:200]>` (16 hex chars)
- TTL: 300 seconds (5 minutes)
- If Redis is unavailable, deduplication is skipped but the alert still sends

Grafana deduplication uses `repeat_interval: 4h` in `notification_policies.yml`.

---

## Message format examples

**Backend 500 error:**
```
🚨 CoreMarket Alert

Service: backend
Level: ERROR
Endpoint: POST /api/v1/items
Error: ValueError: invalid image format
```

**Celery task failure:**
```
🚨 CoreMarket — Celery Task Failed

Task: coremarket.tasks.generate_thumbnail
Error: OSError: cannot identify image file
Retries: 2
Task ID: 3f8a21bc
```

**Grafana alert:**
```
🚨 [CoreMarket] HTTP 5xx Error Rate

Status: FIRING
CoreMarket backend 5xx spike
HTTP error rate exceeded 0.05 req/s for 5+ minutes
Labels: severity=critical service=backend
```

---

## Grafana alert rules

Provisioned via `grafana/provisioning/alerting/alert_rules.yml`.
They are read-only in the UI — to edit, modify the YAML file and restart Grafana.

| Rule UID | Title | Threshold |
|----------|-------|-----------|
| `cm-http-5xx-rate` | HTTP 5xx Error Rate | > 0.05 req/s for 5 min |
| `cm-celery-task-failures` | Celery Task Failures | > 0 failures in 5 min |
| `cm-loki-error-spike` | Backend ERROR Log Spike | > 5 errors in 5 min |
| `cm-backend-down` | Backend Unreachable | `up` < 1 for 2 min |
| `cm-high-request-latency` | High API Latency (p95) | p95 > 2 s for 5 min |

To pause a rule without deleting it, set `isPaused: true` in `alert_rules.yml`.

---

## Disabling alerts

Set `TELEGRAM_ALERTS_ENABLED=false` in `.env` to disable only the Python sender.
Grafana contact point is independent — disable it in `contact_points.yml` or pause rules in `alert_rules.yml`.

---

## Troubleshooting

**No messages received:**
1. Check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set correctly
2. Check `TELEGRAM_ALERTS_ENABLED=true`
3. Look for `telegram_http_error` or `telegram_fatal` in backend logs:
   ```bash
   docker compose logs backend | grep telegram
   ```
4. Verify the bot was started: send `/start` to your bot in Telegram

**Grafana alerts not firing:**
1. Open Grafana → Alerting → Contact points → Test `Telegram Alerts`
2. Check that `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` env vars are set in the `grafana` service
3. Verify the datasource UIDs (`prometheus`, `loki`) match in `loki.yml`

**Too many messages:**
- Increase `_COOLDOWN_TTL` in `telegram.py` (default 300s)
- Increase `repeat_interval` in `notification_policies.yml` (default 4h)
