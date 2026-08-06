from email.mime import application
import os
from re import search
from flask import Flask, render_template
from flask_login import current_user, login_required
from sqlalchemy import sql
from fastapi import FastAPI
from main import app, config
from datetime import timedelta, datetime
from dotenv import load_dotenv


# Данной функцией я достаю из .env, пароль от охраны, админ-пароль, ключ #
load_dotenv()


# Инцилизируем из .env, пароль от охраны и для заявок на выход #

SEQ_PASSWORD = os.environ["SEQ_PASSWORD"]
ADMIN_PASSWORD = os.environ["SEQ_PASSWORD"]

###



# Frontend App #
@app.route("/create_exit")
@login_required
def login():
   # Проверям от куда пользователь если доступа нет то кидаем на not_dostup.html #
    campus=current_user.campus
    efault_group_number=current_user.default_group_number, 
    default_group_letter=current_user.default_group_letter,
    if not current_user.is_confirmed: return render_template('not_dostup.html')
    return render_template("create_exit.html")


@app.route("/create_exit/history")
@login_required
def history():
    return render_template('history.html')



@app.route("/exit/application/<int:id>")
# Откроем страницу для ученика только если API будет верный # # Пример: ip/exit/application/<id>
# 1. Ищем активную заявку в базе данных
def exit():
    current_application = search.query.filter_by(id=id, is_deleted=False).first()
    
    if not current_application:
        return render_template('application-404.html'), 404

    is_student = isinstance(current_user, kids)
    
    is_authorized = current_user.is_authenticated and is_student
    
    # Отладочный вывод в консоль
    print(f"DEBUG: auth={current_user.is_authenticated}, student={is_student}, total={is_authorized}")
    
    return render_template(
        'student_page.html',
        application=current_application,
        is_authorized=is_authorized,
    )



@app.route("/exit/application/404")
def not_found_application():
# Данная функция нужна для того чтобы понять что пользователь ученик #
 is_student=current_user.student.is__authenticated and isinstance(current_user, student)
 print(f"DEBUG 404: is_authenticated={current_user.is_authenticated}, is_student={isinstance(current_user, student)}, is_authorized={is_authorized}")
    
 return render_template('application-404.html', is_authorized=is_authorized)




# Рендрим страницу охраны #
 @app.route()
 def guard_application_all():
    if current_user.campus == "all":
        return render_template("all_guard_application.html", name_sq=current_user.qr.all)
    else:
        return render_template("all_guard_application.html", name_sq=current_user.qr.all2)


