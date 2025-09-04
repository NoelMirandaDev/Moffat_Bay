from flask_sqlalchemy import SQLAlchemy

# This creates one database object (db) that we can share
# across the whole project. Instead of making new ones in
# different files, we all use this single db.
db = SQLAlchemy()