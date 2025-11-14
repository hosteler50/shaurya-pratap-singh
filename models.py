from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')


class Hostel(db.Model):
    __tablename__ = 'hostels'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, default='')
    image = db.Column(db.String(255), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    reviews = db.relationship('Review', backref='hostel', lazy=True, cascade='all, delete-orphan')


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hostel_id = db.Column(db.String(36), db.ForeignKey('hostels.id'), nullable=False)
    reviewer_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    reviewer_name = db.Column(db.String(255), default='Anonymous')
    
    rating_overall = db.Column(db.Float, nullable=True)
    rating_food = db.Column(db.Float, nullable=True)
    rating_cleaning = db.Column(db.Float, nullable=True)
    rating_staff = db.Column(db.Float, nullable=True)
    rating_location = db.Column(db.Float, nullable=True)
    rating_owner = db.Column(db.Float, nullable=True)
    
    comment = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
