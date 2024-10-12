from flask import render_template
from app import create_app
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Create the Flask application instance
app = create_app()


@app.route("/", methods=["GET"])
def index():
    """Render the index page."""
    return render_template("index.html")  # Render the index template


if __name__ == "__main__":
    # Run the application in debug mode, accessible on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)