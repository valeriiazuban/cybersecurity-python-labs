import sys
from datetime import datetime, timezone

from labs.lab02.task1 import Admin, AuditLog, User, UserAccount
from labs.lab02.task2 import analyze, build_parser


def run_demo() -> None:
    """Демонстрація функціональності Завдання 1 (ООП)."""
    print("==========================================")
    print(" Завдання 1 — Модель користувача/сесії ")
    print("==========================================")

    audit_log = AuditLog()

    user = User("j_smith", "j_smith@company.com")
    user.set_password("SecurePassword123!")

    admin = Admin(
        "sys_admin", "admin@company.com", permissions=["read", "write", "delete"]
    )
    admin.set_password("AdminPass2026!")

    account = UserAccount(user, audit_log)

    print("\n1. Тестування входу:")
    print(
        "Невдала спроба входу (невірний пароль):",
        account.login("j_smith", "WrongPass", "192.168.1.10"),
    )
    print(
        "Успішна спроба входу:",
        account.login("j_smith", "SecurePassword123!", "192.168.1.10"),
    )
    print("Статус аутентифікації:", account.is_authenticated())

    print("\n2. Тестування зміни email:")
    try:
        account["user"].email = "invalid-email-format"
    except ValueError as e:
        print("Перехоплено помилку валідації:", e)

    account["user"].email = "john.smith@newdomain.com"
    print("Новий email успішно встановлено:", account["user"].email)

    print("\n3. Тестування адміністратора:")
    print(admin)
    print("Має право 'delete'?:", admin.has_permission("delete"))
    admin.revoke_permission("delete")
    print("Після відклику 'delete':", admin.has_permission("delete"))

    print("\n4. Перевірка таймауту сесії:")
    account.session.last_activity = datetime(2020, 1, 1, tzinfo=timezone.utc)
    print("Статус сесії після штучного застарівання:", account.is_authenticated())

    print("\n5. Вихід із системи:")
    account.logout()
    print("Статус аутентифікації після logout:", account.is_authenticated())

    print("\n6. Записи журналу аудиту (AuditLog):")
    for entry in audit_log.show_all():
        print(
            f"[{entry.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}] User: {entry.username:<10} Action: {entry.action}"
        )


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        run_demo()
    elif len(sys.argv) > 1 and sys.argv[1] == "analyze":
        parser = build_parser()
        args = parser.parse_args(sys.argv[2:])
        analyze(args)
    else:
        print("Використання:")
        print("  python -m labs.lab02.main demo")
        print(
            "  python -m labs.lab02.main analyze --edr-log data/edr_events.json [параметри]"
        )


if __name__ == "__main__":
    main()
