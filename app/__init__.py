from flask import Flask
from config import Config
from app.db import init_db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize DB schema if MySQL is available
    init_db()

    # Register Blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.main_routes import main_bp
    from app.routes.tracker_routes import tracker_bp
    from app.routes.productivity_routes import productivity_bp
    from app.routes.expense_routes import expense_bp
    from app.routes.cluster_routes import cluster_bp
    from app.routes.ai_routes import ai_bp
    from app.routes.profile_routes import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tracker_bp)
    app.register_blueprint(productivity_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(cluster_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(profile_bp)

    return app
