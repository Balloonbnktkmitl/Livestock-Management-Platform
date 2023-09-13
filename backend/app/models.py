from pony.orm import Database, Required, PrimaryKey, Set, Optional, sql_debug    
from datetime import datetime

db = Database()

class Regions(db.Entity):
    region_id = PrimaryKey(int, auto=True)
    region_name = Required(str)
    countries = Set('Countries')
    
class Countries(db.Entity):
    country_id = PrimaryKey(int, auto=True)
    country_name = Required(str)
    region_id = Required(Regions)
    locations = Set('Locations')

class Locations(db.Entity):
    location_id = PrimaryKey(int, auto=True)
    address = Required(str)
    city = Required(str)
    zip = Required(int)
    country_id = Required(Countries)
    users = Set('Users')
    farms = Set('Farms')
    
class Farms(db.Entity):
    farm_id = PrimaryKey(int, auto=True)
    FarmOwners_id = Required('FarmOwners', reverse='farms')
    farm_name = Required(str)
    farm_address = Required(str)
    farm_city = Required(str)
    farm_zip = Required(int)
    farm_phone = Required(str)
    farm_email = Required(str)
    farm_location_id = Required(Locations)
    farmOwners = Set('FarmOwners')
    animals = Set('Animals')
    products = Set('Products')
    staffs = Set('Staffs')
    
class Users(db.Entity):
    user_ID = PrimaryKey(int, auto=True)
    username = Required(str)
    password = Required(str)
    role = Required(str)
    firstName = Required(str)
    lastName = Required(str)
    DOB = Required(datetime)
    phone = Required(str)
    email = Required(str)
    location_id = Required(Locations)
    customers = Set('Customers')
    farmOwners = Set('FarmOwners')
    
    def __repr__(self):
        return f"Student(StudentID={self.StudentID}, Sname='{self.Sname}', Slastname='{self.Slastname}', Snickname='{self.Snickname}', Semail='{self.Semail}', Spassword='{self.Spassword}', SnationNumber='{self.SnationNumber}', Sphone='{self.Sphone}', Saddress='{self.Saddress}', Scity='{self.Scity}', Szip='{self.Szip}', Sstatus='{self.Sstatus}')"

class Customers(db.Entity):
    customers_id = PrimaryKey(int, auto=True)
    user_id = Required(Users)
    

class FarmOwners(db.Entity):
    farmOwners_id = PrimaryKey(int, auto=True)
    user_id = Required(Users)
    farm_id = Required(Farms)
    farms = Set('Farms')

class Products(db.Entity):
    product_code = PrimaryKey(int, auto=True)
    product_name = Required(str)
    farm_id = Required(Farms)
    product_price = Required(float)
    makefrom = Required(str) #เชื่อมFarmOwners ไหม
    status = Required(str)
    exportations = Set('Exportations')
   
class Exportations(db.Entity):
    export_id = PrimaryKey(int, auto=True)
    product_code = Required(Products)
    export_date = Required(datetime)
    
class Animals(db.Entity):
    animal_code = PrimaryKey(int, auto=True)
    farm_id = Required(Farms)
    animal_type = Required(str)
    #เพิ่มรูปภาพ

class Jobs(db.Entity):
    job_id = PrimaryKey(int, auto=True)
    job_title = Required(str)
    min_salary = Required(float)
    max_salary = Required(float)
    staffs = Set('Staffs', reverse='job_id')

class Staffs(db.Entity):
    staff_id = PrimaryKey(int, auto=True)
    job_id = Required(Jobs, reverse='staffs')
    firstName = Required(str)
    lastName = Required(str)
    farm_id = Required(Farms)
    status = Required(str)
    manager_id = Optional('Staffs', reverse='managed_staffs')
    hire_date = Required(datetime)
    salary = Required(float)
    managed_staffs = Set('Staffs', reverse='manager_id')
    
db.bind(provider='mysql', host='161.246.127.24', user='dbproject', passwd='db', db='db', port=9031)
db.generate_mapping(check_tables=True, create_tables=True)  
sql_debug(True)
