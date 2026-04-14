import argparse
from datetime import datetime
from expense_tracker.storage import ExpenseStore
from expense_tracker.models import Expense

def main():
    parser = argparse.ArgumentParser(description='Expense Tracker CLI')
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add', help='Add a new expense')
    add_parser.add_argument('--amount', type=float, required=True, help='Amount of the expense')
    add_parser.add_argument('--category', type=str, required=True, help='Category of the expense')
    add_parser.add_argument('--desc', type=str, required=True, help='Description of the expense')

    list_parser = subparsers.add_parser('list', help='List all expenses')
    list_parser.add_argument('--category', type=str, help='Filter by category')
    list_parser.add_argument('--since', type=str, help='Filter by date (YYYY-MM-DD)')

    summary_parser = subparsers.add_parser('summary', help='Print summary of expenses')

    delete_parser = subparsers.add_parser('delete', help='Delete an expense by ID')
    delete_parser.add_argument('id', type=int, help='ID of the expense')

    args = parser.parse_args()
    store = ExpenseStore()

    if args.command == 'add':
        expense = Expense(id=int(datetime.now().timestamp()), amount=args.amount, category=args.category, description=args.desc, date=datetime.now().date())
        store.add_expense(expense)
        print('Expense added!')
    elif args.command == 'list':
        expenses = store.list_expenses(category=args.category, since=args.since)
        for expense in expenses:
            print(expense)
    elif args.command == 'summary':
        summary = store.summary()
        for category, total in summary.items():
            print(f'{category}: {total}')
    elif args.command == 'delete':
        store.delete_expense(args.id)
        print('Expense deleted!')
    else:
        parser.print_help()

if __name__ == '__main__':
    main()