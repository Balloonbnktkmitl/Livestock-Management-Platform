from pony.orm import Database, Required, PrimaryKey, Set, Optional, sql_debug 
from datetime import datetime
from enum import Enum

db = Database()
    
class Regions(db.Entity):
    region_id = PrimaryKey(int, auto=True)
    region_name = Required(str)
    countries = Set('Countries')
    
class Countries(db.Entity):
    country_id = PrimaryKey(int, auto=True)
    country_name = Required(str)
    region_id = Required(Regions)
    locations = Set('Locations', nullable=True)

class Locations(db.Entity):
    location_id = PrimaryKey(int, auto=True)
    address = Required(str)
    city = Required(str)
    zip = Required(int)
    country_id = Required(Countries)
    users = Set('Users', nullable=True)
    farms = Set('Farms', nullable=True)
    
class Users(db.Entity):
    user_ID = PrimaryKey(int, auto=True)
    username = Required(str)
    password = Required(str)
    firstName = Required(str)
    lastName = Required(str)
    gender = Required(str)
    phone = Required(str)
    email = Required(str)
    role = Required(str)
    location_id = Required(Locations)
    customers = Optional('Customers')
    farmOwners = Optional('FarmOwners')
    farms = Optional("Farms")
    
class Farms(db.Entity):
    farm_id = PrimaryKey(int, auto=True)
    user_id = Optional(Users)
    farm_name = Optional(str, nullable=True)
    farm_address = Optional(str, nullable=True)
    farm_city = Optional(str, nullable=True)
    farm_zip = Optional(int, nullable=True)
    farm_phone = Optional(str, nullable=True)
    farm_email = Optional(str, nullable=True)
    farm_location_id = Optional(Locations, nullable=True)
    farmOwners = Set('FarmOwners')
    animals = Set('Animals')
    products = Set('Products')
    staffs = Set('Staffs')
    

class Customers(db.Entity):
    customers_id = PrimaryKey(int, auto=True)
    user_id = Required(Users)
    

class FarmOwners(db.Entity):
    farmOwners_id = PrimaryKey(int, auto=True)
    user_id = Required(Users)
    farm_id = Required(Farms)

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
    
db.bind(provider='mysql', host='161.246.127.24', user='dbproject', password='db', db='db', port=9031)
db.generate_mapping(check_tables=True, create_tables=True)  
sql_debug(True)
