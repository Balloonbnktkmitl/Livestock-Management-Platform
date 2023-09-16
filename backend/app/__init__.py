from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .models import db, Database, Users, Farms, Customers, FarmOwners, Staffs, Animals, Products, Locations, Countries, Regions
from pony.orm import db_session

def create_app():
    app = FastAPI()
    
    templates = Jinja2Templates(directory="C:\\Users\\USER\\Desktop\\Project\\coding\\PedProPiTakSukSa\\templates")
    

    @app.get('/', response_class=HTMLResponse)
    def home(request: Request):
        return templates.TemplateResponse('home.html', {'request': request})

    @app.get('/register', response_class=HTMLResponse)
    def register_student(request: Request):
        return templates.TemplateResponse('register.html', {'request': request})
    
    @app.get("/check-username/{username}", response_model=dict)
    async def check_username(username: str):
        with db_session:
            user = Users.get(username=username)
            if user:
                return {"exists": True}
            else:
                return {"exists": False}

    @app.get('/login', response_class=HTMLResponse)
    def login(request: Request):
        return templates.TemplateResponse('login.html', {'request': request})
    
    @app.post('/register/success')
    async def register(request: Request,
                       username: str = Form(...), 
                       password: str = Form(...), 
                       role: str = Form(...), 
                   firstname: str = Form(...), 
                   lastname: str = Form(...), 
                   email: str = Form(...), 
                   phone: str = Form(...), 
                   address: str = Form(...), 
                   city: str = Form(...), 
                   zip: str = Form(...),
                   country: str = Form(...),
                   region: str = Form(...),
                   gender: str = Form(...), 
                   farm_name: str = Form(None),
                   farm_email: str = Form(None), 
                   farm_phone: str = Form(None), 
                   farm_address: str = Form(None), 
                   farm_city: str = Form(None), 
                   farm_zip: str = Form(None),
                   farm_country: str = Form(None),
                   farm_region: str = Form(None),
                   ):
        with db_session:
            regions = Regions(region_name=region)
            countries = Countries(region_id = regions, country_name=country)
            location = Locations(country_id = countries, address=address, city=city, zip=zip)
            user = Users(username=username, password=password, role=role, firstName=firstname, lastName=lastname,
                        email=email, phone=phone, gender=gender, location_id=location)
            if(role == "FarmOwner"):
                regionsF = Regions(region_name=farm_region)
                countryF = Countries(region_id=regionsF ,country_name=farm_country)
                locationF = Locations(address=farm_address, city=farm_city, zip=farm_zip, country_id=countryF)
                farm = Farms(farm_name=farm_name, farm_address=farm_address, farm_city=farm_city, farm_zip=farm_zip, farm_phone=farm_phone, farm_email=farm_email, farm_location_id=locationF, user_id=user)
                framOwners = FarmOwners(user_id=user, farm_id=farm)
                
            elif(role == "Customer"):
                customer = Customers(user_id=user)
                
            db.commit()

            return templates.TemplateResponse('home.html', {'request': request})
    
    @app.post("/login")
    async def login(user_data: dict):

        return {"message": "Logged in successfully"}
    
    return app

create_app()


