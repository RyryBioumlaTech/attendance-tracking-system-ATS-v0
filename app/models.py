from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# -----------------------------
# USER MODEL (Admin + Employee)
# -----------------------------

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="employee")

    sex = db.Column(db.String(6))

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id"),
        nullable=True
    )

    position_id = db.Column(
        db.Integer,
        db.ForeignKey("position.id"),
        nullable=True
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    checkpoints = db.relationship(
        "Checkpoint",
        backref="employee",
        cascade="all, delete-orphan",
        lazy=True
    )

    # ---------- password methods ----------

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_pass(self, password):
        return check_password_hash(self.password_hash, password)

    # ---------- role helpers ----------

    def is_admin(self):
        return self.role == "admin"
    
    def is_super_admin(self):
        return self.role == "superAd"

    def is_employee(self):
        return self.role == "employee"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


# -----------------------------
# DEPARTMENT
# -----------------------------

class Department(db.Model):

    __tablename__ = "department"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True, nullable=False)

    employees = db.relationship(
        "User",
        backref="department",
        lazy=True
    )

    def __repr__(self):
        return f"<Department {self.name}>"


# -----------------------------
# POSITION
# -----------------------------

class Position(db.Model):

    __tablename__ = "position"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    employees = db.relationship(
        "User",
        backref="position",
        lazy=True
    )

    def __repr__(self):
        return f"<Position {self.name}>"


# -----------------------------
# CHECKPOINT TYPE
# -----------------------------

class CheckpointType(db.Model):

    __tablename__ = "checkpoint_types"

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.String(10), nullable=False)  
    # example: IN / OUT

    checkpoints = db.relationship(
        "Checkpoint",
        backref="type",
        lazy=True
    )

    def __repr__(self):
        return f"<CheckpointType {self.value}>"


# -----------------------------
# CHECKPOINT
# -----------------------------

class Checkpoint(db.Model):

    __tablename__ = "checkpoints"

    id = db.Column(db.Integer, primary_key=True)

    moment = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    type_id = db.Column(
        db.Integer,
        db.ForeignKey("checkpoint_types.id"),
        nullable=False
    )

    def __repr__(self):
        return f"<Checkpoint {self.employee_id} {self.moment}>"