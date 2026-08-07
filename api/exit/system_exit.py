from email.mime import application
import os
from fastapi import FastAPI
from flask import Flask, render_template, jsonify, request
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from httpx2 import query
from main import app, login_required, current_user # Нужна будет для того чтобы блокировать спец-страницы #

load_dotenv()


# Пароль для страницы охраны #

ADMIN_SQ_PASSWORD=os.environ["ADMIN_SQ_PASSWORD"]




bcrypt = Bcrypt()
login_manager = LoginManager()



# ------------------------------- FRONTEND ------------------------------- #

@app.route("/")
def login():
     return render_template("auth/login.html")

@app.route("/home")
@login_required
def home():
     return render_template("home/home.html")



@app.route("/create/exit")
@login_required
def home():
     return render_template("home/create_exit.html")


@app.route("/create/exit")
@login_required
def home():
     return render_template("home/create_exit.html")



@app.route("/create/exit/history")
@login_required
def home():
     return render_template("home/history_exit.html")


@app.route("/exit/application/<string:id>")
def exit_application():
     exit_application = exit_application.query.filter_by(id=id, is_deleted=False).first()
     if not exit_application:
          return render_template("404-exit.html"), 404
     
     # Проверяем, авторизован ли текущий пользователь как учащийся
     is_authorized = current_user.is_authenticated and isinstance(current_user, student)
    
     print(f"DEBUG: is_authenticated={current_user.is_authenticated}, is_student={isinstance(current_user, student)}, is_authorized={is_authorized}")

     return render_template('student_page.html', application=application, is_authorized=is_authorized)




@app.route("/guard_interface/exit/application")
@login_required
def uard_interface_today_applications_ui():
     if current_user.campus == "pole":
          return render_template("exit/guard_application.html", ampus=current_user.campus)
     else:
          return render_template('exit/guard_application.html', campus=current_user.campus)







# ------------------------------- Backend ------------------------------- #

@app.route("/exit/app/teacher/history", methods="POST, GET")
@login_required
def history():
     return jsonify(
          "student_name" == "student_name"
          "student_lastname" == "student_lastname"
          "student_group" == "student_group"
     )



@app.route('/api/teacher/exit_application/search')
@login_required
def searh_name():
    # 1. Проверка прав доступа
    if not getattr(current_user, 'is_dostup', False): 
        return render_template("auth/not_dostup.html"), 403

    # 2. Получение и обработка строки ФИО
    full_name = request.args.get('fio', '').strip()
    if not full_name:
        return jsonify([])

    from utils import split_full_name
    name, surname, lastname = split_full_name(full_name)

    # 3. Формирование запроса к БД и фильтрация по кампусу
    # Замените 'Student' на точное имя вашей модели (класса) в базе данных
    query = Student.query.filter(Student.campus == current_user.campus)

    # 4. Фильтрация по совпадению ФИО (регистронезависимый поиск по подстроке)
    if surname:
        query = query.filter(Student.surname.ilike(f"%{surname}%"))
    if name:
        query = query.filter(Student.name.ilike(f"%{name}%"))
    if lastname:
        query = query.filter(Student.lastname.ilike(f"%{lastname}%"))

    # 5. Получение результатов и удаление дубликатов
    results = query.all()
    result_list = []
    seen_students = set()

    for student_info in results:
        fio = f'{student_info.surname} {student_info.name} {student_info.lastname}'.strip()
        student_class = f'{student_info.group_number}{student_info.group_letter}'.strip()
        unique_key = f'{fio}|{student_class}'
        
        if unique_key not in seen_students:
            result_list.append({
                'name': fio,
                'class': student_class
            })
            seen_students.add(unique_key)

    return jsonify(result_list)
