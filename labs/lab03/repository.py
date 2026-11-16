import sqlite3
from typing import Any

from labs.lab03.database import get_connection


def create_category(name: str) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        cat_id = cursor.lastrowid
        conn.commit()
        return {"id": cat_id, "name": name}


def get_categories() -> list[dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        rows = cursor.fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]


def delete_category(category_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            return False
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        return True


def create_record(
    code: str, title: str, category_id: int, value: float, status: str
) -> dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
        cat_row = cursor.fetchone()
        if not cat_row:
            raise ValueError("CATEGORY_NOT_FOUND")

        cursor.execute(
            """
            INSERT INTO records (code, title, category_id, value, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (code, title, category_id, value, status),
        )
        rec_id = cursor.lastrowid
        conn.commit()
        return {
            "id": rec_id,
            "code": code,
            "title": title,
            "category_id": category_id,
            "category_name": cat_row[0],
            "value": value,
            "status": status,
        }


def get_record_by_id(record_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.id, r.code, r.title, r.category_id, c.name, r.value, r.status
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id = ?
            """,
            (record_id,),
        )
        r = cursor.fetchone()
        if not r:
            return None
        return {
            "id": r[0],
            "code": r[1],
            "title": r[2],
            "category_id": r[3],
            "category_name": r[4],
            "value": r[5],
            "status": r[6],
        }


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT r.id, r.code, r.title, r.category_id, c.name, r.value, r.status
            FROM records r
            JOIN categories c ON r.category_id = c.id
        """
        conditions = []
        params: list[Any] = []

        if category_id is not None:
            conditions.append("r.category_id = ?")
            params.append(category_id)
        if status is not None:
            conditions.append("r.status = ?")
            params.append(status)
        if min_value is not None:
            conditions.append("r.value >= ?")
            params.append(min_value)
        if q is not None:
            conditions.append("instr(r.title, ?) > 0")
            params.append(q)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "code": r[1],
                "title": r[2],
                "category_id": r[3],
                "category_name": r[4],
                "value": r[5],
                "status": r[6],
            }
            for r in rows
        ]


def update_record(
    record_id: int, code: str, title: str, category_id: int, value: float, status: str
) -> dict[str, Any] | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM records WHERE id = ?", (record_id,))
        if not cursor.fetchone():
            return None

        cursor.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
        cat_row = cursor.fetchone()
        if not cat_row:
            raise ValueError("CATEGORY_NOT_FOUND")

        cursor.execute(
            """
            UPDATE records
            SET code = ?, title = ?, category_id = ?, value = ?, status = ?
            WHERE id = ?
            """,
            (code, title, category_id, value, status, record_id),
        )
        conn.commit()
        return {
            "id": record_id,
            "code": code,
            "title": title,
            "category_id": category_id,
            "category_name": cat_row[0],
            "value": value,
            "status": status,
        }


def delete_record(record_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM records WHERE id = ?", (record_id,))
        if not cursor.fetchone():
            return False
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        conn.commit()
        return True


def create_records_bulk(
    records_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        category_ids = {r["category_id"] for r in records_data}
        placeholders = ",".join(["?"] * len(category_ids))
        cursor.execute(
            f"SELECT id, name FROM categories WHERE id IN ({placeholders})",
            list(category_ids),
        )
        cat_map = {row[0]: row[1] for row in cursor.fetchall()}
        for cat_id in category_ids:
            if cat_id not in cat_map:
                raise ValueError(f"CATEGORY_NOT_FOUND_{cat_id}")

        codes_in_batch = [r["code"] for r in records_data]
        if len(codes_in_batch) != len(set(codes_in_batch)):
            raise sqlite3.IntegrityError("DUPLICATE_CODE_IN_BATCH")

        created_records = []
        with conn:
            for r in records_data:
                cursor.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        r["code"],
                        r["title"],
                        r["category_id"],
                        r["value"],
                        r["status"],
                    ),
                )
                rec_id = cursor.lastrowid
                created_records.append(
                    {
                        "id": rec_id,
                        "code": r["code"],
                        "title": r["title"],
                        "category_id": r["category_id"],
                        "category_name": cat_map[r["category_id"]],
                        "value": r["value"],
                        "status": r["status"],
                    }
                )

        return created_records
