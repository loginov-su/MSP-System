# gunicorn.conf.py — конфигурация Gunicorn для портала МШП
# Запуск: gunicorn -c gunicorn.conf.py main:app
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 60
graceful_timeout = 30
keepalive = 65

# Проксируется через nginx (HTTPS до клиента)
forwarded_allow_ips = "127.0.0.1"

# Служебные файлы
accesslog = "/var/log/msp/gunicorn_access.log"
errorlog = "/var/log/msp/gunicorn_error.log"
loglevel = "info"

# Максимальный размер запроса (совпадает с client_max_body_size в nginx)
limit_request_line = 4096
limit_request_fields = 100
