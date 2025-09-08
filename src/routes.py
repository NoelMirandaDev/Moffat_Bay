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

    # Landing page (shows backend connection message)
    @app.route("/")
    def landing():
        backend_message = "✅ Backend connection is running."
        return render_template("index.html", backend_message=backend_message)

    # Redirect for /index.html to /
    @app.route("/index.html")
    def index_html_redirect():
        return redirect(url_for("landing"))

    # Attraction page
    @app.route("/attraction.html")
    def attraction():
        return render_template("attraction.html")

    # About Us page
    @app.route("/about.html")
    def about():
        return render_template("about.html")

    # Lodge Reservation page
    @app.route("/lodge_reservation.html")
    def lodge_reservation():
        return render_template("lodge_reservation.html")

    # Reservation Lookup page
    @app.route("/reservation_lookup.html")
    def reservation_lookup():
        return render_template("reservation_lookup.html")

    # Reservation Summary page
    @app.route("/reservation_summary.html")
    def reservation_summary():
        return render_template("reservation_summary.html")

    # Registration page
    @app.route("/registration.html")
    def registration():
        return render_template("registration.html")

    # Contact page
    @app.route("/contact.html")
    def contact():
        return render_template("contact.html")

    # ---------------------
    # Register Page route
    # ---------------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
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
                elif not re.match(r"[A-Za-z]+$", first) or not re.match(r"[A-Za-z]+$", last):
                    flash("Name must only contain letters.", "error")
                elif not re.match(r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$", phone):
                    flash("Must be a valid US phone number.")
                elif not re.match(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}", password):
                    flash("Password must be at least 8 characters, contain 1 uppercase and lowercase letter and a number.", "error")
                else:
                    result = db.session.execute(text("SELECT * FROM customer WHERE email = :email"), {"email": email}).fetchone()
                    if result:
                        flash("Email is already registered.", "error")
                    else:
                        pw_hash = generate_password_hash(password)
                        try:
                            db.session.execute(
                                text("INSERT INTO customer (FirstName, LastName, Email, Phone, PasswordHash) VALUES (:first, :last, :email, :phone, :pw_hash)"),
                                {"first": first, "last": last, "email": email, "phone": phone, "pw_hash": pw_hash}
                            )
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

            customer = db.session.execute(
                text("SELECT * FROM customer WHERE Email = :email"),
                {"email": email}
            ).fetchone()

            if not customer or not check_password_hash(customer.PasswordHash, password):
                flash("Invalid email or password.", "error")
                return redirect(url_for("login"))
            
            session["customer_id"] = customer.CustomerID
            session["customer_email"] = customer.Email
            session["customer_name"] = customer.FirstName

            flash(f"Welcome back, {customer.FirstName}!", "success")
            return redirect(url_for("landing"))

        return render_template("login.html")
    
    # -----------------------------------
    # Logout route (clears the session)
    # -----------------------------------
    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("landing"))
