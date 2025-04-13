gunicorn app: app
# app.py
from flask import Flask
app = Flask(__name__)  # Make sure this is defined

@app.route("/")
def home():
    return "Hello, World!"

# ... rest of your code
