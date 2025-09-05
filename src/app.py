from flask import Flask # Imports Flask to create the web application
from config import Config # Imports configuration settings (e.g., database connection info)
from dotenv import load_dotenv, find_dotenv # Imports dotenv tools to load variables from a .env file (for DB credentials, etc.)
from extensions import db, csrf # Imports database object and csrf token instance

def create_app():
    """
    This function builds and sets up the Flask app.
    It loads settings, connects the database, and adds routes.
    Then it gives back the ready-to-use app.
    """

    # Loads environment variables from the .env file so they can be used in Config
    load_dotenv(find_dotenv())

    # Creates the Flask application
    app = Flask(__name__)
    # Secret key to be able to flash
    app.secret_key = "default"
    # Load configuration values from our Config class
    app.config.from_object(Config)

    # Initializes SQLAlchemy from extensions with our Flask app
    # This allows us to interact with the database using Python objects (ORM)
    db.init_app(app)

    # Enables CSRF for all POST/PUT/DELETE
    csrf.init_app(app)

    # Registers all the routes
    from routes import register_routes
    register_routes(app)

    return app

# Allows running with: python app.py 
# debug=True gives detailed error messages and auto-reloads when code changes
if __name__ == "__main__":
    app = create_app() # builds the app 
    app.run(debug=True) # runs the app