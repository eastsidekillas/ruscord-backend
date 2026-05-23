# Ruscord Backend

Django + Django Channels бэкенд для Discord-клона.

---

## Требования

- Python 3.12+
- [Poetry](https://python-poetry.org/)
- Docker + Docker Compose

---

## Dev-режим (локальная разработка)

### 1. Установка зависимостей

**macOS / Linux:**
```bash
pip install poetry
poetry install
```

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
После установки добавь в переменную `Path`:
```
C:\Users\<ИМЯ_ПОЛЬЗОВАТЕЛЯ>\AppData\Roaming\Python\Scripts
```
```powershell
poetry install
```

### 2. Настройка окружения

Скопируй `.env.example` в `.env` и убедись что там стоит:
```
DJANGO_ENV=dev
```

По умолчанию используется SQLite — база данных создаётся автоматически.

### 3. Запуск инфраструктуры (Redis + PostgreSQL)

```bash
docker-compose -f docker-compose.dev.yml up -d
```

Это запускает только Redis и PostgreSQL. Django запускается отдельно.

### 4. Применение миграций

```bash
cd src
poetry run python manage.py migrate
```

### 5. Запуск сервера

Обычный HTTP (без WebSocket):
```bash
cd src
poetry run python manage.py runserver
```

С поддержкой WebSocket (рекомендуется):
```bash
cd src
poetry run daphne -p 8000 -b 0.0.0.0 ruscord.asgi:application
```

### 6. Создание суперпользователя (опционально)

```bash
cd src
poetry run python manage.py createsuperuser
```

Панель администратора: http://localhost:8000/admin/  
Swagger-документация: http://localhost:8000/api/docs/swagger/

---

## Prod-режим (Docker)

### 1. Настройка окружения

Создай `.env` на основе `.env.example`, заполни обязательные поля:

```env
DJANGO_ENV=prod
DJANGO_SECRET_KEY=<длинная случайная строка>
PUBLIC_HOST=your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com

DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=ruscord
DATABASE_USER=ruscord
DATABASE_PASSWORD=<пароль>
DATABASE_HOST=postgres
DATABASE_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

LIVEKIT_API_KEY=<ключ>
LIVEKIT_API_SECRET=<секрет>

STATIC_ROOT=/app/static
MEDIA_ROOT=/app/media
```

Сгенерировать `SECRET_KEY`:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 2. Запуск

```bash
docker-compose up -d
```

Это автоматически:
- применит миграции
- соберёт статику
- запустит PostgreSQL, Redis, LiveKit, Django (Daphne) и фронтенд (nginx)

### 3. Остановка

```bash
docker-compose down
```

Для полного сброса (включая данные):
```bash
docker-compose down -v
```

---

## Структура настроек

| Файл               | Назначение                                            |
|--------------------|-------------------------------------------------------|
| `settings.py`      | Диспетчер — выбирает режим по `DJANGO_ENV`            |
| `settings_base.py` | Общие настройки для обоих режимов                     |
| `settings_dev.py`  | Dev: `DEBUG=True`, куки без HTTPS, SQLite             |
| `settings_prod.py` | Prod: `DEBUG=False`, HTTPS-заголовки, валидация ключей|