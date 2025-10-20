# renderers.py 

from __future__ import annotations
from typing import Dict, List

def render_expenses_table(rows: List[Dict]) -> str: 
    """Render a readable expenses table. 

    Args:
        rows (List[Dict]): Normalized expense rows.

    Returns:
        str: Good-looking printed table. 
    """
    # Checking if there is a table to render
    if not rows:
        return "No expenses to display."
    
    # Format
    header = f"{'ID':<5} {'Date':<12} {'Category':<15} {'Amount':>12}  Note"
    line = "-" * len(header)
    out_lines = [header, line]
    
    for r in rows:
        out_lines.append(
            f"{r['id']:<5} {r['date']:<12} {r['category']:<15} {r['amount']:>12.2f}  {r['note'] or ''}"
        )
    return "\n".join(out_lines)

def render_report_by_category(rows: List[Dict[str, Any]]) -> str:
    """Render a readable table for the category aggregates.

    Args:
        rows (List[Dict]): Normalized expense rows

    Returns:
        str: Good-looking printed table. 
    """
    # Checking if there is a table to render
    if not rows:
        return "No data to report."
    
    # Format
    header = f"{'Category':<20} {'Total':>12} {'Count':>7} {'%':>6}"
    line = "-" * len(header)
    out_lines = [header, line]

    for r in rows:
        out_lines.append(
            f"{str(r['category']):<20} "
            f"{float(r['total']):>12.2f} "
            f"{int(r['count']):>7d} "
            f"{float(r['pct_total']):>6.1f}"
        )
    
    return "\n".join(out_lines)

def render_report_range(summary: Dict | None) -> str:
    """Render a readable summary with total, count and average within a date range.

    Args:
        summary (Dict | None): Dictionary with total, count and average values.

    Returns:
        str: Good-looking printed summary
    """
    # Checking if there are data to render
    if summary is None:
        return "No data to report within the given range"
    
    return (
        f"Total:   {float(summary['total']):.2f}\n"
        f"Count:   {int(summary['count'])}\n"
        f"Average: {float(summary['avg']):.2f}"
    )

