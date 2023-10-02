from fastapi import FastAPI, Request, Form, Depends, HTTPException, Cookie, Response, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from .models import db, Users, Farms, Staffs, Animals, Products, Locations, Countries, Regions, Orders, Animal_Types, Products, Jobs
from pony.orm import db_session, get, select,  ObjectNotFound
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
from io import BytesIO

def get_all_jobs():
    with db_session:
        jobs = select(job for job in Jobs)[:]
        return jobs

def get_all_staffs():
    with db_session:
        staffs = select(staff for staff in Staffs)[:]
        return staffs
    
def get_all_farms():
    with db_session:
        farms = select(farm for farm in Farms)[:]
        return farms
    
def get_product_image_by_code(product: int):
    with db_session:
        product = Products.get(product_code=product)
        return product.product_image
    
def get_animals_image_by_code(animal: int):
    with db_session:
        animal = Animals.get(animal_code=animal)
        return animal.animal_image

def get_all_animals():
    with db_session:
        animals = select(animal for animal in Animals)[:]
        return animals

@db_session
def get_all_products():
    products = Products.select()[:]
    return products

@db_session
def get_all_orders():
    orders = Orders.select()[:]
    return orders
    
def get_or_create_type(type_name):
    with db_session:
        existing_type = Animal_Types.get(type_name=type_name)
        if existing_type is None:
            existing_type = Animal_Types(type_name=type_name)
            db.commit()
    return existing_type.type_id
            
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
            regions_info = countries_info.region_id
            user_info = user.to_dict()
            user_info["region"] = regions_info
            user_info["location"] = location_info
            user_info["country"] = countries_info
            if user.role == "FarmOwner":
                user_info["farm"] = farm
            return user_info
        else:
            return None
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
@db_session  
def get_farm_info(user_ID : int):
    try:
        farm = Farms.get(user_id=user_ID)
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
        expire = datetime.utcnow() + timedelta(days=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_app():
    app = FastAPI()
    
    app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")
    frontend = Jinja2Templates(directory="../frontend/src")

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
            return frontend.TemplateResponse('home_customer.html', {'request': request, "user_info": user_info, 'products': products})
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
            
        user_info = get_user_info(access_token)
        products = get_all_products()
        if role == "FarmOwner":
            return frontend.TemplateResponse('home_farmowner.html', {'request': request, "user_info": user_info, 'products': products})
        elif role == "Customer":
            return frontend.TemplateResponse('Home_customer.html', {'request': request})
        else:
            raise HTTPException(status_code=403, detail="Access Forbidden")    
    
    @app.get("/user-profile", response_class=HTMLResponse)
    @db_session
    def user_profile(request: Request):
        # ตรวจสอบค่า request เพื่อให้แน่ใจว่ามีคุกกี้และค่า "access_token" อยู่
        if "access_token" in request.cookies:
            access_token = request.cookies.get("access_token")
            user_info = get_user_info(access_token)
            products = get_all_products()
            orders = get_all_orders()
            if not user_info:
                raise HTTPException(status_code=401, detail="User not authenticated")
        else:
            raise HTTPException(status_code=401, detail="User not authenticated")

        return frontend.TemplateResponse("profile_edit.html", {"request": request, "user_info": user_info, 'products': products, 'orders': orders})
    
    @app.get("/get-product-image/{product_id}", response_class=StreamingResponse)
    async def get_product_image(product_id: int):
        # ดึงข้อมูลรูปภาพจากฐานข้อมูล (ในกรณีของคุณ)
        product_image = get_product_image_by_code(product_id)
        if product_image is None:
            raise HTTPException(status_code=404, detail="Product image not found")
        
        # สร้าง FileResponse จากข้อมูลรูปภาพและระบุ media_type ถูกต้อง
        return StreamingResponse(BytesIO(product_image), media_type="image/jpeg")
    
    @app.get("/get-animals-image/{animal_code}", response_class=StreamingResponse)
    async def get_animals_image(animal_code: int):
        animals_image = get_animals_image_by_code(animal_code)
        if animals_image is None:
            raise HTTPException(status_code=404, detail="Animals image not found")
        return StreamingResponse(BytesIO(animals_image), media_type="image/jpeg")
    
    
    @app.post("/update_data", response_model=dict)
    async def update_data(request: Request, fromData: dict):
        with db_session:
            user = Users.get(user_ID=fromData["user_id"])
            region = get_or_create_region(fromData["region"])
            country,temp = get_or_create_country(fromData["country"], region)
            location,temp = get_or_create_location(fromData["address"], fromData["city"], fromData["zip"], country)
            if not user:
                raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
            user.firstName = fromData["firstname"]
            user.lastName = fromData["lastname"]
            user.email = fromData["email"]
            user.phone = fromData["phone"]
            user.gender = fromData["gender"]
            user.location_id = location
            user.location_id.country_id = country
            db.commit()
            return {"message": "อัปเดตข้อมูลผู้ใช้สำเร็จ"}
        
    @app.post("/update_password", response_model=dict)
    async def update_password(request: Request, fromData: dict):
        with db_session:
            user = Users.get(user_ID=fromData["user_id"])
            if not user:
                raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
            
            if not verify_password(fromData["oldPassword"], user.password):
                raise HTTPException(status_code=400, detail="รหัสผ่านเดิมไม่ถูกต้อง")
            
            user.password = get_password_hash(fromData["newPassword"])
            
            db.commit()
            
            return {"message": "อัปเดตรหัสผ่านสำเร็จ"}
        
    @app.get('/delete-user/{user_id}', response_model=dict)
    async def delete(user_id: int, response: Response):
        with db_session:
            print(user_id)
            user = Users.get(user_ID=user_id)
            if not user:
                raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
            user.delete()
            db.commit()
            response.delete_cookie("access_token")
            return RedirectResponse(url="/")
            
    @app.get("/logout")
    async def logout(response: Response):
        # ลบคุกกี้ Access Token
        response.delete_cookie("access_token")

        # รีเดอิเร็กต์ผู้ใช้ไปยังหน้าล็อกอินหลังจากล็อกเอ้า
        return RedirectResponse(url="/")
    
    @app.get("/product", response_class=HTMLResponse)
    def product(request: Request):
        with db_session:
            if "access_token" in request.cookies:
                access_token = request.cookies.get("access_token")
                user_info = get_user_info(access_token)
                products = get_all_products()
                animal = get_all_animals()
                if not user_info:
                    raise HTTPException(status_code=401, detail="User not authenticated")
            else:
                raise HTTPException(status_code=401, detail="User not authenticated")
            return frontend.TemplateResponse('product.html', {'request': request, 'products': products, "user_info": user_info})
    
    @app.get("/managefarm", response_class=HTMLResponse)
    def managefarm(request: Request):
        with db_session:
            if "access_token" in request.cookies:
                access_token = request.cookies.get("access_token")
                user_info = get_user_info(access_token)
                products = get_all_products()
                animal = get_all_animals()
                farm = get_all_farms()
                staff = get_all_staffs()
                job = get_all_jobs()
                order = get_all_orders()
                typeanimal = select(type for type in Animal_Types)[:]
                if not user_info:
                    raise HTTPException(status_code=401, detail="User not authenticated")
            else:
                raise HTTPException(status_code=401, detail="User not authenticated")
            return frontend.TemplateResponse('managefarm.html', {'request': request, 'products': products, "user_info": user_info, "farm": farm, 
                                                                 "animal": animal, "staff": staff, "job": job, "typeanimal": typeanimal, "order": order})
    
    @app.post("/managefarm", response_class=HTMLResponse)
    def managefarm(request: Request):
        with db_session:
            if "access_token" in request.cookies:
                access_token = request.cookies.get("access_token")
                user_info = get_user_info(access_token)
                products = get_all_products()
                animal = get_all_animals()
                farm = get_all_farms()
                staff = get_all_staffs()
                job = get_all_jobs()
                order = get_all_orders() 
                typeanimal = select(type for type in Animal_Types)[:]
                if not user_info:
                    raise HTTPException(status_code=401, detail="User not authenticated")
            else:
                raise HTTPException(status_code=401, detail="User not authenticated")
            return frontend.TemplateResponse('managefarm.html', {'request': request, 'products': products, "user_info": user_info, 
                                                                 "farm": farm, "animal": animal, "staff": staff, "job": job, "typeanimal": typeanimal, "order": order})
        
    @app.post("/updatefarm", response_model=dict)
    async def updatefarm(request: Request, fromData: dict):
        with db_session:
            farm = Farms.get(farm_id=fromData["farm_id"])
            region = get_or_create_region(fromData["region"])
            country,temp = get_or_create_country(fromData["country"], region)
            location,temp = get_or_create_location(fromData["address"], fromData["city"], fromData["zip"], country)
            if not farm:
                raise HTTPException(status_code=404, detail="ไม่พบผู้ใช้")
            
            farm.farm_name = fromData["farm_name"]
            farm.farm_email = fromData["email"]
            farm.farm_phone = fromData["phone"]
            farm.location_id = location
            farm.location_id.country_id = country
            db.commit()
            
            return {"message": "อัปเดตข้อมูลผู้ใช้สำเร็จ"}
    
    @app.post("/addproduct")
    async def addproduct(request: Request, product_image: UploadFile = File(...),
                         product_name: str = Form(...), 
                       product_price: float = Form(...), 
                       product_detail: str = Form(...), 
                       product_quantity: int = Form(...),
                       farm_id: int = Form(...)):
        with db_session:
            try:
                image_data = product_image.file.read()
                product = Products(product_name=product_name, farm_id=farm_id, product_price=product_price, 
                                   product_detail=product_detail, product_status="Available", product_image=image_data
                                   ,quantity=product_quantity)
                db.commit()
                return RedirectResponse(url="/managefarm")
            except Exception as e:
                print(str(e))
                return {"message": "เพิ่มสินค้าไม่สำเร็จ"}
            
    @app.post("/updateproduct")
    async def updateproduct(request: Request, image: UploadFile = File(...),
                         name: str = Form(...), 
                       price: float = Form(...), 
                       detail: str = Form(...), 
                       quantity: int = Form(...),
                       status: str = Form(...),
                       product_code: int = Form(...)):
        with db_session:
            image_data = image.file.read()
            product = Products.get(product_code=product_code)
            if not product:
                raise HTTPException(status_code=404, detail="ไม่พบสินค้า")
            product.product_name = name
            product.product_price = price
            product.product_detail = detail
            product.quantity = quantity
            product.product_image = image_data
            product.product_status = status
            db.commit()
            return RedirectResponse(url="/managefarm")
    
    @app.post("/deleteproduct/{product_id}", response_model=dict)
    async def deleteproduct(product_id: int, response: Response):
        with db_session:
            product = Products.get(product_code=product_id)
            if not product:
                raise HTTPException(status_code=404, detail="ไม่พบสินค้า")
            product.delete()
            db.commit()
            return RedirectResponse(url="/managefarm")
        
    @app.get("/farm", response_class=HTMLResponse)
    def farm(request: Request):
        with db_session:
            farm = get_all_farms()
            return frontend.TemplateResponse('farm.html', {'request': request, "farm": farm})
    
    @app.get("/farmprofile/{farm_id}", response_class=HTMLResponse)
    async def farmprofile(request: Request, farm_id: int):
        with db_session:
            farm = Farms.get(farm_id=farm_id)
            if not farm:
                raise HTTPException(status_code=404, detail="ไม่พบฟาร์ม")
            location = farm.location_id
            country = location.country_id
            region = country.region_id
            user = farm.user_id
            product = get_all_products()
            
            return frontend.TemplateResponse('farm_profile.html', {'request': request, "farm": farm, 
            "location": location, "country": country, "region": region, "user": user, "product": product})
    
    @app.post("/farmprofile/{farm_id}", response_class=HTMLResponse)
    async def farmprofile(request: Request, farm_id: int):
        with db_session:
            farm = Farms.get(farm_id=farm_id)
            if not farm:
                raise HTTPException(status_code=404, detail="ไม่พบฟาร์ม")
            location = farm.location_id
            country = location.country_id
            region = country.region_id
            user = farm.user_id
            product = get_all_products()
            
            return frontend.TemplateResponse('farm_profile.html', {'request': request, "farm": farm, 
            "location": location, "country": country, "region": region, "user": user, "product": product})
    
    @app.post("/addjob")
    async def addjob(request: Request, name: str = Form(...), des: str = Form(...), min: float = Form(...), max: float = Form(...)):
        with db_session:
            job = Jobs(job_title=name, job_detail=des, min_salary=min, max_salary=max)
            db.commit()
            return RedirectResponse(url="/managefarm")
        
    @app.post("/updatejob")
    async def updatejob(request: Request, nameedit: str = Form(...), desedit: str = Form(...), minedit: float = Form(...)
                        , maxedit: float = Form(...), job_id: int = Form(...)):
        job = Jobs.get(job_id=job_id)
        if not job:
            raise HTTPException(status_code=404, detail="ไม่พบงาน")
        job.job_title = nameedit
        job.job_detail = desedit
        job.min_salary = minedit
        job.max_salary = maxedit
        db.commit()
        return RedirectResponse(url="/managefarm")
    
    @app.post("/addstaff")
    async def addstaff(request: Request, first: str = Form(...), last: str = Form(...), job: int = Form(...),
                       email: str = Form(...), phone: str = Form(...), farm_id: int = Form(...), gender: str = Form(...), salary: float = Form(...),
                       hiredate: str = Form(...)):
        with db_session:
            staff = Staffs(firstName=first, lastName=last, job_id=job, staff_email=email, staff_phone=phone, staff_gender=gender, farm_id=farm_id, 
                           salary=salary, status="Active", hire_date=hiredate)
            db.commit()
            return RedirectResponse(url="/managefarm")          
    
    @app.post("/updatestaff")
    async def updatestaff(request: Request, first: str = Form(...), last: str = Form(...), phone: str = Form(...),
                          mail: str = Form(...), editjobstaff: str= Form(...), gender: str = Form(...), sala: float = Form(...),
                          status: str = Form(...), staff_id: int = Form(...)):
        with db_session:
            staff = Staffs.get(staff_id=staff_id)
            if not staff:
                raise HTTPException(status_code=404, detail="ไม่พบพนักงาน")
            staff.firstName = first
            staff.lastName = last
            staff.staff_phone = phone
            staff.staff_email = mail
            staff.job_id = editjobstaff
            staff.status = status
            staff.salary = sala
            staff.staff_gender = gender
            db.commit()
            return RedirectResponse(url="/managefarm")
            
    @app.post("/addanimals")
    async def addanimals(request: Request, codeanimal: int = Form(...), typeanimal: str = Form(...), farm_id: int = Form(...),
                         imageanimal: UploadFile=File (...), detailanimal: str = Form(...)):
        with db_session:
            try:
                image_data = imageanimal.file.read()
                type_id = get_or_create_type(typeanimal)
                animal = Animals(animal_code=codeanimal, type_id=type_id, farm_id=farm_id, animal_image=image_data, animal_detail=detailanimal)
                db.commit()
                return RedirectResponse(url="/managefarm")
            except Exception as e:
                print(str(e))
                return {"message": "เพิ่มสินค้าไม่สำเร็จ"}
    
    @app.post("/updateanimal")
    async def updateanimals(request: Request, codeanimal: int = Form(...), typeanimal: str = Form(...),
                         imageanimal: UploadFile=File (...), detailanimal: str = Form(...)):
        with db_session:
            image_data = imageanimal.file.read()
            animal = Animals.get(animal_code=codeanimal)
            if not animal:
                raise HTTPException(status_code=404, detail="ไม่พบสัตว์")
            animal.animal_code = codeanimal
            animal.animal_detail = detailanimal
            animal.animal_image = image_data
            animal.type_id = typeanimal
            db.commit()
            return RedirectResponse(url="/managefarm")
        
    @app.post("/deleteanimal/{animal_id}", response_model=dict)
    async def deleteanimal(animal_id: int, response: Response):
        with db_session:
            animal = Animals.get(animal_code=animal_id)
            if not animal:
                raise HTTPException(status_code=404, detail="ไม่พบสัตว์")
            animal.delete()
            db.commit()
            return RedirectResponse(url="/managefarm")
        
    @app.post("/updateorder")
    async def updateorder(request: Request, showorderid: int = Form(...), status: str = Form(...)):
        with db_session:
            order = Orders.get(order_id=showorderid)
            if not order:
                raise HTTPException(status_code=404, detail="ไม่พบสัตว์")
            order.order_status = status
            db.commit()
            return RedirectResponse(url="/managefarm")
    
    @app.post("/addorder", response_model=dict)
    async def addorder(request: Request, formData: dict):
        user_id = formData["usersids"]
        product_id = formData["productcode"]
        quantity = formData["quantity"]
        pdname = formData["product_name"]
        farm_id = formData["farmids"]
        with db_session:
            product = Products.get(product_code=product_id)
            if int(product.quantity) < int(quantity):
                return {"message": "สินค้าไม่เพียงพอ",  "available_quantity": product.quantity}
            order = Orders(user_id=user_id, product_code=product_id, order_status="Pending", farm_id=farm_id, order_quantity=quantity
                           ,order_date=datetime.now())
            product.quantity = int(product.quantity) - int(quantity)
            if int(product.quantity) == 0:
                product.product_status = "soldout"
            db.commit()
            return {"message": "เพิ่มสินค้าสำเร็จ"}
    
    return app

create_app()


