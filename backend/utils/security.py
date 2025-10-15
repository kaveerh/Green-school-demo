"""
Security Utilities
Password hashing, token generation, and other security functions
"""
import bcrypt
import secrets
import string


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    # Convert password to bytes and hash with bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password to compare

    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def generate_reset_token(length: int = 32) -> str:
    """
    Generate a secure random token for password reset

    Args:
        length: Length of the token

    Returns:
        Random token string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_verification_token(length: int = 32) -> str:
    """
    Generate a secure random token for email verification

    Args:
        length: Length of the token

    Returns:
        Random token string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
