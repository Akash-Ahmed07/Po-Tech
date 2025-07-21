import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///po_tech.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-string")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Mail Configuration - Disabled for development
    app.config['MAIL_SERVER'] = None  # Disable email for development
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None
    app.config['MAIL_DEFAULT_SENDER'] = "noreply@potech.edu"
    app.config['MAIL_SUPPRESS_SEND'] = True  # Suppress sending emails in development
    
    # File Upload Configuration
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Create upload directories
    upload_dirs = [
        'uploads',
        'uploads/pdfs',
        'uploads/animations', 
        'uploads/books',
        'uploads/covers',
        'uploads/blog_images'
    ]
    for directory in upload_dirs:
        os.makedirs(directory, exist_ok=True)
    
    with app.app_context():
        # Import models to ensure tables are created
        import models
        db.create_all()
        
        # Create default admin user
        from models import User
        from werkzeug.security import generate_password_hash
        
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@potech.com',
                password_hash=generate_password_hash('Unitedsylhet90'),
                is_admin=True,
                is_verified=True
            )
            db.session.add(admin_user)
            db.session.commit()
    
    # Register routes
    from routes import register_routes
    register_routes(app)
    
    return app

# Create the app instance
app = create_app()
