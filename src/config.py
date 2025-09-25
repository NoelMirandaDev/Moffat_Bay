import os
import platform
from dotenv import load_dotenv

# Detect system and load the right env file
if platform.system() == "Darwin":  # macOS
    load_dotenv(".env.mac")
elif platform.system() == "Windows":
    load_dotenv(".env.win")
else:
    # Default for Linux or shared repo
    load_dotenv(".env")

class Config:
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "moffat_bay")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    WTF_CSRF_ENABLED = True

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
