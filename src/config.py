import os # Reads environment variables

class Config:
    # These lines pull values from the .env file (or system environment)
    # If the variable is not found, it uses the value after the comma as a default
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "moffat_bay")

    # Builds the full database connection string (URI) that SQLAlchemy uses
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Disables a feature not needed (saves resources)
    SQLALCHEMY_TRACK_MODIFICATIONS = False