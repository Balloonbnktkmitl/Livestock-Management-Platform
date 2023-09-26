from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from .models import db, Users, Farms, Staffs, Animals, Products, Locations, Countries, Regions, Orders, Animal_Types, Products
from pony.orm import db_session, get, select,  ObjectNotFound
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
from io import BytesIO


def get_product_image_by_code(product: int):
    with db_session:
        product = Products.get(product_code=product)
        return product.product_image

@db_session
def get_all_products():
    products = Products.select()[:]
    return products
    
def get_or_create_region(region_name):
    with db_session:
        existing_region = Regions.get(region_name=region_name)
        if existing_region is None:
            existing_region = Regions(region_name=region_name)
            db.commit()
    region_id = existing_region.region_id
    return region_id

def get_or_create_country(country_name, region_id):
    with db_session:
        existing_country = Countries.get(country_name=country_name, region_id=region_id)
        if existing_country is None:
            existing_country = Countries(country_name=country_name, region_id=region_id)
            db.commit()    
    country_id = existing_country.country_id
    region_id = existing_country.region_id
    return country_id, region_id

def get_or_create_location(address, city, zip, country_id):
    with db_session:
        existing_location = Locations.get(address=address, city=city, zip=zip, country_id=country_id)
        if existing_location is None:
            existing_location = Locations(address=address, city=city, zip=zip, country_id=country_id)
            db.commit()
    location_id = existing_location.location_id
    country_id = existing_location.country_id
    return location_id, country_id

# login
# อัพเดทคำสั่งสร้างฟังก์ชันตรวจสอบรหัสผ่าน
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
        return pwd_context.hash(password)
    
@db_session    
def get_user_info(access_token: str):
    try:
        # ทำการตรวจสอบความถูกต้องของ Access Token
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        # ในกรณีนี้คุณสามารถใช้ข้อมูลจาก payload เพื่อดึงข้อมูลผู้ใช้งานจากฐานข้อมูล
        # สมมติว่าคุณมีโมเดล User ในการเก็บข้อมูลผู้ใช้
        user = Users.get(username=payload.get("sub"))  # สมมติว่า "sub" เก็บ username ใน Token
        user_ID = user.user_ID
        if user.role == "FarmOwner":
            farm = get_farm_info(user_ID)
        if user:
            location_info = user.location_id
            countries_info = location_info.country_id
            region_info = countries_info.region_id
            user_info = user.to_dict()
            user_info["location"] = location_info
            user_info["country"] = countries_info
            user_info["region"] = region_info
            if user.role == "FarmOwner":
                user_info["farm"] = farm
            return user_info
        else:
            return None
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def get_farm_info(user_ID : int):
    try:
        farm = Farms.get(user_id=user_ID)
        farm_ID = farm.farm_id
        if farm:
            location_info = farm.location_id
            countries_info = location_info.country_id
            region_info = countries_info.region_id
            # animal_info = select(animal for animal in Animals if animal.farm_id == farm_ID)[:]
            # animal_type = animal_info.animal_type_id
            farm_info = farm.to_dict()
            farm_info["location"] = location_info
            farm_info["country"] = countries_info
            farm_info["region"] = region_info
            return farm_info
        else:
            return None
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
       
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_app():
    app = FastAPI()
    
    app.mount("/frontend", StaticFiles(directory="..\\frontend"), name="frontend")
    frontend = Jinja2Templates(directory="..\\frontend\\src")

    @app.get('/', response_class=HTMLResponse)
    def home(request: Request):
        return frontend.TemplateResponse('login.html', {'request': request})
    
    # เพิ่มเส้นทางสำหรับล็อกอิน
    @app.post("/", response_class=HTMLResponse)
    async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends() ,username: str = Form(...),
    password: str = Form(...),):
        with db_session:
            user = Users.get(username=form_data.username)
            if not user or not verify_password(form_data.password, user.password):
                raise HTTPException(status_code=400, detail="Incorrect username or password")

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.username, "role": user.role},
                expires_delta=access_token_expires
            )
            
            encoded_jwt = jwt.encode({"sub": user.username, "role": user.role}, SECRET_KEY, algorithm=ALGORITHM)
            
            response = RedirectResponse(url="/home")
            response.set_cookie(key="access_token", value=access_token, httponly=True)
            response.set_cookie(key="user_role", value=user.role, httponly=True)
            response.set_cookie(key="jwt_token", value=encoded_jwt, httponly=True)
            return response
        
    @app.get('/check-uesrnameorpassword/{username,password}', response_class=HTMLResponse)
    async def check_uesrnameorpassword(request: Request, username: str = Form(...), password: str = Form(...)):
        with db_session:
            user = Users.get(username=username)
            if not user or not verify_password(password, user.password):
                return {"exists": True}
            else:
                return {"exists": False}
    
    @app.get("/check-username/{username}", response_model=dict)
    async def check_username(username: str):
        with db_session:
            user = Users.get(username=username)
            if user:
                return {"exists": True}
            else:
                return {"exists": False}
            
    @app.get('/register', response_class=HTMLResponse)
    def register_users(request: Request):
        return frontend.TemplateResponse('register.html', {'request': request})
    
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
            # ตรวจสอบว่ามี Region อยู่แล้วหรือไม่
            region = get_or_create_region(region)

            country, region = get_or_create_country(country.capitalize(), region)

            location, country = get_or_create_location(address, city.capitalize(), zip, country)
            
            hashed_password = get_password_hash(password)
            
            user = Users(username=username, password=hashed_password, role=role, firstName=firstname, lastName=lastname,
             email=email, phone=phone, gender=gender, location_id=location)
            
            if(role == "FarmOwner"):
                farm_region = get_or_create_region(farm_region)
                farm_country, farm_region = get_or_create_country(farm_country.capitalize(), farm_region)
                farm_location, farm_country = get_or_create_location(farm_address, farm_city.capitalize(), farm_zip, farm_country)
                
                farm = Farms(farm_name=farm_name, farm_phone=farm_phone, farm_email=farm_email, location_id=farm_location, user_id=user)
                
            db.commit()

            raise HTTPException(status_code=303, detail="See Other", headers={"Location": "/"})
    
    @app.post("/home", response_class=HTMLResponse)
    @db_session
    def post_dashboard(request: Request):
        jwt_token = request.cookies.get("jwt_token")
        access_token = request.cookies.get("access_token")
        try:
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role", "Unknown")
        except jwt.ExpiredSignatureError:
            # Handle token expiration
            role = "Expired"

        user_info = get_user_info(access_token)
        products = get_all_products()
        if role == "FarmOwner":
            return frontend.TemplateResponse('home_farmowner.html', {'request': request, "user_info": user_info, 'products': products})
        elif role == "Customer":
            return frontend.TemplateResponse('Home_customer.html', {'request': request})
        else:
            raise HTTPException(status_code=403, detail="Access Forbidden")
        
    @app.get("/home", response_class=HTMLResponse)
    @db_session
    def get_dashboard(request: Request):
        jwt_token = request.cookies.get("jwt_token")
        access_token = request.cookies.get("access_token")
        try:
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role", "Unknown")
        except jwt.ExpiredSignatureError:
            # Handle token expiration
            role = "Expired"
            
        products = get_all_products()
        user_info = get_user_info(access_token)
        if role == "FarmOwner":
            return frontend.TemplateResponse('home_farmowner.html', {'request': request, "user_info": user_info, 'products': products})
        elif role == "Customer":
            return frontend.TemplateResponse('Home_customer.html', {'request': request})
        else:
            raise HTTPException(status_code=403, detail="Access Forbidden")    
    
    @app.get("/user-profile", response_class=HTMLResponse)
    async def user_profile(request: Request):
        # ตรวจสอบค่า request เพื่อให้แน่ใจว่ามีคุกกี้และค่า "access_token" อยู่
        if "access_token" in request.cookies:
            access_token = request.cookies.get("access_token")
            user_info = get_user_info(access_token)
            if not user_info:
                raise HTTPException(status_code=401, detail="User not authenticated")
        else:
            raise HTTPException(status_code=401, detail="User not authenticated")

        return frontend.TemplateResponse("user_profile.html", {"request": request, "user_info": user_info})
    
    @app.get("/get-product-image/{product_id}", response_class=StreamingResponse)
    async def get_product_image(product_id: int):
        # ดึงข้อมูลรูปภาพจากฐานข้อมูล (ในกรณีของคุณ)
        product_image = get_product_image_by_code(product_id)
        if product_image is None:
            raise HTTPException(status_code=404, detail="Product image not found")
        
        # สร้าง FileResponse จากข้อมูลรูปภาพและระบุ media_type ถูกต้อง
        return StreamingResponse(BytesIO(product_image), media_type="image/jpeg")
    
    @app.get("/logout")
    async def logout(response: Response):
        # ลบคุกกี้ Access Token
        response.delete_cookie("access_token")

        # รีเดอิเร็กต์ผู้ใช้ไปยังหน้าล็อกอินหลังจากล็อกเอ้า
        return RedirectResponse(url="/")
    
    return app
    
create_app()


