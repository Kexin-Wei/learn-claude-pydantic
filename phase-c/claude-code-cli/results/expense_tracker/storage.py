import json
from pathlib import Path
from datetime import datetime

from .models import Expense


class ExpenseStore:

    def __init__(self, filepath: str | None = None):
        if filepath is None:
            filepath = Path(__file__).parent / "expenses.json"
        else:
            filepath = Path(filepath)
        self.filepath = filepath

    def _load(self) -> list[Expense]:
        try:
            if not self.filepath.exists():
                return []
            with open(self.filepath, "r") as f:
                data = json.load(f)
            return [Expense.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError, TypeError):
            return []

    def _save(self, expenses: list[Expense]) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        data = [e.to_dict() for e in expenses]
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=2)

    def add(self, amount: float, category: str, description: str) -> Expense:
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        expenses = self._load()
        new_expense = Expense(amount=amount, category=category, description=description)
        expenses.append(new_expense)
        self._save(expenses)
        return new_expense

    def list_expenses(self, category: str | None = None, since: str | None = None) -> list[Expense]:
        expenses = self._load()
        if category is not None:
            expenses = [e for e in expenses if e.category == category]
        if since is not None:
            try:
                since_date = datetime.fromisoformat(since).date()
                expenses = [
                    e for e in expenses
                    if datetime.fromisoformat(e.date).date() >= since_date
                ]
            except ValueError:
                pass
        return expenses

    def delete(self, expense_id: str) -> bool:
        expenses = self._load()
        original_length = len(expenses)
        expenses = [e for e in expenses if e.id != expense_id]
        if len(expenses) < original_length:
            self._save(expenses)
            return True
        return False

    def summary(self) -> dict[str, float]:
        expenses = self._load()
        totals: dict[str, float] = {}
        for e in expenses:
            totals[e.category] = totals.get(e.category, 0) + e.amount
        return totals
