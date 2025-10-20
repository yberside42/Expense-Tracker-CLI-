# reports.py

from __future__ import annotations
from typing import Any, Dict, List, Optional
import sqlite3

def where_builder_category(params: Dict[str, Any]) -> tuple[List[str], List[Any]]:
    """Builds a WHERE clause from the filters dictionary.

    Args:
        params: Filters.

    Returns:
        where, parameters (tuple[List[str], List[Any]]): A tuple of two lists: the WHERE clauses and the parameters.
    """
    where = []
    parameters = []
    
    # Knowing which WHERE are going to be added (all can be added at the same time)
    if params.get("date_from") is not None:
        where.append("date >= ?")
        parameters.append(params["date_from"])
        
    if params.get("date_to") is not None:
        where.append("date <= ?")
        parameters.append(params["date_to"])
        
    if params.get("min_amount") is not None:
        where.append("amount >= ?")
        parameters.append(params["min_amount"])
        
    if params.get("max_amount") is not None:
        where.append("amount <= ?")
        parameters.append(params["max_amount"])
    
    text = params.get("text")
    if text:
        like = f"%{text}%"
        where.append("(note LIKE ? OR category LIKE ?)")
        parameters.extend([like, like])
        
    return where, parameters

def where_builder_range(*,
                  date_from: Optional[str] = None,
                  date_to: Optional[str] = None,
                  min_amount: Optional[float] = None,
                  max_amount: Optional[float] = None,
                  text: Optional[str] = None,
) -> tuple[list[str], list[Any]]:
    """Builds a WHERE clause to filter the range summary.

    Args:
        date_from: Start date. 
        date_to: End date. 
        min_amount (optional): Min amount of the expense.
        max_amount (optional): Max amount of the expense.
        text (optional): Text to label note or category.

    Returns:
        tuple[list[str], list[Any]]:  A tuple of two lists: the WHERE clauses and the parameters.
    """
    where = ["date BETWEEN ? AND ?"]
    parameters = [date_from, date_to]
    
    # WHERE filteres 
    if min_amount is not None:
        where.append("amount >= ?")
        parameters.append(min_amount)
        
    if max_amount is not None:
        where.append("amount <= ?")
        parameters.append(max_amount)
    
    if text:
        like = f"%{text}%"
        where.append("(note LIKE ? OR category LIKE ?)")
        parameters.extend([like, like])
    
    return where, parameters
    
def by_category(conn: sqlite3.Connection, 
                  *,
                  date_from: Optional[str] = None,
                  date_to: Optional[str] = None,
                  min_amount: Optional[float] = None,
                  max_amount: Optional[float] = None,
                  text: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """SQL query to aggregate expenses using optional filters.

    Args:
        conn: Active connection with SQLite.
        date_from (optional): Start date.
        date_to (optional): End date.
        min_amount (optional): Min amount.
        max_amount (optional): Max amount.
        text (optional): Text to label note or category.

    Returns:
        List[Dict[str, Any]]: List of aggregated rows. 
    """
    # SQL with optional WHERE filters 
    where, parameters =  where_builder_category(locals())
    sql = "SELECT category, SUM(amount) AS total, COUNT(*) AS count FROM expenses"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " GROUP BY category ORDER BY total DESC"
    
    # SQL connection 
    cursor = conn.cursor()
    cursor.execute(sql, parameters)
    rows = cursor.fetchall()
    
    if not rows:
        return []
    
    # Percentages
    total_global = sum(float(row["total"]) for row in rows if row["total"] is not None)
    if total_global == 0:
        return []
    
    # Format
    result = []
    for row in rows:
        total = float(row["total"] or 0.0)
        count = int(row["count"] or 0)
        percentage = (total / total_global) * 100.0 if total_global else 0.0
        result.append({
            "category": str(row["category"]),
            "total": total,
            "count": count,
            "pct_total": percentage,   
        })
    return result
        
    
def range_summary(conn: sqlite3.Connection, 
                  *,
                  date_from: str,
                  date_to: str,
                  min_amount: Optional[float] = None,
                  max_amount: Optional[float] = None,
                  text: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Return total, average and count for an expense within a date range.

    Args:
        conn (sqlite3.Connection): Active connection with SQLite.
        date_from (str): Start date (obligatory).
        date_to (str): End date (obligatory)
        min_amount (Optional[float], optional): Min amount of the expense.
        max_amount (Optional[float], optional): Max amount of the expense.
        text (Optional[str], optional): Text to label note or category.

    Returns:
        Optional[Dict[str, Any]]: Dictionary with total, count and average values.
    """
    where, parameters = where_builder_range(date_from =date_from, date_to=date_to,
                                            min_amount=min_amount, max_amount=max_amount,
                                            text=text,)
    # SQL Query
    sql = ("SELECT SUM(amount) AS total, COUNT(*) AS count, AVG(amount) AS avg "
    "FROM expenses WHERE " + " AND ".join(where)
    )
    
    # SQL connection
    cursor = conn.cursor()
    cursor.execute(sql, parameters)
    row = cursor.fetchone()
    
    if row is None or int(row["count"]) == 0:
        return None
    
    return {
        "total": float(row["total"] or 0.0),
        "count": int(row["count"]),
        "avg": float(row["avg"] or 0.0),
    }
          
    
