import os
from re import search
from main import app
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from flask_login import current_user, login_required
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Константы из .env
SEQ_PASSWORD = os.getenv["SEQ_PASSWORD"]
ADMIN_PASSWORD = os.getenv["ADMIN_PASSWORD"]  

# Константы для избежания магических чисел, "Позже будет удаленно" #
CAMPUS_MAPPING = {5: 'Oktyabrskoye Pole', 6: 'Oktyabrskoye Pole'}
DEFAULT_CAMPUS = 'Mytishchi'

# Вспомогательная функция для разбиения ФИО
def split_full_name(full_name):
    """Разбивает полное имя на фамилию, имя и отчество."""
    if not full_name:
        return '', '', ''
    parts = full_name.split()
    surname, name, lastname = parts + [''] * (3 - len(parts))
    return name, surname, lastname

def get_campus_by_group(group_number):
    """Определяет корпус по номеру группы."""
    return CAMPUS_MAPPING.get(group_number, DEFAULT_CAMPUS)

# -------------------- FRONTEND ROUTES --------------------

@app.route("/create_exit")
@login_required
def create_exit_page():
    """Страница создания заявки на выход."""
    if not current_user.is_confirmed:
        return render_template('not_dostup.html')
    return render_template("create_exit.html")

@app.route("/create_exit/history")
@login_required
def history_page():
    """Страница истории заявок."""
    return render_template('history.html')

@app.route("/exit/application/<int:application_id>")
def application_page(application_id):
    """Страница просмотра заявки."""
    application = search.query.filter_by(id=application_id, is_deleted=False).first()
    
    if not application:
        return render_template('application-404.html'), 404

    is_authorized = current_user.is_authenticated and isinstance(current_user, kids)
    
    return render_template(
        'student_page.html',
        application=application,
        is_authorized=is_authorized,
    )

@app.route("/exit/application/404")
def not_found_application_page():
    """Страница ошибки 404 для заявки."""
    is_student = current_user.is_authenticated and isinstance(current_user, student)
    is_authorized = is_student  # Упрощено
    return render_template('application-404.html', is_authorized=is_authorized)

@app.route("/guard/application/all")
def guard_application_all():
    """Страница охраны со всеми заявками."""
    campus = current_user.campus
    name_sq = current_user.qr.OktyabrskoyePole if campus == "all" else current_user.qr.Mytishchi
    return render_template("all_guard_application.html", name_sq=name_sq)

# -------------------- BACKEND API ROUTES --------------------

@app.route("/api/exit/my_application", methods=["POST"])
@login_required
def create_my_application():
    """API для создания заявки на выход."""
    # Проверка доступа
    if not current_user.is_confirmed:
        return jsonify({'status': 'error', 'message': 'Доступ запрещен'}), 403

    # Получение данных
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Некорректные данные запроса'}), 400

    # Валидация обязательных полей
    required_fields = ['fio', 'group_number', 'cause', 'time']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({
            'status': 'error', 
            'message': f'Отсутствуют обязательные поля: {", ".join(missing_fields)}'
        }), 400

    try:
        group_number = int(data['group_number'])
    except (ValueError, TypeError):
        return jsonify({'status': 'error', 'message': 'Номер группы должен быть числом'}), 400

    # Определение корпуса
    expected_campus = get_campus_by_group(group_number)
    
    # Проверка соответствия корпуса
    if current_user.campus != expected_campus:
        return jsonify({
            'status': 'error', 
            'message': 'Вы не можете создавать заявки для этого корпуса'
        }), 403

    # Проверка блокировки группы
    is_blocked = teacher_not_dostup.query.filter(
        teacher_not_dostup.default_group_number == group_number,
        teacher_not_dostup.default_group_letter == data['group_letter'],
        teacher_not_dostup.block_class_exit == True
    ).first()

    if is_blocked and is_blocked.id != current_user.id:
        return jsonify({
            'status': 'error', 
            'message': 'Учитель запретил выход для этой группы'
        }), 403

    # Разбиение ФИО
    name, surname, lastname = split_full_name(data['fio'])
    campus = expected_campus

    # Поиск или создание студента
    student_info = student.query.filter_by(
        name=name, 
        surname=surname, 
        lastname=lastname,
        group_number=group_number,
        group_letter=data['group_letter']
    ).first()

    if not student_info:
        student_info = student(
            name=name,
            surname=surname,
            lastname=lastname,
            group_number=group_number,
            group_letter=data['group_letter'],
            campus=campus
        )
        db.session.add(student_info)
        db.session.commit()
    elif not student_info.campus:
        student_info.campus = campus
        db.session.commit()

    # Генерация кода
    import bcrypt
    code = str(datetime.now().timestamp()).replace('.', '')[-6:]  # Простой генератор кода
    hashed_code = bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Создание заявки
    new_application = exit_applications(
        student_id=student_info.id,
        teacher_id=current_user.id,
        code=hashed_code,
        cause=data['cause'],
        allowed_exit_time=data['time'],
        campus=campus
    )
    db.session.add(new_application)
    db.session.commit()

    return jsonify({
        'status': 'success', 
        'application_id': new_application.id, 
        'code': code
    }), 200

@app.route("/exit/guard/api/exit_application", methods=["GET", "POST"])
def guard_api():
    """API для охраны."""
    now = datetime.now()
    # Дальнейшая логика...
    return jsonify({'status': 'ok', 'timestamp': now.isoformat()})