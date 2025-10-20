# db.py

from __future__ import annotations
from pathlib import Path
import sqlite3
import logging

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL, -- ISO YYYY-MM-DD
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    note TEXT
);
"""

INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);",
    "CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);"
]

def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Open the connection with SQLite.

    Args:
        db_path: Path to the SQLIite database file.

    Returns:
        sqlite3.Connection: SQLite connection object.
    """
    path = str(db_path)
    
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception:
        logger.exception("Failed to connect to DB at %s", path)
        raise

def init_db(conn: sqlite3.Connection) -> None:
    """Create a basic schema and indexes.

    Args:
        conn: Active SQLite connection. 
    """
    try:
        cursor = conn.cursor()
        cursor.executescript(SCHEMA_SQL)
        for statement in INDEXES_SQL:
            cursor.execute(statement)
        conn.commit() 
        logger.info("Database schena created.")
        
    except Exception:
        logger.exception("init_db failed.")
        raise
    
    finally:
        try:
            cursor.close()
        except Exception:
            logger.warning("Failed to close the cursor in init_db")
        
