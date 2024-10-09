import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


def create_app():
    app = Flask(__name__)

    # Load configuration from environment variables
    app.config['MP3_DIRECTORY'] = os.getenv("MP3_DIRECTORY", "default/path/to/music")
    app.config['EXPORT_DIRECTORY'] = os.getenv("EXPORT_DIRECTORY", "default/path/to/exports")

    # Ensure necessary directories exist
    initialize_directories(app.config['MP3_DIRECTORY'], app.config['EXPORT_DIRECTORY'])

    # Import and register the API blueprint
    from app.api.api_routes import api
    app.register_blueprint(api, url_prefix='/api')  # Prefix all API routes with /api

    # Import and register other blueprints if you have any
    # from app.some_module import some_blueprint
    # app.register_blueprint(some_blueprint)

    return app


def initialize_directories(music_dir, export_dir):
    """Ensure the necessary directories exist."""
    try:
        os.makedirs(music_dir, exist_ok=True)
        os.makedirs(export_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating directories: {e}")
