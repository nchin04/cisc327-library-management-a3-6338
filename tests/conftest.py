import pytest
import sqlite3
import os

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create a fresh test database before any tests run."""
    db_path = "library.db"

    # Remove any old DB to start clean
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create a new SQLite database and required tables
    conn = sqlite3.connect(db_path)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT,
        isbn TEXT,
        total_copies INTEGER,
        available_copies INTEGER
    );
    CREATE TABLE IF NOT EXISTS borrow_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patron_id TEXT,
        book_id INTEGER,
        borrow_date TEXT,
        due_date TEXT,
        return_date TEXT
    );
    """)
    conn.close()

    print("\n✅ Test database setup complete")

    yield  # Run all tests

    # Optional teardown after tests
    if os.path.exists(db_path):
        os.remove(db_path)
        print("\n🧹 Test database removed")