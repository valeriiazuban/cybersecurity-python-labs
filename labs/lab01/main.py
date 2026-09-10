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


if __name__ == "__main__":
    main()