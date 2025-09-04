from flask import Flask
from flask_cors import CORS   # <--- ADD THIS LINE
from backend.db import get_db, close_db
from backend.routes import sample

def create_app():
    app = Flask(__name__)
    CORS(app)  # <--- ADD THIS LINE (enables CORS for all routes)
    app.config.from_object('backend.config.Config')

    # Register blueprints
    app.register_blueprint(sample.bp)

    # Database teardown
    app.teardown_appcontext(close_db)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)