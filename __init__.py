# in app/__init__.py
from flask import Flask
from .routes.learner_routes import learner_bp

def create_app():
    app = Flask(__name__, static_folder='../frontend/static', template_folder='../frontend/templates')
    app.register_blueprint(learner_bp)
    return app