# LMS API

## Быстрый старт (локально)
1. Создайте `.env` по примеру `example.env`.
2. Установите зависимости: `pip install -r requirements.txt`.
3. Примените миграции: `python manage.py migrate`.
4. Запустите сервер: `python manage.py runserver`.

## Настройка удаленного сервера

Ниже — базовая инструкция для Ubuntu. Пути и пользователей можно заменить под себя.

### 1) Подготовка сервера
```bash
sudo apt update && sudo apt -y upgrade
sudo apt -y install python3 python3-venv python3-pip git nginx postgresql postgresql-contrib
```

### 2) Безопасность
```bash
sudo adduser deploy
sudo usermod -aG sudo deploy
sudo mkdir -p /home/deploy/.ssh
sudo nano /home/deploy/.ssh/authorized_keys
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

UFW:
```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
sudo ufw enable
```

### 3) PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE lms;
CREATE USER lms_user WITH PASSWORD 'strong_password';
ALTER ROLE lms_user SET client_encoding TO 'utf8';
ALTER ROLE lms_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE lms_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE lms TO lms_user;
\q
```

### 4) Деплой проекта
```bash
sudo mkdir -p /var/www/eigth_module
sudo chown -R deploy:www-data /var/www/eigth_module
sudo chmod -R 775 /var/www/eigth_module
sudo -u deploy git clone https://github.com/DiannaaaM/eigth_module.git /var/www/eigth_module
cd /var/www/eigth_module
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Создайте `.env` на сервере по примеру `example.env`:
```bash
cp example.env .env
```

### 5) Gunicorn + Systemd
Примеры unit-файлов лежат в `deploy/`.
```bash
sudo cp deploy/gunicorn.socket /etc/systemd/system/gunicorn.socket
sudo cp deploy/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl start gunicorn.socket
sudo systemctl enable gunicorn.socket
```

### 6) Nginx
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/eigth_module
sudo ln -s /etc/nginx/sites-available/eigth_module /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 7) Миграции и статика
```bash
. /var/www/eigth_module/.venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

## GitHub Actions workflow

Файл workflow находится в `.github/workflows/ci_cd.yml`.  
Он запускается на каждый push, выполняет тесты и деплой на сервер, если ветка `develop`.

### Secrets для GitHub Actions
Добавьте в репозитории:
- `SSH_HOST` — IP или домен сервера
- `SSH_PORT` — порт SSH (обычно `22`)
- `SSH_USER` — пользователь (например, `deploy`)
- `SSH_KEY` — приватный ключ для доступа
- `PROJECT_DIR` — путь к проекту (например, `/var/www/eigth_module`)

## Переменные окружения
Шаблон файла `.env` — `example.env`.  
Чувствительные значения (`SECRET_KEY`, данные БД, ключи Stripe) должны храниться в `.env` и в Secrets GitHub.

