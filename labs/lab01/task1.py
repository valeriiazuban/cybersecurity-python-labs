import random
import re

# Вхідні дані за Варіантом 14
INITIAL_PASSWORDS = [
    "C2@Command",
    "plain123",
    "Backdoor@D3tect",
    "public123",
    "Rootk1t@Hunt",
    "access123",
    "Exploit@An4lysis",
    "basic",
    "Payload@D3code",
    "default123",
]

CRITERIA = {
    "min_length": 10,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

FORBIDDEN_PASSWORDS = {
    "plain123",
    "public123",
    "access123",
    "basic",
    "default123",
    "user",
}


def prepare_passwords_list(passwords: list[str]) -> list[str]:
    """Генерує 3 випадкові індекси та додає дублікати відповідних паролів у кінець"""
    working_list = passwords.copy()
    random_indices = [random.randint(0, len(passwords) - 1) for _ in range(3)]

    for idx in random_indices:
        working_list.append(passwords[idx])

    return working_list


def check_password_strength(password: str, criteria: dict, forbidden: set) -> dict:
    feedback = []

    # Перевірка на присутність у списку заборонених
    if password in forbidden:
        return {
            "score": 0,
            "strength": "Заборонений (Критично слабкий)",
            "feedback": ["Пароль міститься у списку заборонених паролів!"],
        }

    score = 0

    # Довжина
    if len(password) >= criteria.get("min_length", 10):
        score += 1
    else:
        feedback.append(
            f"Довжина має бути не менше {criteria.get('min_length', 10)} символів"
        )

    # Великі літери
    if criteria.get("require_upper") and re.search(r"[A-Z]", password):
        score += 1
    elif criteria.get("require_upper"):
        feedback.append("Додайте велику літеру")

    # Цифри
    if criteria.get("require_digits") and re.search(r"\d", password):
        score += 1
    elif criteria.get("require_digits"):
        feedback.append("Додайте цифри")

    # Спецсимволи
    if criteria.get("require_special") and re.search(
        r"[!@#$%^&*(),.?\":{}|<>]", password
    ):
        score += 1
    elif criteria.get("require_special"):
        feedback.append("Додайте спецсимволи ")

    strength = "Сильний" if score == 4 else ("Середній" if score >= 2 else "Слабкий")

    return {"score": score, "strength": strength, "feedback": feedback}
