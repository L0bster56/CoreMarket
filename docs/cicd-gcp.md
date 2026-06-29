# CI/CD на GCP — Пошаговая инструкция

## Архитектура

```
git push → main
    │
    ▼
GitHub Actions: CI (ci.yml)
  • pytest (backend)
  • tsc --noEmit (frontend)
    │ success
    ▼
GitHub Actions: CD (cd.yml)
  ┌─ Job 1: Build & Push ──────────────────────────────┐
  │  docker build backend  → DockerHub :sha + :latest  │
  │  docker build frontend → DockerHub :sha + :latest  │
  └────────────────────────────────────────────────────┘
    │
    ▼
  ┌─ Job 2: Deploy (SSH) ──────────────────────────────┐
  │  SSH → GCP VM                                      │
  │  git pull                                          │
  │  docker compose pull backend frontend              │
  │  docker compose up -d --no-build                  │
  └────────────────────────────────────────────────────┘
    │
    ▼
  ┌─ Job 3: Smoke test ────────────────────────────────┐
  │  curl проверка сайта + API                         │
  │  Telegram уведомление                              │
  └────────────────────────────────────────────────────┘
```

---

## Что потребуется

- GCP VM с запущенным проектом (`/opt/coremarket`)
- Аккаунт на [hub.docker.com](https://hub.docker.com)
- GitHub репозиторий

---

## Шаг 1 — DockerHub: создать репозитории и токен

1. Зайди на [hub.docker.com](https://hub.docker.com) → **Create repository**
2. Создай два репозитория:
   - `YOUR_USERNAME/coremarket-backend` (Private)
   - `YOUR_USERNAME/coremarket-frontend` (Private)
3. Создай Access Token: **Account Settings → Security → New Access Token**
   - Scope: `Read, Write, Delete`
   - Скопируй токен — он показывается один раз

---

## Шаг 2 — SSH ключ для деплоя

На своём компьютере сгенерируй ключ:

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/coremarket_deploy
# Passphrase: оставь пустым (Enter)
```

Получишь два файла:
- `coremarket_deploy` — приватный (→ в GitHub Secret)
- `coremarket_deploy.pub` — публичный (→ на VM)

Добавь публичный ключ на VM одним из способов:

**Способ А — через GCP Console:**
- Compute Engine → VM → Edit → SSH Keys → Add Item → вставь содержимое `coremarket_deploy.pub`

**Способ Б — через браузерный SSH в консоли GCP:**
```bash
echo "ssh-ed25519 AAAA...твой_ключ... github-actions-deploy" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Проверь с локальной машины:
```bash
ssh -i ~/.ssh/coremarket_deploy YOUR_USER@YOUR_VM_IP "echo connected"
# Должно вывести: connected
```

> **Где узнать YOUR_USER:** GCP Console → Compute Engine → VM → вкладка SSH → имя пользователя в строке подключения (`username@VM_IP`).

---

## Шаг 3 — Подготовить VM

### 3.1 Проект находится в `~/CoreMarket`

Путь в workflow: `cd ~/CoreMarket`. Если перенесёшь проект в другое место — обнови эту строку в `cd.yml` и `rollback.yml`.

### 3.2 Убедиться что remote указывает на GitHub

```bash
cd ~/CoreMarket
git remote -v
# должно быть: origin  https://github.com/YOUR_USER/CoreMarket.git
```

### 3.3 Убедиться что `.env` на VM заполнен

```bash
ls -la /opt/coremarket/.env
# должен быть файл с production-значениями
```

---

## Шаг 4 — GitHub: добавить Secrets и Variables

Перейти: **Settings → Secrets and variables → Actions**

### Secrets (секретные)

| Имя | Значение |
|-----|---------|
| `DOCKERHUB_USERNAME` | Логин на DockerHub (например `l0bster56`) |
| `DOCKERHUB_TOKEN` | Access Token DockerHub (из Шага 1) |
| `VM_HOST` | Внешний IP VM (например `34.123.45.67`) |
| `VM_USER` | SSH-пользователь на VM (например `ubuntu`) |
| `VM_SSH_PRIVATE_KEY` | Содержимое файла `~/.ssh/coremarket_deploy` (весь текст включая `-----BEGIN...`) |
| `TELEGRAM_BOT_TOKEN` | Токен Telegram-бота (для уведомлений) |
| `TELEGRAM_CHAT_ID` | Chat ID для уведомлений |

### Variables (нечувствительные)

| Имя | Значение |
|-----|---------|
| `PUBLIC_URL` | URL сайта, например `https://sanjaranvarov.uz` |

---

## Шаг 5 — Первый деплой

Просто сделай push в `main`:

```bash
git add .
git commit -m "setup: CI/CD"
git push origin main
```

Следить за прогрессом: **GitHub → Actions → CD — Deploy to GCP**

Pipeline занимает ~5-8 минут (первая сборка дольше из-за отсутствия кэша).

---

## Ручной деплой без изменений кода

**GitHub → Actions → CD — Deploy to GCP → Run workflow** → Run.

---

## Откат (Rollback)

Если после деплоя что-то сломалось:

1. Найти SHA предыдущего рабочего деплоя:
   ```bash
   git log --oneline -10
   ```
   Или в GitHub → Actions → CD → найти успешный run → взять `image_tag` из логов.

2. **GitHub → Actions → Rollback — Deploy specific image tag → Run workflow**
   - `image_tag`: SHA коммита рабочей версии
   - `reason`: кратко почему откат

Rollback деплоит именно тот образ из DockerHub и присылает Telegram-уведомление.

---

## Просмотр текущего статуса на VM

```bash
# SSH на VM
ssh YOUR_USER@YOUR_VM_IP

cd ~/CoreMarket

# Какие контейнеры запущены
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Какие образы сейчас используются
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.gcp.yml images

# Логи backend
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs backend --tail=100 -f

# Логи frontend
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs frontend --tail=100 -f
```

---

## Troubleshooting

### CD не запускается автоматически после CI

Проверить: в `ci.yml` должно быть `name: CI` (уже есть). CD слушает именно это имя через `workflow_run`.

### SSH: Permission denied

```bash
# Проверить с локальной машины
ssh -i ~/.ssh/coremarket_deploy -v YOUR_USER@YOUR_VM_IP

# На VM проверить authorized_keys
cat ~/.ssh/authorized_keys
# Должна быть строка с твоим ключом

# Права на файлы
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

Если VM использует **OS Login** (GCP фича) — метод с `authorized_keys` не работает. В GCP Console: VM → Edit → отключить OS Login, или добавить ключ через `gcloud compute os-login ssh-keys add`.

### docker login failed

Проверить токен: токен DockerHub должен иметь права `Read, Write`. Убедиться что `DOCKERHUB_USERNAME` и `DOCKERHUB_TOKEN` в GitHub Secrets написаны без пробелов.

### docker compose pull: image not found

Убедиться что репозитории на DockerHub созданы (не просто аккаунт, а именно `coremarket-backend` и `coremarket-frontend`).

Первый push в новый репозиторий DockerHub создаёт его автоматически, если аккаунт существует.

### frontend не обновился визуально

`NEXT_PUBLIC_API_URL` запекается в образ при сборке. Если поменял `PUBLIC_URL` в GitHub Variables — нужен новый деплой (пересборка образа).
Hard refresh в браузере: `Ctrl+Shift+R`.

### git reset --hard failed на VM

Если на VM есть незакоммиченные изменения (например, отредактировал `.env`):
```bash
# .env не трекается git-ом, поэтому проблема в другом файле
git status   # посмотреть что изменено
git stash    # спрятать изменения
```

`.env` в `.gitignore` — git его не трогает.
