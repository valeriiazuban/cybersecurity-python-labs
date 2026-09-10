import functools
import hashlib
import json
import os
from datetime import datetime, timezone

from shared.student import VARIANT_NUMBER

MIN_PASSWORD_LENGTH = 16


class ValidationError(Exception):
    """Власний виняток для помилок валідації пароля."""



# Персональна сіль
def generate_personal_salt() -> str:
    return str(VARIANT_NUMBER).zfill(5)


# Хешування
def generate_hash(password: str, salt: str = "00000") -> str:
    if not password or not salt:
        raise ValueError("Пароль та сіль не можуть бути порожніми")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(
            f"Пароль коротший за {MIN_PASSWORD_LENGTH} символів"
        )

    salted_password = (password + salt).encode("utf-8")
    return hashlib.sha512(salted_password).hexdigest()


# 3. Реєстрація користувачів
USERS_TO_REGISTER = (
    ("blockchain_dev", "SuperSecureBlockchainPassword2026!"),
    ("smart_contract_auditor", "ContractAuditor_Secret_Pass16"),
    ("crypto_trader", "TraderProAlgorithm_2026_Secure"),
    ("wallet_user", "WalletUser_Pass_Minimum16Chars!"),
    ("mining_pool", "MiningPoolAdminSecret_Pass16!"),
    ("defi_expert", "DeFiProtocolMasterPass2026!"),
    ("validator_node", "ValidatorNodeSecureAccessPass1!"),
    ("market_analyst", "MarketDataAnalystPass2026!"),
    ("community_lead", "CommunityForumLeaderPass16!"),
    ("security_guard", "InstitutionalSecurityPass2026!"),
)


def create_user(username: str, password: str) -> tuple[str, str]:
    salt = generate_personal_salt()
    pwd_hash = generate_hash(password, salt)
    return (username, pwd_hash)


def create_users(users_list: tuple | list) -> str:
    data_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "data")
    )
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "users.csv")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("username,password_hash\n")
        for username, password in users_list:
            try:
                user_data = create_user(username, password)
                f.write(f"{user_data[0]},{user_data[1]}\n")
            except (ValidationError, ValueError) as e:
                print(
                    f"Пропущено користувача {username}: {e}"
                )

    return file_path


# Читання бази даних
def load_users_db(file_path: str) -> list[dict]:
    users_db = []
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не знайдено")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()[1:]  # пропускаємо заголовок
        for line in lines:
            line = line.strip()
            if line:
                username, pwd_hash = line.split(",")
                users_db.append({"username": username, "password_hash": pwd_hash})
    return users_db

# Логування подій (Декоратор)
def log_event(func):
    @functools.wraps(func)
    def wrapper(username: str, password: str, *args, **kwargs):
        result_status = "failure"
        try:
            res = func(username, password, *args, **kwargs)
            if res:
                result_status = "success"
            return res
        finally:
            data_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "data")
            )
            os.makedirs(data_dir, exist_ok=True)
            log_file = os.path.join(data_dir, "log.json")

            log_entry = {
                "event": "login",
                "user": username,
                "result": result_status,
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                "args": list(args),
                "kwargs": kwargs,
            }

            logs = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []

            logs.append(log_entry)
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)

    return wrapper
    # Автентифікація
@log_event
def login(username: str, password: str, users_db: list[dict]) -> bool:
    if not username or not password:
        raise ValueError("Логін та пароль не можуть бути порожніми")

    salt = generate_personal_salt()
    pwd_hash = generate_hash(password, salt)

    for user in users_db:
        if user["username"] == username and user["password_hash"] == pwd_hash:
            return True
    return False


