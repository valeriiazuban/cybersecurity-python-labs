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
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


def main():
    print(f"Студент: {STUDENT_NAME}")
    print(f"Група: {GROUP_NAME}")
    print(f"Варіант: {VARIANT_NUMBER}")

    print("--- Завдання 1: Аналізатор паролів (Варіант 14) ")

    passwords_to_check = prepare_passwords_list(INITIAL_PASSWORDS)
    print(f"Всього паролів для аналізу : {len(passwords_to_check)}\n")

    for idx, pwd in enumerate(passwords_to_check, 1):
        res = check_password_strength(pwd, CRITERIA, FORBIDDEN_PASSWORDS)
        print(f"{idx}. Пароль: '{pwd}'")
        print(f"   Статус: {res['strength']} | Бал: {res['score']}/4")
        if res["feedback"]:
            print(f"   Зауваження: {', '.join(res['feedback'])}")
        print("-" * 40)


if __name__ == "__main__":
    main()