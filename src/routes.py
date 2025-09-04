from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import text
from werkzeug.security import check_password_hash
from extensions import db

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