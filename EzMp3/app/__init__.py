from flask import Flask

def create_app():
    app = Flask(__name__)

    with app.app_context():
        # Import parts of our application
        from . import main

        # Register blueprints
        app.register_blueprint(main.bp)

    return app
