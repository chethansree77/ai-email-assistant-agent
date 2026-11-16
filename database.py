import sqlite3
from datetime import datetime

DB_NAME = "email_assistant.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            category TEXT,
            created_at TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


def draft_exists(task_type, subject, body, category=None):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id FROM drafts
        WHERE task_type = ?
          AND TRIM(LOWER(subject)) = TRIM(LOWER(?))
          AND TRIM(body) = TRIM(?)
          AND COALESCE(category, '') = COALESCE(?, '')
        LIMIT 1
    """, (task_type, subject, body, category))
    existing = cursor.fetchone()
    connection.close()
    return existing is not None


def save_draft(task_type, subject, body, category=None):
    # Database-level protection: identical content is not inserted twice.
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT id FROM drafts
        WHERE task_type = ?
          AND TRIM(LOWER(subject)) = TRIM(LOWER(?))
          AND TRIM(body) = TRIM(?)
          AND COALESCE(category, '') = COALESCE(?, '')
        ORDER BY id DESC
        LIMIT 1
    """, (task_type, subject, body, category))
    existing = cursor.fetchone()
    if existing:
        connection.close()
        return existing["id"]

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO drafts (task_type, subject, body, category, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (task_type, subject, body, category, created_at))
    connection.commit()
    draft_id = cursor.lastrowid
    connection.close()
    return draft_id


def get_all_drafts():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM drafts ORDER BY id DESC")
    drafts = cursor.fetchall()
    connection.close()
    return drafts


def get_draft_by_id(draft_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
    draft = cursor.fetchone()
    connection.close()
    return draft


def update_draft(draft_id, subject, body):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE drafts SET subject = ?, body = ? WHERE id = ?",
        (subject, body, draft_id)
    )
    connection.commit()
    updated_rows = cursor.rowcount
    connection.close()
    return updated_rows


def delete_draft(draft_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
    connection.commit()
    deleted_rows = cursor.rowcount
    connection.close()
    return deleted_rows


def search_drafts(keyword):
    if not keyword or not keyword.strip():
        return get_all_drafts()
    connection = get_connection()
    cursor = connection.cursor()
    search_value = f"%{keyword.strip()}%"
    cursor.execute("""
        SELECT * FROM drafts
        WHERE subject LIKE ? OR body LIKE ?
           OR category LIKE ? OR task_type LIKE ?
        ORDER BY id DESC
    """, (search_value, search_value, search_value, search_value))
    drafts = cursor.fetchall()
    connection.close()
    return drafts


def get_recent_drafts(limit=5):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM drafts ORDER BY id DESC LIMIT ?", (limit,)
    )
    drafts = cursor.fetchall()
    connection.close()
    return drafts


def get_drafts_by_category(category):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT * FROM drafts WHERE category = ? ORDER BY id DESC",
        (category,)
    )
    drafts = cursor.fetchall()
    connection.close()
    return drafts
