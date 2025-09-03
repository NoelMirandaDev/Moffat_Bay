from sqlalchemy import text
from extensions import db

def register_routes(app):
    """
    Attaches all route handlers to 'app'.
    Add new routes here (login, register, reservation, etc.).
    """

    @app.route("/")
    def landing():
        return "<h1>Welcome to Moffat Bay Lodge</h1>"

    @app.route("/db-health")
    def db_health():
        # Simple ping to confirm DB connectivity
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return "Database connection OK"
        except Exception as e:
            return f"Database connection FAILED: {e}", 500