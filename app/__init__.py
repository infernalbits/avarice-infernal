from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.api.routes import api_bp
    from app.api.enhanced_routes import enhanced_api_bp
    from app.api.enhanced_ml_routes import enhanced_ml_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(enhanced_api_bp, url_prefix='/api')
    app.register_blueprint(enhanced_ml_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
