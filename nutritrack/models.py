from flask_login import UserMixin
from datetime import datetime
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
    profile_pic_url = db.Column(db.String(250), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.now)

    height_cm = db.Column(db.Float, nullable=True)
    weight_kg = db.Column(db.Float, nullable=True)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    activity_level = db.Column(db.String(50), nullable=True)
    last_health_update = db.Column(db.DateTime, nullable=True)
    recommended_calories = db.Column(db.Integer, nullable=True)
    goal = db.Column(db.String(50), nullable=True, default='Maintain Weight')

    # Relationship to history table
    history = db.relationship('History', backref='user', lazy=True)
    meal_plans = db.relationship('MealPlan', backref='user', lazy=True)


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String(150))
    ingredients = db.Column(db.Text)
    nutrition_result = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class MealPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requirements = db.Column(db.Text, nullable=False)
    meal_plan_result = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
