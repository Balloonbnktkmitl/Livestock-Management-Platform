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

    @app.get('/login', response_class=HTMLResponse)
    def login(request: Request):
        return templates.TemplateResponse('login.html', {'request': request})
    
    @app.post('/register/success')
    async def register(username: str = Form(...), 
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
                   farmname: str = Form(...),
                   Femail: str = Form(...), 
                   Fphone: str = Form(...), 
                   Faddress: str = Form(...), 
                   Fcity: str = Form(...), 
                   Fzip: str = Form(...),
                   Fcountry: str = Form(...),
                   Fregion: str = Form(...)):
        with db_session:
            regions = Regions(region_name=region)
            countries = Countries(region_id = regions, country_name=country)
            location = Locations(country_id = countries, address=address, city=city, zip=zip)
            user = Users(username=username, password=password, role=role, firstName=firstname, lastName=lastname,
                        email=email, phone=phone, gender=gender, location_id=location)
            if(role == "FarmOwner"):
                regionsF = Regions(region_name=Fregion)
                countryF = Countries(region_id=regionsF ,country_name=Fcountry)
                locationF = Locations(address=Faddress, city=Fcity, zip=Fzip, country_id=countryF)
                farm = Farms(farm_name=farmname, farm_address=Faddress, farm_city=Fcity, farm_zip=Fzip, farm_phone=Fphone, farm_email=Femail, farm_location_id=locationF, user_id=user)
                framOwners = FarmOwners(user_id=user, farm_id=farm)
                
            elif(role == "Customer"):
                customer = Customers(user_id=user)
                
            db.commit()

            return {"message": "Registration successful"}
    
    @app.post("/login")
    async def login(user_data: dict):

        return {"message": "Logged in successfully"}
    
    return app

create_app()


