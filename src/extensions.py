from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

# This creates one database object (db) that we can share
# across the whole project. Instead of making new ones in
# different files, we all use this single db.
db = SQLAlchemy()

# This enables CSRF (Cross-Site Request Forgery) protection for the app.
# It makes sure that forms and requests include a secure token so users
# are protected against malicious attacks.
csrf = CSRFProtect()