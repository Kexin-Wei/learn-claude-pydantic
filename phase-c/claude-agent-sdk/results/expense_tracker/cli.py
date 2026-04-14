import argparse
import os
import sys

# Ensure the parent directory is on sys.path so `expense_tracker` is importable
# when running as `python expense_tracker/cli.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expense_tracker.models import Expense
from expense_tracker.storage import ExpenseStore


def cmd_add(args, store: ExpenseStore) -> None:
    try:
        amount = float(args.amount)
    except ValueError:
        print(f"Error: '{args.amount}' is not a valid amount.")
        return
    if amount <= 0:
        print("Error: amount must be a positive number.")
        return

    expense = Expense(amount=amount, category=args.category, description=args.desc)
    store.add(expense)
    print(f"Added expense {expense.id}: ${amount:.2f} [{expense.category}] {expense.description}")


def cmd_list(args, store: ExpenseStore) -> None:
    expenses = store.list_all(category=args.category, since=args.since)
    if not expenses:
        print("No expenses found.")
        return

    hdr_id, hdr_date, hdr_cat, hdr_amt, hdr_desc = "ID", "Date", "Category", "Amount", "Description"
    w_id = max(len(hdr_id), *(len(e.id) for e in expenses))
    w_date = max(len(hdr_date), *(len(e.date) for e in expenses))
    w_cat = max(len(hdr_cat), *(len(e.category) for e in expenses))
    w_amt = max(len(hdr_amt), *(len(f"${e.amount:.2f}") for e in expenses))
    w_desc = max(len(hdr_desc), *(len(e.description) for e in expenses))

    header = f"{hdr_id:<{w_id}}  {hdr_date:<{w_date}}  {hdr_cat:<{w_cat}}  {hdr_amt:>{w_amt}}  {hdr_desc}"
    sep = "-" * len(header)
    print(header)
    print(sep)
    for e in expenses:
        amt_str = f"${e.amount:.2f}"
        print(f"{e.id:<{w_id}}  {e.date:<{w_date}}  {e.category:<{w_cat}}  {amt_str:>{w_amt}}  {e.description}")


def cmd_summary(args, store: ExpenseStore) -> None:
    totals = store.summary()
    if not totals:
        print("No expenses recorded.")
        return

    w_cat = max(len("Category"), *(len(c) for c in totals))
    w_amt = max(len("Total"), *(len(f"${v:.2f}") for v in totals.values()))
    grand_total = sum(totals.values())
    w_amt = max(w_amt, len(f"${grand_total:.2f}"))

    header = f"{'Category':<{w_cat}}  {'Total':>{w_amt}}"
    sep = "-" * len(header)
    print(header)
    print(sep)
    for cat, total in sorted(totals.items()):
        print(f"{cat:<{w_cat}}  ${total:>{w_amt - 1}.2f}")
    print(sep)
    print(f"{'TOTAL':<{w_cat}}  ${grand_total:>{w_amt - 1}.2f}")


def cmd_delete(args, store: ExpenseStore) -> None:
    if store.delete(args.id):
        print(f"Deleted expense {args.id}.")
    else:
        print(f"Error: no expense found with id '{args.id}'.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Expense Tracker CLI")
    subparsers = parser.add_subparsers(dest="command")

    p_add = subparsers.add_parser("add", help="Add a new expense")
    p_add.add_argument("--amount", required=True, help="Expense amount")
    p_add.add_argument("--category", required=True, help="Expense category")
    p_add.add_argument("--desc", required=True, help="Expense description")

    p_list = subparsers.add_parser("list", help="List expenses")
    p_list.add_argument("--category", default=None, help="Filter by category")
    p_list.add_argument("--since", default=None, help="Filter by date (YYYY-MM-DD)")

    subparsers.add_parser("summary", help="Show category totals")

    p_del = subparsers.add_parser("delete", help="Delete an expense by id")
    p_del.add_argument("id", help="Expense ID to delete")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    store = ExpenseStore()

    commands = {
        "add": cmd_add,
        "list": cmd_list,
        "summary": cmd_summary,
        "delete": cmd_delete,
    }
    try:
        commands[args.command](args, store)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
