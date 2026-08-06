#!/usr/bin/env bash
# pull.sh — обновление кода и перезапуск портала МШП
# Использование:
#   ./pull.sh                 # обычное обновление
#   ./pull.sh --install-deps  # обновить код И установить зависимости
set -euo pipefail

APP_DIR="${APP_DIR:-/var/www/msp}"
GUNICORN_SERVICE="${GUNICORN_SERVICE:-msp}"

cd "$APP_DIR"

echo "==> Обновление кода (git pull)"
git pull origin "$(git branch --show-current)"

if [[ "${1:-}" == "--install-deps" ]]; then
    echo "==> Установка зависимостей"
    if [[ -x venv/bin/pip ]]; then
        venv/bin/pip install --upgrade -r requirements.txt
    else
        pip install --upgrade -r requirements.txt
    fi
fi

echo "==> Применение настроек nginx"
if nginx -t >/dev/null 2>&1; then
    cp -f nginx.conf /etc/nginx/conf.d/msp.conf
    nginx -t && nginx -s reload
    echo "    nginx обновлён и перезагружен"
else
    echo "    WARN: nginx не настроен локально — пропускаем"
fi

echo "==> Перезапуск приложения (gunicorn: $GUNICORN_SERVICE)"
if systemctl list-units --type=service --all | grep -q "$GUNICORN_SERVICE"; then
    systemctl restart "$GUNICORN_SERVICE"
    sleep 2
    systemctl --no-pager status "$GUNICORN_SERVICE" || true
else
    echo "    WARN: systemd-сервис '$GUNICORN_SERVICE' не найден — не перезапускаем"
fi

echo ""
echo "==> Готово. Проверка доступности..."
curl -sI "http://127.0.0.1:8000/" | head -1 || true

echo ""
echo "Проверьте сайт и применённые изменения."