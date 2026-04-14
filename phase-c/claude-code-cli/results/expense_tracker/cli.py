import argparse
import sys
from pathlib import Path

# Allow running as a script
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from expense_tracker.storage import ExpenseStore


def cmd_add(args, store: ExpenseStore):
    try:
        expense = store.add(
            amount=args.amount, category=args.category, description=args.desc
        )
        print(f"Added expense {expense.id[:8]}:  ${expense.amount:.2f}  [{expense.category}]  {expense.description}")
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args, store: ExpenseStore):
    expenses = store.list_expenses(category=args.category, since=args.since)
    if not expenses:
        print("No expenses found.")
        return
    print(f"{'ID':>8}  {'Amount':>10}  {'Category':<14}  {'Description':<20}  {'Date'}")
    print("-" * 78)
    for e in expenses:
        print(f"{e.id[:8]:>8}  ${e.amount:>9.2f}  {e.category:<14}  {e.description:<20}  {e.date[:10]}")


def cmd_summary(_args, store: ExpenseStore):
    totals = store.summary()
    if not totals:
        print("No expenses to summarise.")
        return
    print(f"{'Category':<20}  {'Total':>10}")
    print("-" * 32)
    grand = 0.0
    for cat, total in sorted(totals.items()):
        print(f"{cat:<20}  ${total:>9.2f}")
        grand += total
    print("-" * 32)
    print(f"{'TOTAL':<20}  ${grand:>9.2f}")


def cmd_delete(args, store: ExpenseStore):
    if store.delete(args.id):
        print(f"Deleted expense {args.id[:8]}.")
    else:
        print(f"Error: expense {args.id} not found.", file=sys.stderr)
        sys.exit(1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Expense Tracker CLI")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Add a new expense")
    p_add.add_argument("--amount", type=float, required=True)
    p_add.add_argument("--category", required=True)
    p_add.add_argument("--desc", required=True, help="Description")

    # list
    p_list = sub.add_parser("list", help="List expenses")
    p_list.add_argument("--category", default=None)
    p_list.add_argument("--since", default=None, help="ISO date (YYYY-MM-DD)")

    # summary
    sub.add_parser("summary", help="Show totals per category")

    # delete
    p_del = sub.add_parser("delete", help="Delete an expense by ID")
    p_del.add_argument("id", help="Expense UUID")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(1)

    store = ExpenseStore()
    {"add": cmd_add, "list": cmd_list, "summary": cmd_summary, "delete": cmd_delete}[
        args.command
    ](args, store)


if __name__ == "__main__":
    main()
