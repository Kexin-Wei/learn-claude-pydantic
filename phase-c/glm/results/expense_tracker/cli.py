#!/usr/bin/env python3
"""Command-line interface for the expense tracker."""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
from typing import Optional

# Add parent directory to path to allow imports when running directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from expense_tracker.models import Expense
from expense_tracker.storage import ExpenseStore

# Default storage file path
DEFAULT_DATA_FILE = os.path.expanduser("~/.expenses.json")


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"${amount:.2f}"


def format_date(date_obj: date) -> str:
    """Format date for display."""
    return date_obj.isoformat()


def print_table(headers: list[str], rows: list[list[str]], title: str = "") -> None:
    """Print a simple formatted table.

    Args:
        headers: Column headers
        rows: Table rows
        title: Optional table title
    """
    if title:
        print(f"\n{title}")
        print("-" * len(title))

    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(cell))

    # Print header
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
    print(header_line)
    print("-" * len(header_line))

    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(w) for cell, w in zip(row, col_widths)))


def filter_expenses(expenses: list[Expense], category: Optional[str] = None, since: Optional[date] = None) -> list[Expense]:
    """Filter expenses by category and/or date.

    Args:
        expenses: List of expenses to filter
        category: Filter by category (case-insensitive)
        since: Filter by minimum date

    Returns:
        Filtered list of expenses
    """
    filtered = expenses

    if category:
        category_lower = category.lower()
        filtered = [e for e in filtered if e.category.lower() == category_lower]

    if since:
        filtered = [e for e in filtered if e.date >= since]

    return filtered


def cmd_add(args: argparse.Namespace, storage: ExpenseStore) -> int:
    """Add a new expense."""
    try:
        amount = float(args.amount)
        if amount <= 0:
            print("Error: Amount must be a positive number.", file=sys.stderr)
            return 1
    except ValueError:
        print(f"Error: Invalid amount '{args.amount}'. Must be a number.", file=sys.stderr)
        return 1

    if not args.category:
        print("Error: Category is required.", file=sys.stderr)
        return 1

    if not args.desc:
        print("Error: Description is required.", file=sys.stderr)
        return 1

    # Generate ID by finding max existing ID + 1
    expenses = storage.load()
    new_id = max([exp.id for exp in expenses], default=0) + 1

    expense = Expense(
        id=new_id,
        amount=amount,
        category=args.category,
        description=args.desc,
        date=date.today(),
    )

    success = storage.add_expense(expense)
    if success:
        print(f"Added expense: {format_currency(amount)} - {args.desc} ({args.category})")
        print(f"ID: {expense.id} | Date: {format_date(expense.date)}")
        return 0
    else:
        print("Error: Failed to add expense.", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace, storage: ExpenseStore) -> int:
    """List expenses with optional filters."""
    try:
        # Parse date if provided
        since_date = None
        if args.since:
            try:
                since_date = date.fromisoformat(args.since)
            except ValueError:
                print(f"Error: Invalid date format '{args.since}'. Use YYYY-MM-DD.", file=sys.stderr)
                return 1

        expenses = storage.load()

        # Apply filters
        expenses = filter_expenses(
            expenses,
            category=args.category,
            since=since_date,
        )

        if not expenses:
            print("No expenses found.")
            return 0

        # Sort by date descending
        expenses = sorted(expenses, key=lambda e: e.date, reverse=True)

        # Build table data
        headers = ["ID", "Date", "Category", "Description", "Amount"]
        rows = []
        for exp in expenses:
            rows.append([
                str(exp.id),
                format_date(exp.date),
                exp.category,
                exp.description,
                format_currency(exp.amount),
            ])

        title = "Expenses"
        if args.category:
            title += f" (Category: {args.category})"
        if since_date:
            title += f" (Since: {since_date.isoformat()})"

        print_table(headers, rows, title)

        # Print total
        total = sum(exp.amount for exp in expenses)
        print(f"\nTotal: {format_currency(total)}")

        return 0
    except json.JSONDecodeError as e:
        print(f"Error: Failed to read expenses file. Invalid JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_summary(args: argparse.Namespace, storage: ExpenseStore) -> int:
    """Print a summary of expenses by category."""
    try:
        expenses = storage.load()

        if not expenses:
            print("No expenses found.")
            return 0

        # Group by category
        category_totals: dict[str, float] = {}
        for exp in expenses:
            category_totals[exp.category] = (
                category_totals.get(exp.category, 0) + exp.amount
            )

        # Sort by amount descending
        sorted_categories = sorted(
            category_totals.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # Build table data
        headers = ["Category", "Total"]
        rows = [
            [cat, format_currency(total)]
            for cat, total in sorted_categories
        ]

        print_table(headers, rows, "Expense Summary by Category")

        # Print grand total
        grand_total = sum(category_totals.values())
        print(f"\nGrand Total: {format_currency(grand_total)}")

        return 0
    except json.JSONDecodeError as e:
        print(f"Error: Failed to read expenses file. Invalid JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_delete(args: argparse.Namespace, storage: ExpenseStore) -> int:
    """Delete an expense by ID."""
    try:
        expense_id = int(args.id)
    except ValueError:
        print(f"Error: Invalid ID '{args.id}'. Must be an integer.", file=sys.stderr)
        return 1

    # First, find the expense to show what's being deleted
    expense_to_delete = storage.get_expense(expense_id)

    if not expense_to_delete:
        print(f"Error: No expense found with ID {expense_id}.", file=sys.stderr)
        return 1

    deleted = storage.delete_expense(expense_id)

    if deleted:
        print(f"Deleted expense ID {expense_id}:")
        print(f"  {format_currency(expense_to_delete.amount)} - {expense_to_delete.description}")
        print(f"  Category: {expense_to_delete.category} | Date: {format_date(expense_to_delete.date)}")
        return 0
    else:
        print(f"Error: Failed to delete expense with ID {expense_id}.", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="expense-tracker",
        description="Track and manage your expenses from the command line.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add --amount 25.50 --category Food --desc "Lunch at cafe"
  %(prog)s list --category Food --since 2024-01-01
  %(prog)s summary
  %(prog)s delete 1
        """,
    )

    parser.add_argument(
        "--file",
        default=DEFAULT_DATA_FILE,
        help=f"Path to the expenses data file (default: {DEFAULT_DATA_FILE})",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        required=True,
    )

    # Add command
    add_parser = subparsers.add_parser(
        "add",
        help="Add a new expense",
        description="Add a new expense to the tracker.",
    )
    add_parser.add_argument(
        "--amount",
        required=True,
        help="The amount of the expense (e.g., 25.50)",
    )
    add_parser.add_argument(
        "--category",
        required=True,
        help="The category for the expense (e.g., Food, Transport, Entertainment)",
    )
    add_parser.add_argument(
        "--desc",
        required=True,
        help="A brief description of the expense",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List expenses",
        description="List all expenses with optional filters.",
    )
    list_parser.add_argument(
        "--category",
        help="Filter by category",
    )
    list_parser.add_argument(
        "--since",
        help="Filter by date (YYYY-MM-DD format)",
    )

    # Summary command
    summary_parser = subparsers.add_parser(
        "summary",
        help="Show expense summary by category",
        description="Display a summary of total expenses grouped by category.",
    )

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete an expense",
        description="Delete an expense by its ID.",
    )
    delete_parser.add_argument(
        "id",
        help="The ID of the expense to delete",
    )

    args = parser.parse_args()

    # Initialize storage
    try:
        storage = ExpenseStore(args.file)
    except Exception as e:
        print(f"Error: Failed to initialize storage: {e}", file=sys.stderr)
        return 1

    # Execute command
    command_handlers = {
        "add": cmd_add,
        "list": cmd_list,
        "summary": cmd_summary,
        "delete": cmd_delete,
    }

    handler = command_handlers.get(args.command)
    if not handler:
        print(f"Error: Unknown command '{args.command}'", file=sys.stderr)
        parser.print_help()
        return 1

    return handler(args, storage)


if __name__ == "__main__":
    sys.exit(main())
