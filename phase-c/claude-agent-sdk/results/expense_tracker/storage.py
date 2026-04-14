import json
from collections import defaultdict
from pathlib import Path

from .models import Expense


class ExpenseStore:
    def __init__(self, filepath: str | None = None):
        if filepath is None:
            filepath = str(Path(__file__).parent / "expenses.json")
        self.filepath = Path(filepath)

    def _load(self) -> list[dict]:
        try:
            return json.loads(self.filepath.read_text())
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return []

    def _save(self, expenses: list[dict]) -> None:
        self.filepath.write_text(json.dumps(expenses, indent=2))

    def add(self, expense: Expense) -> None:
        expenses = self._load()
        expenses.append(expense.to_dict())
        self._save(expenses)

    def list_all(
        self, category: str | None = None, since: str | None = None
    ) -> list[Expense]:
        expenses = self._load()
        results = []
        for data in expenses:
            if category and data["category"] != category:
                continue
            if since and data["date"] < since:
                continue
            results.append(Expense.from_dict(data))
        return results

    def delete(self, expense_id: str) -> bool:
        expenses = self._load()
        filtered = [e for e in expenses if e["id"] != expense_id]
        if len(filtered) == len(expenses):
            return False
        self._save(filtered)
        return True

    def summary(self) -> dict[str, float]:
        totals: dict[str, float] = defaultdict(float)
        for data in self._load():
            totals[data["category"]] += data["amount"]
        return dict(totals)
