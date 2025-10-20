# Expense Tracker CLI

Command-Line version of an expense tracker. Built with Python, featuring modular design, reporting and export options.

---

## Technologies & Requirements
- Python 3.10+
- SQLite3
- argparse
- logging

## Features

- Initialize and manage an SQLite database of expenses.
- Add new expenses with date, category, amount and an optional note.
- Update / Delete existing expenses using ID (Deletion requires confirmation)
- List expenses with filters:
    - Category, amount range, date range
    - Text search (category or note)
    - Ordering and Pagination
    - Output as a table or JSON
- Reports:
    - By category (totals, count, percentage of total)
    - By date range (total, count, average)
- Exports filtered expenses to CSV or JSON:
    - Select Fields (id, date, category, amount, note)
    - Overwrite existing files with --force
    - Pretty print JSON with --pretty
- Action logging for all the operations.
- Error handling and validations (date format, positive amounts, non-empty category, valid IDs).

## Structure

The project has 9 files:

- "__init__.py": Define the version of the app. 
- "cli.py": Entry point and command parser (argparse).
- "db.py": Handles SQLite connection and database operations.  
- "validators.py": Contains all input validation functions. 
- "services.py": Core business logic (add, edit, delete, search expenses).  
- "renderers.py": Renders tables and formatted reports for the CLI output.  
- "reports.py": Builds reports by category, totals and date ranges.
- "exporters.py": Functions to export data to CSV or JSON.  
- "logger.py": Configures logging and registers all actions.  

---

## Usage

Run the CLI as a module from the project folder:

```bash
cd expense_tracker
python -m expense_tracker.cli --help
```

Global Options:
--db PATH: SQLite database file.
--debug: Enable debug logging.
--version: Show Current Version.
--help: Show help

Commands:

- init: Initialize the database
python -m expense_tracker.cli init

- add: Add a new expense, date category and amount are required
python -m expense_tracker.cli add --date 2025-10-01 --category Food --amount 100 --note "Lunch"

- list: List all the expenses with filters
python -m expense_tracker.cli list --category Food --from 2025-09-01 --to 2025-09-30 --order-by date --desc --limit 10 --format table

- update: Update certain fields of an existing expense
python -m expense_tracker.cli update 3 --amount 120 --note "Corrected"

- delete: Delete an expense by ID, confirmation is required
python -m expense_tracker.cli delete 3 --yes

- report category: Adds totals by category
python -m expense_tracker.cli report category --from 2025-09-01 --to 2025-09-30 --top 5 --format table

- report range: Summary of the expenses between dates, requires from and to
python -m expense_tracker.cli report range --from 2025-09-01 --to 2025-09-30 --format table

- export: Export data to CSV or JSON
python -m expense_tracker.cli export --format csv --dest exports/expenses.csv --from 2025-09-01 --to 2025-09-30 --fields id,date,category,amount,note --force

Output:

- Table (default):
-   List: ID, Date, Category, Amount, Note
-   Report by category: Category, Total, Count, %
-   Report range: 3 lines → Total, Count, Average

- JSON:
-   List → array of objects with keys id, date, category, amount, note
-   Report category → array of objects with keys category, total, count, pct_total
-   Report range → object {total, count, avg}

---

## Learned:

- Learned to implement CLI, argparse and more complex SQLite instructions.
- Learned database persistence with SQLite.
- Practiced error handling and logging.
- Learned validations for the first time.
- Improved the export options, featuring CSV and JSON.
- Learned to build simple tests.
- Learned project organization at a larger scale.
- Learned to generate data and then render it. 

---

## License 
This project is licensed under the [MIT License](LICENSE)
© 2025 Yael Tapia.
