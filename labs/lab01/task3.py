import hashlib
import secrets

MIN_PASSWORD_LENGTH = 16


def generate_salt(length: int = 16) -> str:
    """Генерує криптографічно стійку сіль у hex-форматі."""
    return secrets.token_hex(length)


def hash_password_sha512(password: str, salt: str) -> str:
    """Хешує пароль із сіллю за допомогою алгоритму SHA-512."""
    salted_password = (salt + password).encode("utf-8")
    return hashlib.sha512(salted_password).hexdigest()


def process_user_password(password: str) -> dict:
    if len(password) < MIN_PASSWORD_LENGTH:
        return {
            "success": False,
            "error": f"Пароль занадто короткий ({len(password)} < {MIN_PASSWORD_LENGTH} символів)",
            "salt": None,
            "hash": None,
        }

    salt = generate_salt()
    pwd_hash = hash_password_sha512(password, salt)

    return {
        "success": True,
        "error": None,
        "salt": salt,
        "hash": pwd_hash,
    }