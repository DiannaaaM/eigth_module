# LMS API

## Контейнерная локальная разработка

### Пример запуска
1. Скопируйте шаблон: `cp example.env .env` и заполните секреты (`SECRET_KEY`, Stripe, данные БД, `ALLOWED_HOSTS`, `EMAIL_*` и т.д.).
2. Убедитесь, что Docker Engine и плагин Docker Compose установлены.
3. Запустите все сервисы одной командой:  
   `docker compose up --build -d`
4. Приложение доступно по адресу `http://localhost:80` (или `http://localhost:8000`, если вы обращаетесь к контейнеру `web` напрямую).
5. Статические файлы и медиа сохраняются в выделенных томах (`static_data`, `media_data`), а `nginx` проксирует запросы к `web`.

### Быстрые команды
- Миграции и сбор статических файлов уже выполняются внутри `web` благодаря `entrypoint.sh`, но для ручного запуска используйте:
  `docker compose exec web python manage.py migrate --noinput`
  `docker compose exec web python manage.py collectstatic --noinput`
- Запустить тесты: `docker compose run --rm web python manage.py test`
- Запустить линтер локально: `pip install ruff && ruff check .`
- Остановить все: `docker compose down`

## Сервисы проекта
Docker Compose поднимает по одному контейнеру для каждого сервиса:
- `db` — PostgreSQL 16 с томом `db_data`.
- `redis` — брокер/бекенд для Celery.
- `web` — Django + Gunicorn, запускает `entrypoint.sh`, который выполняет миграции и `collectstatic`.
- `celery` и `celery-beat` — воркер и планировщик, подключенные к Redis.
- `nginx` — обратный прокси на основе `nginx:1.25-alpine`, который раздает статические/медиа-ресурсы и проксирует запросы на `web`.

## CI/CD через GitHub Actions

Файл workflow находится в `.github/workflows/ci_cd.yml` и срабатывает на каждый push. Последовательность:
1. **Lint** — устанавливает `ruff` и проверяет весь проект.
2. **Tests** — поднимает PostgreSQL и Redis, устанавливает зависимости и запускает `python manage.py test`.
3. **Docker build** — собирает образ из `Dockerfile` (`docker build --pull --tag lms-api:ci .`).
4. **Deploy** — через `appleboy/ssh-action` подключается к серверу и выполняет:
   - `git fetch && git checkout develop && git reset --hard origin/develop`
   - `docker compose pull` и `docker compose up -d --build`
   - `docker compose exec -T web python manage.py collectstatic --noinput`
   - `docker compose restart web celery celery-beat nginx`

Чтобы CI/CD работал, добавьте секреты:
- `SSH_HOST`, `SSH_PORT`, `SSH_USER`, `SSH_KEY` — для доступа по SSH.
- `PROJECT_DIR` — путь к каталогу проекта на сервере (например, `/var/www/eigth_module`).

## Деплой на удаленный сервер

### Подготовка
```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install git docker.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker deploy
```
Доступ к серверу обеспечьте ключом, привязанным к `deploy`. После этого перезапустите сессию пользователя, чтобы вступили в силу группы.

Откройте порт 22 и 80:
```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
sudo ufw enable
```

### Разворачивание
1. Клонируйте проект и перейдите в директорию:
   `git clone https://github.com/DiannaaaM/eigth_module.git /var/www/eigth_module`
2. Перейдите в папку и создайте `.env`:
   `cd /var/www/eigth_module && cp example.env .env`
3. Настройте `ALLOWED_HOSTS` и другие переменные (включая `SECRET_KEY`, `STRIPE_*`, `DB_*`, `EMAIL_*`, `CELERY_*`). В CI/CD эти значения подаются через GitHub Secrets и `.env`.
4. Запустите контейнеры:
   `docker compose up -d --build`
5. После этого проект доступен по адресу `http://lms.example.com` (замените на свой домен или IP) — укажите этот адрес в `ALLOWED_HOSTS`.

### Обновления
На сервере достаточно:
```bash
cd /var/www/eigth_module
git fetch origin develop
git checkout develop
git reset --hard origin/develop
docker compose pull
docker compose up -d --build
```
CI/CD делает то же самое и перезапускает сервисы автоматически.

## Дополнительно
Каталог `deploy/` содержит примерные конфигурации `nginx`, `gunicorn.socket` и `gunicorn.service`, если вы захотите запускать проект без Docker. При контейнерном деплое они не обязательны, но могут помочь для отладки.
