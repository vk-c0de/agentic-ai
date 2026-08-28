"""Database initialization module for the ecommerce database."""

import sqlite3
from pathlib import Path


def init_database():
    """Initialize the ecommerce database from SQL seed file."""
    # Resolve paths
    root = Path(__file__).resolve().parents[2]
    db_path = root / "ecommerce.db"
    sql_seed_path = root / "ecommerce_setup.sql"
    
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read SQL seed file
    with open(sql_seed_path, "r", encoding="utf-8") as f:
        sql_script = f.read()
    
    # Connect and execute
    conn = sqlite3.connect(str(db_path))
    conn.executescript(sql_script)
    conn.commit()
    conn.close()
    
    return db_path


def main():
    """CLI entry point to initialize the database."""
    db_path = init_database()
    print(f"✅ Database initialized at: {db_path}")


if __name__ == "__main__":
    main()
