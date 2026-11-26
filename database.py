import os
import json
import sqlite3
from contextlib import contextmanager

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    import psycopg2
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    @contextmanager
    def get_conn():
        conn = psycopg2.connect(DATABASE_URL)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db():
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS app_data (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """)

    def save_data(key, value):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO app_data (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
                    (key, json.dumps(value))
                )

    def load_data(key, default=None):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT value FROM app_data WHERE key = %s", (key,))
                row = cur.fetchone()
                return json.loads(row[0]) if row else default

    def delete_data(key):
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM app_data WHERE key = %s", (key,))

else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "vibmagick_data.db")

    @contextmanager
    def get_conn():
        conn = sqlite3.connect(DB_PATH)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db():
        with get_conn() as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS app_data (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """)

    def save_data(key, value):
        with get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO app_data (key, value) VALUES (?, ?)",
                (key, json.dumps(value))
            )

    def load_data(key, default=None):
        with get_conn() as conn:
            cur = conn.execute("SELECT value FROM app_data WHERE key = ?", (key,))
            row = cur.fetchone()
            return json.loads(row[0]) if row else default

    def delete_data(key):
        with get_conn() as conn:
            conn.execute("DELETE FROM app_data WHERE key = ?", (key,))

init_db()
