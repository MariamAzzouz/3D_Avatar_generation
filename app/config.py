from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_compress import Compress

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'

# Configuration paths
CSV_FILE_PATH = "Body_Measurements_output_modified2.csv"
OBJ_FOLDER_PATH = "static/3D_AVATARS"
CLOTHES_FOLDER_PATH = "static/3D_CLOTHING"

def init_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    Compress(app)

    # Configuration
    app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/javascript', 'application/json']
    app.config['COMPRESS_LEVEL'] = 6
    app.config['COMPRESS_MIN_SIZE'] = 500
    app.config['SECRET_KEY'] = 'b9e7c45dacc7041a402b95ed81f2895d'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    return app 