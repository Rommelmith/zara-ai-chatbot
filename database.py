import sqlite3
from datetime import datetime

DB_PATH = "handoverit.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            item      TEXT,
            condition TEXT,
            looking_for TEXT,
            created_at  TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_listing(item, condition, looking_for):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO listings (item, condition, looking_for, created_at) VALUES (?, ?, ?, ?)",
        (item, condition, looking_for, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    print(f"Item {item} saved")

def get_all_listings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM listings")
    rows = cursor.fetchall()

    conn.close()
    return rows

init_db()
print(get_all_listings())
