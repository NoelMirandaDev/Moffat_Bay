from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db
import re

def register_routes(app):
    """
    Attaches all route handlers to 'app'.
    Add new routes here (login, register, reservation, etc.).
    """

    # --------------------
    # Landing Page route
    # --------------------
    @app.route("/")
    def landing():

        return render_template("landing.html")
    
    # ---------------------
    # Register Page route
    # ---------------------
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
                    # Check if email address is valid
                    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
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
                    # Check database to see if email already exists
                    else:
                        result = db.session.execute(text("SELECT * FROM customer WHERE email = :email"), {"email": email}).fetchone()
                    if result:
                        flash("Email is already registered.", "error")
                    # Everything is valid, hash password and register user to database
                    else:
                        pw_hash = generate_password_hash(password)
                        try:
                            db.session.execute(text("INSERT INTO customer (FirstName, LastName, Email, Phone, PasswordHash) VALUES (:first, :last, :email, :phone, :pw_hash)"), {"first": first, "last": last, "email": email, "phone": phone, "pw_hash": pw_hash})
                            db.session.commit()
                            flash("You have successfully registered.", "success")
                            return redirect(url_for("login"))
                        except Exception as e:
                            db.session.rollback()
                            print(f"Error: {e}")
                
            except Exception:
                flash("Something went wrong, please try again.", "error")         
        
        return render_template("register.html")

    # -------------------------------
    # Database Connection Test Page
    # -------------------------------
    @app.route("/db-health")
    def db_health():
        # Simple ping to confirm DB connectivity
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return "Database connection OK"
        except Exception as e:
            return f"Database connection FAILED: {e}", 500
        
    # ------------------
    # Login Page route
    # ------------------
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            # Look up the user by email
            customer = db.session.execute(
                text("SELECT * FROM customer WHERE Email = :email"),
                {"email": email}
            ).fetchone()

            if not customer or not check_password_hash(customer.PasswordHash, password):
                flash("Invalid email or password.", "error")
                return redirect(url_for("login"))
            
            # Stores minimal, safe info in the session
            session["customer_id"] = customer.CustomerID
            session["customer_email"] = customer.Email
            session["customer_name"] = customer.FirstName

            flash(f"Welcome back, {customer.FirstName}!", "success")
            return redirect(url_for("landing"))

        # GET: render the login form
        return render_template("login.html")
    
    # -----------------------------------
    # Logout route (clears the session)
    # -----------------------------------
    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("landing"))