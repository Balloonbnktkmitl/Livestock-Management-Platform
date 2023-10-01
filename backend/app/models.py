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
    farms = Optional("Farms", cascade_delete=True)
    Orders = Set('Orders')
    
class Farms(db.Entity):
    farm_id = PrimaryKey(int, auto=True)
    user_id = Optional(Users)
    farm_name = Optional(str, nullable=True)
    farm_phone = Optional(str, nullable=True)
    farm_email = Optional(str, nullable=True)
    location_id = Optional(Locations, nullable=True)
    animals = Set('Animals')
    products = Set('Products')
    staffs = Set('Staffs')
    Orders = Set('Orders')

class Animals(db.Entity):
    animal_code = PrimaryKey(int, auto=True)
    farm_id = Required(Farms)
    type_id = Required("Animal_Types")
    animal_detail = Required(str)
    animal_image = Required(bytes)
    products = Set("Products", reverse="animal_code")

       
class Products(db.Entity):
    product_code = PrimaryKey(int, auto=True)
    product_name = Required(str)
    farm_id = Required(Farms)
    product_price = Required(float)
    product_detail = Required(str)
    product_status = Required(str)
    animal_code = Optional("Animals", reverse="products")
    quantity = Required(int)
    product_image = Required(bytes)
    Orders = Set('Orders')
   
class Animal_Types(db.Entity):
    type_id = PrimaryKey(int, auto=True)
    type_name = Required(str)
    animals = Set('Animals')

class Jobs(db.Entity):
    job_id = PrimaryKey(int, auto=True)
    job_title = Required(str)
    job_detail = Required(str)
    min_salary = Required(float)
    max_salary = Required(float)
    staffs = Set('Staffs')

class Staffs(db.Entity):
    staff_id = PrimaryKey(int, auto=True)
    job_id = Required(Jobs)
    firstName = Required(str)
    lastName = Required(str)
    farm_id = Required(Farms)
    status = Required(str)
    hire_date = Required(datetime)
    salary = Required(float)
    staff_email = Required(str)
    staff_phone = Required(str)
    staff_gender = Required(str)
    
class Orders(db.Entity):
    order_id = PrimaryKey(int, auto=True)
    product_code = Required(Products)
    farm_id = Required(Farms)
    user_id = Required(Users)
    order_date = Required(datetime)
    order_status = Required(str)
    order_quantity = Required(int)
    
db.bind(provider='mysql', host='161.246.127.24', user='dbproject', password='db', db='db', port=9031)
db.generate_mapping(check_tables=True, create_tables=True)  
sql_debug(True)
