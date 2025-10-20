# services.py 

from __future__ import annotations
from typing import Any, Dict, List, Optional
import sqlite3

VALID_ORDER_BY = {"amount", "date", "category", "id"}

def list_expenses(conn: sqlite3.Connection, 
                  *,
                  date_from: Optional[str] = None,
                  date_to: Optional[str] = None,
                  category: Optional[str] = None,
                  min_amount: Optional[float] = None,
                  max_amount: Optional[float] = None,
                  text: Optional[str] = None,
                  order_by: Optional[str] = None,
                  desc: bool = False,
                  limit: Optional[int] = None,
                  offset: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Returns a list of expense records optionally filtered, sorted and paginated.
    
    Every row is a dictionary with the same format: 
    {"id": int, "date": str, "category": str, "amount": float, "note": str|None}

    Filters (Optional):
        - date_from / date_to (inclusive): Filter by a date range (ISO format: YYYY-MM-DD)
        - category: Exact match on the category name .
        - min_amount / max_amount: Filter by amount range.
        - text: String search on note or category.
        
    Ordering: 
        - order_by: Sorting by either one of: (amount, date, category or ID).
        - desc: Descending if True, ascending if False.
        - limit: Number of maximum results. 
        - offset: Number of records to skip (most be a non-negative integer).

    Args:
        conn: Active SQLite connection.
        date_from (optional): Start date (ISO Format). 
        date_to (optional): End date (ISO Format). 
        category (optional): Category to filter by.
        min_amount (optional): Min amount to filter by. 
        max_amount (optional): Max amount to filter by.
        text (optional): Substring to search in category or note.
        order_by (optional): Order preference of a column.
        desc (optional): Descending order instruction.
        limit (optional): Max number of rows that are showdd. 
        offset (optional): Starting offset.

    Returns:
        List: List of the expenses normalized using the indications.
    """
    where = []
    parameters: List[Any] = []
    
    # Filters (Totally optional)
    if date_from is not None:
        where.append("date >= ?")
        parameters.append(date_from)
    if date_to is not None:
        where.append("date <= ?")
        parameters.append(date_to)
    if category is not None:
        where.append("category = ?")
        parameters.append(category)
    if min_amount is not None:
        where.append("amount >= ?")
        parameters.append(min_amount)
    if max_amount is not None:
        where.append("amount <= ?")
        parameters.append(max_amount)
    if text:
        where.append("(note LIKE ? OR category LIKE ?)")
        like = f"%{text}%"
        parameters.extend([like, like])
    
    sql = "SELECT id, date, category, amount, note FROM expenses"
    # Applying the filters if there are any.
    if where:
        sql += " WHERE " + " AND ".join(where)
    # Ordering the expenses (if the user wants it)
    if order_by:
        if order_by not in VALID_ORDER_BY:
            raise ValueError(f"Invalid order_by: {order_by!r}")
        sql += f" ORDER BY {order_by} {'DESC' if desc else 'ASC'}"
    # Limiting the amount of rows to be showed (optional)
    if limit is not None:
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("limit must be a positive integer.")
        sql += " LIMIT ?"
        parameters.append(limit)
        if offset is not None:
            if not isinstance(offset, int) or offset < 0:
                raise ValueError("offset must be an non negative integer.")
            sql += " OFFSET ?"
            parameters.append(offset)
            
    cursor = conn.cursor()
    cursor.execute(sql, parameters)
    rows = cursor.fetchall()
    
    return [
        {
            "id": int(r["id"]),
            "date": str(r["date"]),
            "category": str(r["category"]),
            "amount": float(r["amount"]),
            "note": (r["note"] if r["note"] is not None else None),
        }
        for r in rows
    ]
            
def add_expense(conn: sqlite3.Connection, *,
                date: str,
                category: str,
                amount: float,
                note: str | None = None,
) -> int:
    """Add a new expense in the 'expenses' table. 

    Args:
        conn: Active SQLite connection.
        date: Expense date.
        category: Expense category.
        amount: Expense amount.
        note (optional): Optional note to label the expense.

    Returns:
        int: Inserted row ID. 
    """
    cursor = conn.execute("INSERT INTO expenses (date, category, amount, note) VALUES (?,?,?,?)", 
                          (date, category, amount, note),)
    conn.commit()
    return int(cursor.lastrowid)

def update_expense(conn: sqlite3.Connection, expense_id: int, *,
                   date: str | None = None,
                   category: str | None = None,
                   amount: float | None = None,
                   note: str | None = None,
) -> int:
    """Update fields of an existing expense by ID. 

    Args:
        conn: Active SQLite connection.
        expense_id : Expense ID.
        date, category, amount, note: Optional fields to update.

    Returns:
        int: Number of rows updated. 
    """
    updates: list[str] = []
    parameters: list[Any] = []
    
    # Checking which fields are been updated.
    if date is not None:
        updates.append("date=?")
        parameters.append(date)
        
    if category is not None:
        updates.append("category=?")
        parameters.append(category)
        
    if amount is not None:
        updates.append("amount=?")
        parameters.append(amount)
        
    if note is not None:
        updates.append("note=?")
        parameters.append(note)
    
    # If non of the fields are been updated, the action is canceled.
    if not updates:
        return 0
    
    # Identification of which ID is going to get the changes.
    parameters.append(expense_id)
    sql = f"UPDATE expenses SET {', '.join(updates)} WHERE id=?"
    cursor = conn.execute(sql, parameters)
    conn.commit()
    return int(cursor.rowcount)

def delete_expense(conn: sqlite3.Connection, expense_id: int) -> int:
    """Delete an expense from 'expenses' table by ID.

    Args:
        conn: Active SQLite connection.
        expense_id: Expense ID.

    Returns:
        int: Number of rows deleted. 
    """
    # Identification of which ID is going to get deleted
    cursor = conn.execute("DELETE FROM expenses WHERE id=?", 
                          (expense_id,))
    conn.commit()
    return int(cursor.rowcount)    
        
