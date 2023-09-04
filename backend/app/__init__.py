from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .models import db, Database, Student


def create_app():
    app = FastAPI()
    
    templates = Jinja2Templates(directory="C:\\Users\\USER\\Desktop\\Project\\coding\\PedProPiTakSukSa\\templates")
    

    @app.get('/', response_class=HTMLResponse)
    def login(request: Request):
        return templates.TemplateResponse('login.html', {'request': request})

    @app.get('/register/student', response_class=HTMLResponse)
    def register_student(request: Request):
        return templates.TemplateResponse('register_student.html', {'request': request})
    
    @app.post('/register/success')
    async def register(name: str = Form(...), email: str = Form(...), password: str = Form(...), Lname: str = Form(...), \
            Nname: str = Form(...), SnationNumber: str = Form(...), Sphone: str = Form(...), Saddress: str = Form(...), Scity: str = Form(...), Szip: str = Form(...)):
    # Create a new Student entity and save it to the database
        new_student = Student(
        Sname=name,
        Semail=email,
        Spassword=password,
        Slastname=Lname,
        Snickname=Nname,
        SnationNumber=SnationNumber,
        Sphone=Sphone,
        Saddress=Saddress,
        Scity=Scity,
        Szip=Szip,
        Sstatus= "Student"
        )
        db.commit()  # Save the new student to the database

        # You can implement additional logic here, such as sending a confirmation email
    
        return {"message": "Registration successful"}

    @app.get('/register/teacher', response_class=HTMLResponse)
    def register_teacher(request: Request):
        return templates.TemplateResponse('register_teacher.html', {'request': request})

    @app.post('/login')
    def postlogin(request: Request):
        return ("login")
    
    return app

create_app()


