from flask import Flask, render_template, request, url_for, flash, redirect # Imports Flask to create the web application
from flask_sqlalchemy import SQLAlchemy # Imports SQLAlchemy for database integration with Flask
from sqlalchemy import text # Imports text to run simple SQL statements directly (used in db_health route)
from config import Config # Imports configuration settings (e.g., database connection info)
from dotenv import load_dotenv, find_dotenv # Imports dotenv tools to load variables from a .env file (for DB credentials, etc.)
from werkzeug.security import generate_password_hash
import re
# Loads environment variables from the .env file so they can be used in Config
load_dotenv(find_dotenv())

# Creates the Flask application
app = Flask(__name__)
app.secret_key = "default"
# Load configuration values from our Config class
app.config.from_object(Config)

# Initializes SQLAlchemy with our Flask app
# This allows us to interact with the database using Python objects (ORM)
db = SQLAlchemy(app)

# Defines the landing page route
@app.route("/")
def landing():
    return "<h1>Welcome to Moffat Bay Lodge</h1>"

# Defines register page route for when we visit /register
@app.route("/register", methods=["GET", "POST"])
def register():
    #Check if form is filled out
    if request.method == "POST" and "first" in request.form and "last" in request.form and "email" in request.form and "password" in request.form and "phone" in request.form:
        first = request.form["first"]
        last = request.form["last"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        
        try:
            #Connect to DB
            with db.engine.connect() as conn:
                #Check DB to see if email is already registered
                result = conn.execute(text("SELECT * FROM customer WHERE email = :email"), {"email": email}).fetchone()
                if result:
                    flash("Email is already registered.", "error")
                #Check if email address is valid
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    flash("Invalid email address", "error")
                #Check if first and last name are valid.
                elif not re.match(r"[A-Za-z]+$", first) or not re.match(r"[A-Za-z]+$", last):
                    flash("Name must only contain letters.", "error")
                #Check if phone number is valid.
                elif not re.match(r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$", phone):
                    flash("Must be a valid US phone number.")
                #Check if password is valid
                elif not re.match(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}", password):
                    flash("Password must be atleast 8 charcters, contain 1 uppercase and lowercase letter and a number." "error")
                #Everything is valid, hash password and register user to database
                else:
                    pw_hash = generate_password_hash(password)
                    conn.execute(text("INSERT INTO customer (FirstName, LastName, Email, Phone, PasswordHash) VALUES (:first, :last, :email, :phone, :pw_hash)"), {"first": first, "last": last, "email": email, "phone": phone, "pw_hash": pw_hash})
                    conn.commit()
                    flash("You have successfully registered.", "success")
            
        except Exception:
            flash("Something went wrong, please try again.", "error")         
    
    return render_template("register.html")
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