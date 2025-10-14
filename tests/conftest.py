import os
import sys
import pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database import get_db_connection


@pytest.fixture(autouse=True)
def reset_database():
    """
    Automatically runs before each test.
    It deletes and recreates the library.db file to ensure a clean slate.
    """
    db_path = "library.db"


    if os.path.exists(db_path):
        os.remove(db_path)


    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            total_copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS borrow_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patron_id TEXT NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TEXT,
            due_date TEXT,
            return_date TEXT,
            FOREIGN KEY(book_id) REFERENCES books(id)
        );
    """)

    conn.commit()
    conn.close()

  
    yield

    if os.path.exists(db_path):
        os.remove(db_path)