import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from labs.lab01.task1 import (
    CRITERIA,
    FORBIDDEN_PASSWORDS,
    INITIAL_PASSWORDS,
    check_password_strength,
    prepare_passwords_list,
)
from labs.lab01.task2 import (
    RESOURCES,
    USERS,
    check_resource_access,
)
from labs.lab01.task3 import (
    MIN_PASSWORD_LENGTH,
    USERS_TO_REGISTER,
    ValidationError,
    create_users,
    generate_personal_salt,
    load_users_db,
    login,
)
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def main():
    print(f"Студент: {STUDENT_NAME}")
    print(f"Група: {GROUP_NAME}")
    print(f"Варіант: {VARIANT_NUMBER}")

    print("Завдання 1")
    passwords_to_check = prepare_passwords_list(INITIAL_PASSWORDS)
    print(f"Всього паролів для аналізу : {len(passwords_to_check)}\n")

    for idx, pwd in enumerate(passwords_to_check, 1):
        res = check_password_strength(pwd, CRITERIA, FORBIDDEN_PASSWORDS)
        print(f"{idx}. Пароль: '{pwd}'")
        print(f"   Статус: {res['strength']} | Бал: {res['score']}/4")
        if res["feedback"]:
            print(f"   Зауваження: {', '.join(res['feedback'])}")
        print("-" * 40)
    print("\n Завдання 2")
    for username in USERS:
        print(f"\nПеревірка доступу для користувача: [{username}]")
        for res_name, req_level in RESOURCES[:3]:
            allowed, reason = check_resource_access(
                username, res_name, req_level
            )
            status = "ДОЗВОЛЕНО" if allowed else "ВІДМОВЛЕНО"
            print(
                f"  Ресурс: {res_name:<20} | Статус: {status:<10} | Причина: {reason}"
            ) 
    print("\nЗавдання 3 Хешування, Реєстрація та Автентифікація ")
    print(f"Персональна сіль: '{generate_personal_salt()}'")
    print(f"Мінімальна довжина пароля: {MIN_PASSWORD_LENGTH}\n")

    # Обробка винятків
    try:
        # Реєстрація користувачів
        csv_path = create_users(USERS_TO_REGISTER)
        print(f"[OK] Базу даних збережено: {csv_path}")

        # 4. Читання бази даних
        users_db = load_users_db(csv_path)
        print("\n--- База даних користувачів (users.csv) ---")
        print(f"{'Логін':<25} | {'Хеш пароля (SHA-512)':<30}")
        print("-" * 60)
        for u in users_db:
            print(f"{u['username']:<25} | {u['password_hash'][:27]}...")

        # 5. Автентифікація  6. Логування
        print("\n--- Тестування автентифікації ---")
        test_credentials = [
            ("blockchain_dev", "SuperSecureBlockchainPassword2026!"),  # Успіх
            ("crypto_trader", "WrongPassword1234567!"),                 # Невірний пароль
        ]

        for u, p in test_credentials:
            is_logged_in = login(u, p, users_db)
            res_str = "УСПІШНО" if is_logged_in else "ПОМИЛКА ВХОДУ"
            print(f"Спроба входу для '{u}': {res_str}")

    except (OSError, FileNotFoundError, PermissionError, ValidationError, ValueError) as e:
        print(f"[ERROR] Виникла помилка: {e}")


if __name__ == "__main__":
    main()