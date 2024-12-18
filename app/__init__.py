from flask import Flask
from app.config import init_app, db, login_manager
from app.models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = init_app()

    # Register blueprints
    from app.routes.auth import auth
    from app.routes.avatar import avatar
    from app.routes.clothing import clothing
    login_manager.login_view = 'main.login'
    #init_routes(app)
    app.register_blueprint(auth)
    app.register_blueprint(avatar, url_prefix='/avatar')
    app.register_blueprint(clothing, url_prefix='/clothing')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app 
