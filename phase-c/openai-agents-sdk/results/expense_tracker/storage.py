import json
from datetime import datetime
from typing import List, Optional
from expense_tracker.models import Expense

class ExpenseStore:
    def __init__(self, filename='expenses.json'):
        self.filename = filename

    def _serialize(self, expense: Expense) -> dict:
        return {
            'id': expense.id,
            'amount': expense.amount,
            'category': expense.category,
            'description': expense.description,
            'date': expense.date.isoformat(),
        }

    def _deserialize(self, data: dict) -> Expense:
        return Expense(
            id=data['id'],
            amount=data['amount'],
            category=data['category'],
            description=data['description'],
            date=datetime.fromisoformat(data['date']).date()
        )

    def load_expenses(self) -> List[Expense]:
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return [self._deserialize(item) for item in data]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []

    def save_expenses(self, expenses: List[Expense]):
        with open(self.filename, 'w') as f:
            json.dump([self._serialize(e) for e in expenses], f)

    def add_expense(self, expense: Expense):
        expenses = self.load_expenses()
        expenses.append(expense)
        self.save_expenses(expenses)

    def delete_expense(self, expense_id: int):
        expenses = self.load_expenses()
        expenses = [e for e in expenses if e.id != expense_id]
        self.save_expenses(expenses)

    def list_expenses(self, category: Optional[str] = None, since: Optional[str] = None):
        expenses = self.load_expenses()
        if category:
            expenses = [e for e in expenses if e.category == category]
        if since:
            since_date = datetime.strptime(since, '%Y-%m-%d').date()
            expenses = [e for e in expenses if e.date >= since_date]
        return expenses

    def summary(self):
        expenses = self.load_expenses()
        summary = {}
        for expense in expenses:
            summary[expense.category] = summary.get(expense.category, 0) + expense.amount
        return summary