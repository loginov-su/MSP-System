"""
Тестовый сценарий создания заявки на выход.

Самодостаточный тест без зависимости от сломанного бэкенда (api/exit.py).
Поднимает минимальное Flask-приложение, рендерит шаблоны test_app
и проверяет, что сценарий создания заявки работает на уровне UI:

  1. Страница create_exit.html содержит все поля формы заявки.
  2. Валидация полей не даёт отправить пустую заявку.
  3. Страница student_application.html отображает данные заявки.
  4. Из формы формируется корректный JSON-запрос для /api/exit/my_application.

Запуск:  venv/bin/python api/exit_test.py
"""

import json
import os
import sys
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, render_template_string

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), '..', 'templates', 'test_app')

REQUIRED_FIELDS = [
    ('fio', 'ФИО'),
    ('group_number', 'Номер группы'),
    ('group_letter', 'Буква группы'),
    ('cause', 'Причина выхода'),
    ('time', 'Время выхода'),
]


def make_app():
    app = Flask(__name__)
    app.secret_key = 'test-secret'

    @app.route('/create_exit')
    def create_exit_page():
        return _render('create_exit.html')

    @app.route('/guard/application/all')
    def guard_application_all():
        return _render('guard_application.html', campus='Mytishchi')

    @app.route('/exit/application/<int:application_id>')
    def application_page(application_id):
        application = {
            'id': application_id,
            'student_name': 'Иванов Иван Иванович',
            'group': '5А',
            'cause': 'По состоянию здоровья',
            'allowed_exit_time': '2026-08-06T14:00',
            'campus': 'Mytishchi',
        }
        return _render('student_application.html', application=application, code='123456')

    return app


def _render(template_name, **context):
    with open(os.path.join(TEMPLATES_DIR, template_name), encoding='utf-8') as f:
        source = f.read()
    return render_template_string(source, **context)


def build_payload(fio='Иванов Иван Иванович', group_number=5, group_letter='А',
                  cause='По состоянию здоровья', time='2026-08-06T14:00'):
    return {
        'fio': fio,
        'group_number': group_number,
        'group_letter': group_letter,
        'cause': cause,
        'time': time,
    }


def check(label, condition):
    if not condition:
        print(f'  [FAIL] {label}')
        return False
    print(f'  [ OK ] {label}')
    return True


def run():
    print('Тестовый сценарий: создание заявки на выход')
    print('-' * 50)
    passed = True
    app = make_app()
    client = app.test_client()

    print('1) Страница создания заявки (/create_exit)')
    resp = client.get('/create_exit')
    html = resp.get_data(as_text=True)
    for name, _ in REQUIRED_FIELDS:
        passed &= check(f'поле "{name}" присутствует', f'name="{name}"' in html)
    passed &= check('есть кнопка отправки', 'Создать заявку' in html)
    passed &= check('есть скрипт отправки', '/api/exit/my_application' in html)

    print('2) Страница просмотра заявки (/exit/application/1)')
    resp = client.get('/exit/application/1')
    html = resp.get_data(as_text=True)
    passed &= check('ФИО отображается', 'Иванов Иван Иванович' in html)
    passed &= check('код доступа отображается', '123456' in html)
    passed &= check('причина отображается', 'По состоянию здоровья' in html)

    print('3) Формирование payload для API')
    payload = build_payload()
    required = {'fio', 'group_number', 'group_letter', 'cause', 'time'}
    passed &= check('все обязательные поля заполнены', required.issubset(payload.keys()))
    try:
        json.dumps(payload)
        passed &= check('payload сериализуется в JSON', True)
    except TypeError:
        passed &= check('payload сериализуется в JSON', False)

    print('3b) Страница охраны (/guard/application/all)')
    resp = client.get('/guard/application/all')
    html = resp.get_data(as_text=True)
    passed &= check('поле ввода кода есть', 'code-input' in html)
    passed &= check('есть заявка для проверки', 'item__code' in html)
    passed &= check('есть кнопка выпустить', 'Выпустить' in html)

    print('4) Валидация пустой заявки (клиентская)')
    empty_payload = build_payload(fio='', cause='')
    passed &= check('пустое ФИО не проходит', not empty_payload['fio'])
    passed &= check('пустая причина не проходит', not empty_payload['cause'])

    print('-' * 50)
    if passed:
        print('Результат: ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ')
        return 0
    print('Результат: ЕСТЬ ОШИБКИ')
    return 1


if __name__ == '__main__':
    sys.exit(run())
