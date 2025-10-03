import re
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

class RegistrationError(Exception):
    """Raised when registration validation or DB insert fails."""

class LoginError(Exception):
    """Raised when login credentials are invalid."""

def validate_registration(first: str, last: str, email: str, password: str, phone: str):
    """
    Validate registration fields. Raises RegistrationError if invalid.
    """
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise RegistrationError("Invalid email address.")
    if not re.match(r"^[A-za-z]+(?:[-' ][A-Za-z]+)*$", first) or not re.match(r"^[A-za-z]+(?:[-' ][A-Za-z]+)*$", last):
        raise RegistrationError("Name must only contain letters.")
    if not re.match(r"^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$", phone):
        raise RegistrationError("Must be a valid US phone number.")
    if not re.match(r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}", password):
        raise RegistrationError(
            "Password must contain at least 8 characters, contain uppercase, lowercase, and a number."
        )

def register_customer(first: str, last: str, email: str, phone: str, password: str):
    """
    Inserts a new customer if email not taken.
    Raises RegistrationError on duplicate or DB issues.
    """
    existing = db.session.execute(
        text("SELECT 1 FROM customer WHERE email = :email"),
        {"email": email}
    ).fetchone()
    if existing:
        raise RegistrationError("Email is already registered.")

    pw_hash = generate_password_hash(password)
    try:
        db.session.execute(
            text("""
                INSERT INTO customer (FirstName, LastName, Email, Phone, PasswordHash)
                VALUES (:first, :last, :email, :phone, :pw_hash)
            """),
            {
                "first": first,
                "last": last,
                "email": email,
                "phone": phone,
                "pw_hash": pw_hash,
            },
        )
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RegistrationError(f"Database error: {e}")
    
def authenticate_user(email: str, password: str):
    """
    Validate email + password against the DB.
    Returns a customer row if valid, else raises LoginError.
    """
    email = email.strip().lower()

    customer = db.session.execute(
        text("SELECT * FROM customer WHERE Email = :email"), {"email": email}
    ).fetchone()

    if not customer or not check_password_hash(customer.PasswordHash, password):
        raise LoginError("Invalid email or password.")

    return customer
