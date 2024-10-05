from flask import Flask, render_template
import os
from app.api.api_routes import api
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, template_folder='app/templates')
app.register_blueprint(api, url_prefix='/api')  # Prefix all API routes with /api

# dotenv paths
MP3_PATH = os.getenv("MP3_DIRECTORY")
MUSIC_DIR = fr'{MP3_PATH}'  # Directory for storing MP3 files
EXPORT_DIR = 'app/services/metadata_exports/'  # Directory for storing exported metadata

# Ensure directories exist
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    """Render the index page."""
    return render_template("index.html")  # Render the index template


if __name__ == "__main__":
    # Run the application in debug mode
    app.run(debug=True)
