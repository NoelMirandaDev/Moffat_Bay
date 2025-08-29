from flask import Flask # Imports Flask to create the web application
from flask_sqlalchemy import SQLAlchemy # Imports SQLAlchemy for database integration with Flask
from sqlalchemy import text # Imports text to run simple SQL statements directly (used in db_health route)
from config import Config # Imports configuration settings (e.g., database connection info)
from dotenv import load_dotenv, find_dotenv # Imports dotenv tools to load variables from a .env file (for DB credentials, etc.)

# Loads environment variables from the .env file so they can be used in Config
load_dotenv(find_dotenv())

# Creates the Flask application
app = Flask(__name__)

# Load configuration values from our Config class
app.config.from_object(Config)

# Initializes SQLAlchemy with our Flask app
# This allows us to interact with the database using Python objects (ORM)
db = SQLAlchemy(app)

# Defines the landing page route
@app.route("/")
def landing():
    return "<h1>Welcome to Moffat Bay Lodge</h1>"

# Defines a health check route for the database when we visit /db-health
@app.route("/db-health")
def db_health():
    try:
        # Opens a connection to the database
        with db.engine.connect() as conn:
            # Runs a very simple SQL query just to test connectivity
            conn.execute(text("SELECT 1"))
        return "Database connection OK"
    except Exception as e:
        # If something goes wrong, returns the error message
        return f"Database connection FAILED: {e}", 500

# This ensures the app only runs if we start it directly with "python app.py"
# debug=True gives detailed error messages and auto-reloads when code changes
if __name__ == "__main__":
    app.run(debug=True)