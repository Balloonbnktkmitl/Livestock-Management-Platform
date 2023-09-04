from fastapi import FastAPI, Request
from pony.orm import Database
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .models import db, User


def create_app():
    app = FastAPI()
    
    db = Database()

    db.bind(provider='mysql', host='161.246.127.24', user='dbproject', passwd='db', db='db', port=9031)
    db.generate_mapping(create_tables=True)
    templates = Jinja2Templates(directory="C:\\Users\\USER\\Desktop\\Project\\coding\\templates")
    

    @app.get('/', response_class=HTMLResponse)
    def login(request: Request):
        return templates.TemplateResponse('login.html', {'request': request})

    @app.get('/register/student', response_class=HTMLResponse)
    def register_student(request: Request):
        return templates.TemplateResponse('register_student.html', {'request': request})

    @app.get('/register/teacher', response_class=HTMLResponse)
    def register_teacher(request: Request):
        return templates.TemplateResponse('register_teacher.html', {'request': request})

    @app.post('/login')
    def postlogin(request: Request):
        return ("login")
    
    return app

create_app()


