from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash   

db = SQLAlchemy()

class Admin(UserMixin, db.Model):

    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(25), unique=True, nullable=False)
    password_hashed = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='admin')

    def create_pass(self, password):
        self.password_hashed = generate_password_hash(password)

    def verify_pass(self, password):
        return check_password_hash(self.password_hashed, password)

    def get_id(self):
        return super().get_id()
    
    def __repr__(self):
        return f'<Admin {self.login}>'
    

class Department(db.Model):

    __tablename__ = 'department'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(5), unique = True, nullable = False )

    employee = db.relationship('Employee', backref='department', lazy=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'
    
    
class Position(db.Model):

    __tablename__ = 'position'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20),nullable = False )

    employee = db.relationship('Employee', backref = 'position', lazy = True )

    def __repr__(self):
        return f'<Position {self.name}>'
    
    
class Type(db.Model):

    __tablename__ = 'type'

    id = db.Column(db.Integer, primary_key = True)
    value = db.Column(db.String(10), nullable = False)

    checkpoints = db.relationship('Checkpoints', backref = 'type', lazy = True)

    def __repr__(self):
        return f'<Type {self.value}>'
    

class Employee(UserMixin, db.Model):

    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False, unique = True)
    email = db.Column(db.String(20), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    sex = db.Column(db.String(1), nullable = False)

    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable = False)
    position_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable = False )

    checkpoints = db.relationship('Checkpoints', backref='employee', cascade="all, delete-orphan", lazy=True)
    
    def create_pass(self, password):
        self.password = generate_password_hash(password)

    def verify_pass(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return super().get_id()
    
    def __repr__(self):
        return f'<Employee {self.name}>'
    

class Checkpoints(db.Model):

    __tablename__ = 'checkpoints'

    id = db.Column(db.Integer, primary_key = True)
    moment = db.Column(db.DateTime, nullable=False, default=datetime.now)

    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable = False)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)

    def __repr__(self):
        return f'<Checkpoints {self.moment}>'

admin_employee = db.Table(
    'admin_employee',
    db.Column('admin_id', db.Integer, db.ForeignKey('admin.id'), primary_key=True),
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id'), primary_key=True)
)