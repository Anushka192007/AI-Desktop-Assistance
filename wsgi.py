gunicorn wsgi:app

# wsgi.py
from app import app  # Import your Flask app instance

if __name__ == "__main__":
    app.run()
