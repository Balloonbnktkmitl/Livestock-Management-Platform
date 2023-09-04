from pony.orm import Database, Required, PrimaryKey

db = Database()

class Student(db.Entity):
    StudentID = PrimaryKey(int, auto=True)
    Sname = Required(str)
    Slastname = Required(str)
    Snickname = Required(str)
    Semail = Required(str)
    Spassword = Required(str)
    SnationNumber = Required(str)
    Sphone = Required(str)
    Saddress = Required(str)
    Scity = Required(str)
    Szip = Required(str)
    Sstatus = Required(str)
    
class Teacher(db.Entity):
    TeacherID = PrimaryKey(int, auto=True)
    Tname = Required(str)
    Tlastname = Required(str)
    Temail = Required(str)
    Tpassword = Required(str)
    TnationNumber = Required(str)
    Tphone = Required(str)
    Taddress = Required(str)
    Tcity = Required(str)
    Tzip = Required(str)
    Tstatus = Required(str)
    
class Subject(db.Entity):
    SubjectID = PrimaryKey(int, auto=True)
    SubjectName = Required(str)
    SubjectDescription = Required(str)
    SubjectCredit = Required(str)
    SubjectCode = Required(str)
    
class Grade(db.Entity):
    GradeID = PrimaryKey(int, auto=True)
    SubjectID = Required(int)
    StudentID = Required(int)
    TeacherID = Required(int)
    Grade = Required(str)
    
    
    
    
