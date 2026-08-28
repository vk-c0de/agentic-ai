"""Authentication module for user login."""

import sqlite3
from pathlib import Path
from typing import TypedDict, Optional


class UserRecord(TypedDict):
    """User record from the database."""
    email: str
    full_name: str
    role: str


def authenticate_user(email: str, password: str, role: Optional[str] = None) -> Optional[UserRecord]:
    """
    Authenticate a user by email and password.
    
    Args:
        email: User email
        password: User password
        role: Optional role filter ('customer' or 'admin')
    
    Returns:
        UserRecord dict if credentials are valid, None otherwise
    """
    # Resolve database path
    root = Path(__file__).resolve().parents[2]
    db_path = root / "ecommerce.db"
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    query = "SELECT email, full_name, role FROM users WHERE email = ? AND password = ?"
    params = [email, password]
    
    if role:
        query += " AND role = ?"
        params.append(role)
    
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return UserRecord(
            email=row["email"],
            full_name=row["full_name"],
            role=row["role"]
        )
    
    return None
