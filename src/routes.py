from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from werkzeug.security import generate_password_hash
from extensions import db

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

    # Contact page
    @app.route("/contact.html")
    def contact():
        return render_template("contact.html")

    # Registration page - GET + POST
    @app.route("/registration.html", methods=["GET", "POST"])
    def registration():
        if request.method == "POST":
            
            print("✅ DEBUG: Received form submission.")
            print("First:", request.form.get("first_name"))
            print("Last:", request.form.get("last_name"))
            print("Email:", request.form.get("email"))
            print("Phone:", request.form.get("phone"))
            print("Password:", request.form.get("password"))
            
            # Retrieve form data
            first_name = request.form.get("first_name")
            last_name = request.form.get("last_name")
            email = request.form.get("email")
            phone = request.form.get("phone")
            password = request.form.get("password")

            # Basic validation
            if not all([first_name, last_name, email, password]):
                flash("Please fill in all required fields.", "error")
                return render_template("registration.html")

            # Hash the password
            password_hash = generate_password_hash(password)

            # Insert into database
            insert_query = text("""
                INSERT INTO customer (FirstName, LastName, Email, Phone, PasswordHash)
                VALUES (:first_name, :last_name, :email, :phone, :password_hash)
            """)

            try:
                with db.engine.begin() as conn:
                    conn.execute(insert_query, {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone,
                        "password_hash": password_hash
                    })

                flash("Registration successful! You can now log in.", "success")
                return redirect(url_for("landing"))

            except Exception as e:
                flash(f"Registration failed: {e}", "error")
                return render_template("registration.html")

        return render_template("registration.html")


    @app.route("/test-insert")
    def test_insert():
        try:
            with db.engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO customer (FirstName, LastName, Email, Phone, PasswordHash)
                    VALUES ('Test', 'User', 'test@example.com', '123-456-7890', 'hashedpassword123')
                """))
            return "✅ Insert worked!"
        except Exception as e:
            return f"❌ Insert failed: {e}"
        
    # Database health check
    @app.route("/db-health")
    def db_health():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return "Database connection OK"
        except Exception as e:
            return f"Database connection FAILED: {e}", 500

    