import os
from dotenv import load_dotenv
from app import create_app

'''
how to run:
pip install requirements.txt
python run.py
'''

load_dotenv()
app = create_app()

if __name__ == "__main__":
    # Set the host and port if desired, otherwise defaults to 127.0.0.1:5000
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True") == "True"  # Convert to boolean

    app.run(host=host, port=port, debug=debug)
