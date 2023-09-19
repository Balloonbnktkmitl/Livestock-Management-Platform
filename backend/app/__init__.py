from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from .models import db, Database, Users, Farms, Customers, FarmOwners, Staffs, Animals, Products, Locations, Countries, Regions
from pony.orm import db_session
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

def create_app():
    app = FastAPI()
    
    app.mount("/frontend", StaticFiles(directory="..\\frontend"), name="frontend")
    templates = Jinja2Templates(directory="..\\templates")
    frontend = Jinja2Templates(directory="..\\frontend\\src")

    @app.get('/', response_class=HTMLResponse)
    def home(request: Request):
        return frontend.TemplateResponse('login.html', {'request': request})

    @app.get('/register', response_class=HTMLResponse)
    def register_student(request: Request):
        return frontend.TemplateResponse('register.html', {'request': request})
    
    @app.get("/check-username/{username}", response_model=dict)
    async def check_username(username: str):
        with db_session:
            user = Users.get(username=username)
            if user:
                return {"exists": True}
            else:
                return {"exists": False}
    
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
            hashed_password = get_password_hash(password)
            
            regions = Regions(region_name=region)
            countries = Countries(region_id = regions, country_name=country)
            location = Locations(country_id = countries, address=address, city=city, zip=zip)
            user = Users(username=username, password=hashed_password, role=role, firstName=firstname, lastName=lastname,
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

            raise HTTPException(status_code=303, detail="See Other", headers={"Location": "/"})
        
    # login
    # อัพเดทคำสั่งสร้างฟังก์ชันตรวจสอบรหัสผ่าน
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password):
        return pwd_context.hash(password)

    SECRET_KEY = "your-secret-key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # สร้างฟังก์ชันเพื่อดึง Access Token จากคุกกี้หรือส่วนข้อมูลของคำขอ
    def get_access_token(authorization: str = Cookie(None), request: Request = Depends()):
        # กำหนดวิธีการดึง Access Token จากคุกกี้หรือส่วนข้อมูลของคำขอที่เหมาะสม
        # ในที่นี้เราจะดึงจากคุกกี้แต่คุณสามารถปรับแต่งตามความต้องการ
        if authorization:
            return authorization
        elif "access_token" in request.cookies:
            return request.cookies["access_token"]
        else:
            return None
    
    # เพิ่มฟังก์ชันเพื่อดึงบทบาทของผู้ใช้จาก Access Token
    def get_current_user_role(request: Request, token: str = Depends(get_access_token)):
        # คุณสามารถใช้ request ในฟังก์ชันนี้เพื่อดึงข้อมูลจากคำขอ HTTP
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("role")  # ดึงบทบาทของผู้ใช้จาก payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

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
            
            response = RedirectResponse(url="/dashboard")
            response.set_cookie(key="access_token", value=access_token, httponly=True)
            response.set_cookie(key="user_role", value=user.role, httponly=True)
            response.set_cookie(key="jwt_token", value=encoded_jwt, httponly=True)
            return response

    @app.get('/dashboard', response_class=HTMLResponse)
    def dashboard(request: Request):
        pass
    
    @app.post("/dashboard", response_class=HTMLResponse)
    def post_dashboard(request: Request):
        jwt_token = request.cookies.get("jwt_token")

        try:
            payload = jwt.decode(jwt_token, SECRET_KEY, algorithms=[ALGORITHM])
            role = payload.get("role", "Unknown")
        except jwt.ExpiredSignatureError:
            # Handle token expiration
            role = "Expired"
        
        if role == "FarmOwner":
            return frontend.TemplateResponse('farm_owner_dashboard.html', {'request': request})
        elif role == "Customer":
            return frontend.TemplateResponse('customer_dashboard.html', {'request': request})
        else:
            raise HTTPException(status_code=403, detail="Access Forbidden")
    
    return app
    
create_app()


