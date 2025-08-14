from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from datetime import timedelta
import openai
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
mail=Mail()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)

    app.config['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
    if not app.config['OPENAI_API_KEY']:
        raise ValueError("FATAL ERROR: OPENAI_API_KEY not found in .env file.")
    openai.api_key = app.config['OPENAI_API_KEY']
    print("✅ OpenAI API key loaded successfully.")

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback-secret")
    print("--- Checking Environment Variables ---")
    database_url_from_env = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL found: {database_url_from_env}")
    print("------------------------------------")
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, '..', 'instance', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    mail.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_request
    def refresh_session():
        session.permanent = True

    from .auth import auth
    auth.google = google
    app.register_blueprint(auth)

    return app
