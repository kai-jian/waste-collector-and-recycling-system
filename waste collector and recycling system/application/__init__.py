import os
from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_socketio import SocketIO

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
csrf = CSRFProtect()
babel = Babel()
socketio = SocketIO(cors_allowed_origins="*")

login_manager.login_view = 'main.login' 
login_manager.login_message_category = 'info'

def get_locale():
    """Determine the best language to use for the user"""
    # Check if user has set a language preference in session
    if 'language' in session:
        return session['language']
    # Fall back to browser's preferred language (if supported)
    return request.accept_languages.best_match(['en', 'ms', 'zh']) or 'en'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_super_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    app.config['LANGUAGES'] = {
        'en': 'English',
        'ms': 'Bahasa Melayu',
        'zh': '中文 (Chinese)'
    }
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    socketio.init_app(app)

    from application.routes import main
    app.register_blueprint(main)

    with app.app_context():
        import application.models
        
        folders = [
            os.path.join(app.root_path, 'static', 'profile_pics'),
            os.path.join(app.root_path, 'static', 'complaint_pics'),
            os.path.join(app.root_path, 'static', 'point_request_pics')
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            
        db.create_all()
    return app