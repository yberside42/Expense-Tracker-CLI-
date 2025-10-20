# cli.py

from __future__ import annotations
from pathlib import Path
import argparse
import json
import logging
import sys

from typing import Optional

from . import __version__
from .db import get_connection, init_db
from .validators import (validate_date_iso, validate_amount, validate_category, validate_id,)
from .services import list_expenses, add_expense, update_expense, delete_expense
from .renderers import (render_expenses_table, render_report_by_category, render_report_range)
from .reports import by_category, range_summary
from .exporters import export_to_csv, export_to_json
from .logger import logging_cfg


DEFAULT_DB = Path.cwd() / "expenses.db"

logger = logging.getLogger(__name__)

def err(msg: str) -> None:
    """Generate a normalized error message.

    Args:
        msg (str): Error message.
    """
    print(msg, file=sys.stderr)

def build_parser() -> argparse.ArgumentParser:
    """Parser of the Expense Tracker CLI.

    Returns:
        argparse.ArgumentParser: Configured parser with supported commands and options.
    """
    # Parser creation 
    parser = argparse.ArgumentParser(prog="expense_tracker", description="Expense Tracker CLI")
    parser.add_argument("--db", type=str, default=str(DEFAULT_DB), help="Path to the Database file")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--version", action="version", version=f"expense-tracker {__version__}")
    
    # Sub parser section
    sub = parser.add_subparsers(dest="command", required=True)
    
    sub.add_parser("init", help="Initialize database (tables and indexes)")
    
    # List subparser
    sub_list = sub.add_parser("list", help="List the expenses with filters")
    sub_list.add_argument("--from", dest="date_from", type=validate_date_iso, help="Start date. YYYY-MM-DD")
    sub_list.add_argument("--to", dest="date_to", type=validate_date_iso, help="End date. (YYY-MM-DD)")
    sub_list.add_argument("--category", type=str, help="Filter by category")
    sub_list.add_argument("--min", dest="min_amount", type=float, help="Min amount")
    sub_list.add_argument("--max", dest="max_amount", type=float, help="Max amount")
    sub_list.add_argument("--text", type=str, help="String to be search in note or category")
    sub_list.add_argument("--order-by", choices=["amount", "date", "category", "id"], help="Column to order by")
    sub_list.add_argument("--desc", action="store_true", help="Order by descending")
    sub_list.add_argument("--limit", type=int, help="Limit the number of rows")
    sub_list.add_argument("--offset", type=int, help="Offset for pagination")
    sub_list.add_argument("--format", choices=["table", "json"], default="table", help="Output format")

    # Add subparser
    sub_add = sub.add_parser("add", help="Add a new expense to the table")
    sub_add.add_argument("--date", required=True, type=validate_date_iso, help="YYYY-MM-DD")
    sub_add.add_argument("--category", required=True, type=validate_category, help="Category")
    sub_add.add_argument("--amount", required=True, type=validate_amount, help="Amount (> 0)")
    sub_add.add_argument("--note", required=False, type=str, help="Optional note")
    
    # Update subparser
    sub_update = sub.add_parser("update", help="Update an existing expense from the table")
    sub_update.add_argument("id", type=validate_id, help="Expense ID")
    sub_update.add_argument("--date", type=validate_date_iso, help="YYYY-MM-DD")
    sub_update.add_argument("--category", type=validate_category, help="Category")
    sub_update.add_argument("--amount", type=validate_amount, help="Amount (> 0)")
    sub_update.add_argument("--note", type=str, help="Note")
    
    # Delete subparser
    sub_delete = sub.add_parser("delete", help="Delete an expense by ID")
    sub_delete.add_argument("id", type=validate_id, help="Expense ID")
    sub_delete.add_argument("--yes", action="store_true", help="Confirm deletion")
    
    # Report (category and range)
    sub_report = sub.add_parser("report", help="Reports")
    report = sub_report.add_subparsers(dest="report_cmd", required=True)
    
    # Report Category subparser
    sub_report_cat = report.add_parser("category", help="Aggregate by category")
    sub_report_cat.add_argument("--from", dest="date_from", type=validate_date_iso, help="Start date. YYYY-MM-DD")
    sub_report_cat.add_argument("--to", dest="date_to", type=validate_date_iso, help="End date. YYYY-MM-DD")
    sub_report_cat.add_argument("--min", dest="min_amount", type=float, help="Min amount")
    sub_report_cat.add_argument("--max", dest="max_amount", type=float, help="Max amount")
    sub_report_cat.add_argument("--text", type=str, help="String to be search in note or category")
    sub_report_cat.add_argument("--top", type=int, help="Show only the top categories")
    sub_report_cat.add_argument("--format", choices=["table","json"], default="table", help="Format")
    
    # Report Range subparser
    sub_report_range = report.add_parser("range", help="Summary for a date range")
    sub_report_range.add_argument("--from", dest="date_from", type=validate_date_iso, help="Start date. YYYY-MM-DD")
    sub_report_range.add_argument("--to", dest="date_to", type=validate_date_iso, help="End date. YYYY-MM-DD")
    sub_report_range.add_argument("--min", dest="min_amount", type=float, help="Min amount")
    sub_report_range.add_argument("--max", dest="max_amount", type=float, help="Max amount")
    sub_report_range.add_argument("--text", type=str, help="String to be search in note or category")
    sub_report_range.add_argument("--format", choices=["table","json"], default="table", help="Format")
    
    # Export subparser
    sub_export = sub.add_parser("export", help="Export expenses to CSV or JSON files")
    sub_export.add_argument("--format", required=True, choices=["csv", "json"], help="Export format")
    sub_export.add_argument("--dest", required=True, type=str, help="Destination path")
    sub_export.add_argument("--from", dest="date_from", type=validate_date_iso, help="Start date. YYYY-MM-DD")
    sub_export.add_argument("--to", dest="date_to", type=validate_date_iso, help="Start date. YYYY-MM-DD")
    sub_export.add_argument("--category", type=str, help="Filter by category")
    sub_export.add_argument("--min", dest="min_amount", type=float, help="Min amount")
    sub_export.add_argument("--max", dest="max_amount", type=float, help="Max amount")
    sub_export.add_argument("--text", type=str, help="String to be search in note or category")
    sub_export.add_argument("--order-by", choices=["amount", "date", "category", "id"], help="Column to order by")
    sub_export.add_argument("--desc", action="store_true", help="Order descending")
    sub_export.add_argument("--limit", type=int, help="Limit number of rows")
    sub_export.add_argument("--offset", type=int, help="Offset for pagination")
    sub_export.add_argument("--fields", type=str, help="fields (comma-separated)")
    sub_export.add_argument("--force", action="store_true", help="Overwrite destination file if it exists")
    sub_export.add_argument("--pretty", action="store_true", help="Pretty JSON format")
    
    return parser

def cmd_init(db_path: str, logger) -> int:
    """Executes the command 'init' to initialize the database

    Args:
        db_path: Path to the SQLite database.

    Returns:
        int: Exit Code. 
    """
    try:
        
        conn = get_connection(db_path)
        try:
            init_db(conn)
        finally:
            conn.close()
        print(f"Database initialized at: {db_path}")
        logger.info("DB initialized at %s", db_path)
        return 0
    except Exception as e:
        err(f"init failure: {e}")
        logger.exception("init failed")
        return 2

def cmd_list(args, db_path: str) -> int:
    """Executes the command 'list', querying expenses from the db based on filters and outputs the result in the right format.

    Args:
        args: Parsed CLI arguments.
        db_path: Path to the SQLite database.

    Returns:
        int: Exit Code.
    """
    conn = None 
    try: 
        conn = get_connection(db_path)
    
        # Ordering the list
        rows = list_expenses(
                conn,
                date_from = args.date_from,
                date_to = args.date_to,
                category = args.category.strip() if args.category else None,
                min_amount = args.min_amount,
                max_amount = args.max_amount,
                text = args.text,
                order_by = args.order_by,
                desc = bool(args.desc),
                limit = args.limit,
                offset = args.offset,
        )
        
        # logger output 
        if not rows:
            logger.warning("No expenses found to execute the 'list' command.")
        else:
            logger.info("Listed %d expenses from %s", len(rows), db_path)
        
        # User Output
        if args.format == "json":
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print(render_expenses_table(rows))
        return 0
    
    except Exception as e:
        err(f"cmd_list failed: {e}")
        logger.exception("list failed.")
        return 1

    finally:
        if conn:
            conn.close() 

def cmd_add(args, db_path: str) -> int:
    """Executes the command 'add', add a new expense. 

    Args:
        args: Parsed CLI arguments. 
        db_path: Path to the SQLite database.

    Returns:
        int: Exit Code.
    """
    conn = None
    
    try:
        conn = get_connection(db_path)
    
        # New expense format
        new_id = add_expense(
            conn, 
            date=args.date, 
            category=args.category, 
            amount=args.amount, 
            note=args.note,
        )
        logger.info("Expense added succesfuly: (ID = %s, category=%s, amount=%s)",
                    new_id, args.category, args.amount)
        print(f"Expense added. ID = {new_id}")
        return 0
    
    except Exception as e:
        err(f"cmd_add failed: {e}")
        logger.exception("add failed.")
    
    finally:
        if conn:
            conn.close()
    
def cmd_update(args, db_path: str) -> int:
    """Executes the command 'update'. Update the fields of an existing expense.

    Args:
        args: Parsed CLI arguments. 
        db_path: Path to the SQLite database.

    Returns:
        int: Exit Code
    """
    # Checking that there's at least 1 field to update.
    if all(value is None for value in (args.date, args.category, args.amount, args.note)):
        print("There is no fields to be updated. One field is required at least.")
        logger.warning("cmd_update called with nothing to update: (id=%s)", args.id)
        return 2

    conn = None
    
    # Format
    try:
        conn = get_connection(db_path)
        
        rows = update_expense(
            conn, 
            args.id, 
            args.date, 
            args.category, 
            args.amount, 
            args.note)
    
        # Format printing alternatives
        if rows == 0: 
            logger.warning("No expense found to update: (id=%s)", args.id)
            print("There is no expense that match.")
        else:
            logger.info("Updated %d row(s): (id=%s)", rows, args.id)
            print(f"Updated {rows} row(s).")
        return 0
    
    except Exception as e:
        err(f"cmd_update failed: {e}")
        logger.exception("update failed.")

    finally:
        if conn:
            conn.close()

def cmd_delete(args, db_path: str) -> int:
    """Executes the command 'delete'. Delete an expense using an ID.

    Args:
        args: Parsed CLI arguments. 
        db_path: Path to the SQLite database.

    Returns:
        int: Exit Code
    """
    # Verification to prevent accidental deletes.
    if not args.yes:
        print("--yes is requiered to delete.")
        logger.warning("cmd_delete called without confirmation (--yes): (id=%s)", args.id)
        return 2
    
    conn = None
    
    try:
        conn = get_connection(db_path)
        rows = delete_expense(conn, args.id)
        
        # Checks if there's anything to delete
        if rows == 0:
            logger.warning("No expense found to delete: (id=%s)", args.id)
            print("There is no expense that match.")
        else:
            logger.info("Deleted %d row(s): (id=%s)", rows, args.id)
            print(f"Deleted {rows} row(s).")
        return 0
    
    except Exception as e:
        err(f"cmd_delete failed: {e}")
        logger.exception("delete failed.")

    finally:
        if conn:
            conn.close()

def cmd_report_category(args, db_path: str) -> int:
    """Executes the command 'report category'; render the output and print it.

    Args:
        args: Parsed CLI arguments. 
        db_path: Path to the SQLite database.

    Returns:
        int: Exit code.
    """
    conn = None
    
    # Format
    try:
        conn = get_connection(db_path)
        rows = by_category(
            conn,
            date_from = args.date_from,
            date_to = args.date_to,
            min_amount = args.min_amount,
            max_amount = args.max_amount,
            text = args.text,
        )
        
        # Checking types and positives
        if args.top is not None:
            if args.top > 0:
                print("--top must be a positive integer.")
                logger.warning("")
                return 2
            rows = rows[: args.top]
        
        if not rows:
            logger.warning("Report by category returned nothing")
        else:
            logger.info("Report by category generated with %d rows", len(rows))
        
        # User output
        if args.format == 'json':
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print(render_report_by_category(rows))
        return 0
    
    except Exception as e:
        err(f"cmd_report_category failed: {e}")
        logger.exception("report by category failed.")
        return 1

    finally:
        if conn:
            conn.close()

def cmd_report_range(args, db_path: str) -> int:
    """Executes the command 'report range'; render the output and print it.

    Args:
        args: Parsed CLI arguments. 
        db_path: Path to the SQLite database.

    Returns:
        int: Exit code.
    """
    conn = None

    # Format 
    try:
        conn = get_connection(db_path)
        summary = range_summary(
            conn,
            date_from = args.date_from,
            date_to = args.date_to,
            min_amount = args.min_amount,
            max_amount = args.max_amount,
            text = args.text,
        )
        
        if not summary:
            logger.warning("Report by range of dates returned nothing.")
        else:
            total = summary.get("total_amount") if isinstance(summary, dict) else None
            count = summary.get("count") if isinstance(summary, dict) else None
            logger.info("Report range generated: (count=%s), total=%s, from=%s, to=%s",
                        count, total, args.date_from, args.date_to)

        # User Output
        if args.format == 'json':
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(render_report_range(summary))
        return 0
    
    except Exception as e:
        err(f"cmd_report_range failed: {e}")
        logger.exception("report by range failed.")
        return 1

    finally:
        if conn:
            conn.close()

def cmd_export(args, db_path: str) -> int:
    """Executes the command 'export'; export the selected data into a CSV or JSON file.

    Args:
        args: Parsed CLI arguments. 
        db_path: Path to the SQLite database.

    Returns:
        int: Exit code.
    """
    allowed_fields = ["id", "date", "category", "amount", "note"]
    
    # Checking the fields
    if args.fields:
        fields = [f.strip() for f in args.fields.split(",") if f.strip()]
        if not fields:
            print("fields can't be empty.")
            logger.warning("Empty --fields argument received.")
            return 2
    else:
        fields = allowed_fields[:]
    
    # Validating the fields
    unknown = [field for field in fields if field not in allowed_fields]
    if unknown:
        print(f"Unknown field detected: {', '.join(unknown)}")
        logger.warning("Unknown export fields: %s", unknown)
        return 2 
    
    conn = None
    
    # Format
    try:
        conn = get_connection(db_path)
        rows = list_expenses(
            conn,
            date_from = args.date_from,
            date_to = args.date_to,
            category = (args.category.strip() if args.category else None),
            min_amount = args.min_amount,
            max_amount = args.max_amount,
            text = args.text,
            order_by = args.order_by,
            desc = bool(args.desc),
            limit = args.limit,
            offset = args.offset,
        )
        
        # If the user wants less of the allowed fields
        if fields != allowed_fields:
            rows = [{key: r.get(key) for key in fields} for r in rows]
        
        # In case the user use --pretty in CSV
        if args.format == "csv" and args.pretty:
            print("Warning: --pretty is ignores in CSV files") 
            logger.warning("--pretty ignored for CSV format")
        
        # Exporting the data
       
        # CSV format
        if args.format == "csv":
            export_to_csv(rows, dest=args.dest,
                          columns=fields,
                          overwrite=bool(args.force))
        # JSON format
        else:
            export_to_json(rows, dest=args.dest,
                          overwrite=bool(args.force),
                          pretty=bool(args.pretty)) 
    
        # logs and User Ouput
        if not rows:
                logger.warning("Export completed: (dest=%s, format=%s)", args.dest, args.format)
        else:
                logger.info("Exported %d row(s) to %s (format=%s)", len(rows), args.dest, args.format)
    
        print(f"Exported {len(rows)} row(s) to {args.dest}")
        return 0 
    
    except FileExistsError:
        logger.warning("Destination already exists and --force not provided: (dest=%s)", args.dest)
        print(f"The file {args.dest} already exists. If you want to overwrite, use --force")
        return 2

    except OSError as e:
        logger.exception("I/O error writing export: (dest=%s)", args.dest)
        print(f"I/O error writing to {args.dest}: {e}")
        return 2
    
    except Exception as e:
        err(f"cmd_export failed: {e}")
        logger.exception("export failed.")
        return 1

    finally:
        if conn:
            conn.close()

def main(argv: list[str] | None = None) -> int:
    """Entry point for the Expense Tracker CLI. 

    Args:
        argv (list[str] | None): List of command-line arguments. Defaults to None.

    Returns:
        int: Exit Code.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    db_path = args.db
    logger = logging_cfg(debug=bool(args.debug))
    
    
    # Knowing which command to apply.
    try: 
        if args.command == "init":
            return cmd_init(db_path, logger)
        elif args.command == "list":
            return cmd_list(args, db_path)
        elif args.command == "add":
            return cmd_add(args, db_path)
        elif args.command == "update":
            return cmd_update(args, db_path)
        elif args.command == "delete":
            return cmd_delete(args, db_path)
        elif args.command == "export":
            return cmd_export(args, db_path)
    
    # command 'report' alternatives (category or range)
        if args.command == "report":
            if args.report_cmd == "category":
                return cmd_report_category(args, db_path)
            elif args.report_cmd == "range":
                return cmd_report_range(args, db_path)
    except Exception as e:
        err(f"FATAL ERROR: {e}")
        logger = logging_cfg(debug=True)
        logger.exception("Fatal error")
        return 2

    # In case an unknown command is used
    parser.error("Unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
