import json
import logging
import sqlite3
from contextlib import closing

from labs.lab03.database import BASE_DIR, get_connection, initialize_database

SEED_PATH = BASE_DIR / "data" / "seed.json"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database() -> None:
    initialize_database()

    if not SEED_PATH.exists():
        logger.error("Файл початкових даних не знайдено: %s", SEED_PATH)
        return

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] > 0:
            logger.info("База даних вже містить дані. Пропуск заповнення.")
            return

        with open(SEED_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        try:
            with conn:
                for cat in data.get("categories", []):
                    conn.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (cat["id"], cat["name"]),
                    )

                for rec in data.get("records", []):
                    conn.execute(
                        """
                        INSERT INTO records (code, title, category_id, value, status)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            rec["code"],
                            rec["title"],
                            rec["category_id"],
                            rec["value"],
                            rec["status"],
                        ),
                    )
            logger.info("Базу даних успішно заповнено початковими даними.")
        except sqlite3.Error as e:
            logger.error("Помилка під час заповнення бази: %s", e)


if __name__ == "__main__":
    seed_database()
