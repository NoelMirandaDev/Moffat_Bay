from flask import Flask, render_template, request, url_for, flash, redirect
from sqlalchemy import text
from extensions import db
from werkzeug.security import generate_password_hash
import re

def register_routes(app):
    """
    Attaches all route handlers to 'app'.
    Add new routes here (login, register, reservation, etc.).
    """

    @app.route("/")
    def landing():
        return "<h1>Welcome to Moffat Bay Lodge</h1>"
    
    # Defines register page route for when we visit /register
    @app.route("/register", methods=["GET", "POST"])
    def register():
        # Check if form is filled out
        if request.method == "POST" and "first" in request.form and "last" in request.form and "email" in request.form and "password" in request.form and "phone" in request.form:
            first = request.form["first"]
            last = request.form["last"]
            email = request.form["email"]
            password = request.form["password"]
            phone = request.form["phone"]
            
            try:
                # Connect to DB
                with db.engine.connect() as conn:
                    # Check DB to see if email is already registered
                    result = conn.execute(text("SELECT * FROM customer WHERE email = :email"), {"email": email}).fetchone()
                    if result:
                        flash("Email is already registered.", "error")
                    # Check if email address is valid
                    elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                        flash("Invalid email address", "error")
                    # Check if first and last name are valid.
                    elif not re.match(r"[A-Za-z]+$", first) or not re.match(r"[A-Za-z]+$", last):
                        flash("Name must only contain letters.", "error")
                    # Check if phone number is valid.
                    elif not re.match(r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$", phone):
                        flash("Must be a valid US phone number.")
                    # Check if password is valid
                    elif not re.match(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}", password):
                        flash("Password must be atleast 8 charcters, contain 1 uppercase and lowercase letter and a number." "error")
                    # Everything is valid, hash password and register user to database
                    else:
                        pw_hash = generate_password_hash(password)
                        conn.execute(text("INSERT INTO customer (FirstName, LastName, Email, Phone, PasswordHash) VALUES (:first, :last, :email, :phone, :pw_hash)"), {"first": first, "last": last, "email": email, "phone": phone, "pw_hash": pw_hash})
                        conn.commit()
                        flash("You have successfully registered.", "success")
                
            except Exception:
                flash("Something went wrong, please try again.", "error")         
        
        return render_template("register.html")

    @app.route("/db-health")
    def db_health():
        # Simple ping to confirm DB connectivity
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return "Database connection OK"
        except Exception as e:
            return f"Database connection FAILED: {e}", 500