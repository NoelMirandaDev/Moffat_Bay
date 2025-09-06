from flask import render_template, redirect, url_for
from sqlalchemy import text
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

    # Registration page
    @app.route("/registration.html")
    def registration():
        return render_template("registration.html")

    # Contact page
    @app.route("/contact.html")
    def contact():
        return render_template("contact.html")

    # Database health check
    @app.route("/db-health")
    def db_health():
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return "Database connection OK"
        except Exception as e:
            return f"Database connection FAILED: {e}", 500