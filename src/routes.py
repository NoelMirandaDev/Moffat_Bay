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

    # --------------
    # Landing Page
    # --------------
    @app.route("/")
    def landing():
        return render_template("index.html")

    # -----------------
    # Attraction Page
    # -----------------
    @app.route("/attraction.html")
    def attraction():
        return render_template("attraction.html")

    # ---------------
    # About Us Page
    # ---------------
    @app.route("/about.html")
    def about():
        return render_template("about.html")

    # ------------------------
    # Lodge Reservation Page
    # ------------------------
    @app.route("/lodge_reservation.html")
    def lodge_reservation():
        return render_template("lodge_reservation.html")

    # -------------------------
    # Reservation Lookup Page
    # -------------------------
    @app.route("/reservation_lookup.html")
    def reservation_lookup():
        return render_template("reservation_lookup.html")

    # --------------------------
    # Reservation Summary Page
    # --------------------------
    @app.route("/reservation_summary.html")
    def reservation_summary():
        return render_template("reservation_summary.html")

    # -------------------
    # Registration Page
    # -------------------
    @app.route("/registration", methods=["GET", "POST"])
    def registration():
        if request.method == "POST" and "first" in request.form and "last" in request.form and "email" in request.form and "password" in request.form and "phone" in request.form:
            first = request.form["first"]
            last = request.form["last"]
            email = request.form["email"]
            password = request.form["password"]
            phone = request.form["phone"]
            try:
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    flash("Invalid email address", "error")
                elif not re.match(r"[A-Za-z]+$", first) or not re.match(r"[A-Za-z]+$", last):
                    flash("Name must only contain letters.", "error")
                elif not re.match(r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$", phone):
                    flash("Must be a valid US phone number.", "error")
                elif not re.match(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}", password):
                    flash("Password must contain at least 8 characters, contain uppercase, lowercase, and a number.", "error")
                else:
                    result = db.session.execute(
                        text("SELECT * FROM customer WHERE email = :email"), {"email": email}
                    ).fetchone()
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
                        except Exception as e:
                            db.session.rollback()
                            print(f"Error: {e}")
                            flash("Database error. Please try again later.", "error")
            except Exception:
                flash("Something went wrong, please try again.", "error")
        return render_template("registration.html")

    

    # Login Page
    # ------------
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
                return render_template("index.html", show_login=True)

            session["customer_id"] = customer.CustomerID
            session["customer_email"] = customer.Email
            session["customer_name"] = customer.FirstName

            flash(f"Welcome back, {customer.FirstName}!", "success")
            return redirect(url_for("landing"))

        return redirect(url_for("landing"))

    # ------------
    # Logout Route
    # ------------
    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been successfully logged out.", "success")
        return redirect(url_for("landing"))