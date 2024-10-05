import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # Set up configuration or any necessary initialization here
    MP3_PATH = os.getenv("MP3_DIRECTORY")
    MUSIC_DIR = fr'{MP3_PATH}'
    EXPORT_DIR = 'app/services/metadata_exports/'

    # Ensure directories exist
    os.makedirs(MUSIC_DIR, exist_ok=True)
    os.makedirs(EXPORT_DIR, exist_ok=True)

    # Import and register the API blueprint
    from app.api.api_routes import api
    app.register_blueprint(api, url_prefix='/api')  # Prefix all API routes with /api

    # Import and register other blueprints if you have any
    # from app.some_module import some_blueprint
    # app.register_blueprint(some_blueprint)

    return app
