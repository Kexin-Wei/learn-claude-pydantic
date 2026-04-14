"""Storage module for expense persistence using JSON."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Expense


STORAGE_PATH = Path("/home/kexin/Repos/learn-claude/phase-c/glm/results/expense_tracker/expenses.json")


class ExpenseStore:
    """Handles JSON persistence for Expense records.

    Provides CRUD operations with automatic serialization/deserialization
    and graceful error handling for file operations.
    """

    def __init__(self, storage_path: Path = STORAGE_PATH) -> None:
        """Initialize the expense store.

        Args:
            storage_path: Path to the JSON file for storing expenses.
                          Defaults to the standard location.
        """
        self._storage_path = Path(storage_path)

    def load(self) -> list[Expense]:
        """Load expenses from the JSON file.

        Returns:
            A list of Expense objects. Returns an empty list if the file
            does not exist or cannot be parsed.

        Raises:
            None - all errors are caught and logged, returning empty list.
        """
        try:
            if not self._storage_path.exists():
                return []

            data = json.loads(self._storage_path.read_text(encoding="utf-8"))

            if not isinstance(data, list):
                # Handle case where file contains non-list data
                return []

            expenses = []
            for item in data:
                try:
                    expense = Expense.from_dict(item)
                    expenses.append(expense)
                except (TypeError, KeyError, ValueError) as e:
                    # Skip invalid expense entries
                    continue

            return expenses

        except (json.JSONDecodeError, OSError, IOError):
            # Return empty list on any file/parsing error
            return []

    def save(self, expenses: list[Expense]) -> bool:
        """Save expenses to the JSON file.

        Args:
            expenses: List of Expense objects to save.

        Returns:
            True if save was successful, False otherwise.
        """
        try:
            # Validate input type
            if not isinstance(expenses, list):
                return False

            # Validate each item is an Expense
            for item in expenses:
                if not isinstance(item, Expense):
                    return False

            # Convert to list of dicts
            data = [expense.to_dict() for expense in expenses]

            # Ensure parent directory exists
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to file with atomic write pattern
            self._storage_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            return True

        except (OSError, IOError, TypeError):
            return False

    def add_expense(self, expense: Expense) -> bool:
        """Add a new expense to storage.

        Args:
            expense: The Expense object to add.

        Returns:
            True if the expense was added successfully, False otherwise.
        """
        if not isinstance(expense, Expense):
            return False

        expenses = self.load()
        expenses.append(expense)
        return self.save(expenses)

    def get_expense(self, expense_id: int) -> Expense | None:
        """Retrieve an expense by its ID.

        Args:
            expense_id: The unique identifier of the expense.

        Returns:
            The Expense object if found, None otherwise.
        """
        if not isinstance(expense_id, int):
            return None

        expenses = self.load()
        for expense in expenses:
            if expense.id == expense_id:
                return expense
        return None

    def list_expenses(self) -> list[Expense]:
        """List all expenses from storage.

        Returns:
            A list of all Expense objects. Returns empty list if no
            expenses exist or on error.
        """
        return self.load()

    def delete_expense(self, expense_id: int) -> bool:
        """Delete an expense by its ID.

        Args:
            expense_id: The unique identifier of the expense to delete.

        Returns:
            True if the expense was found and deleted, False otherwise.
        """
        if not isinstance(expense_id, int):
            return False

        expenses = self.load()
        original_count = len(expenses)
        expenses = [e for e in expenses if e.id != expense_id]

        if len(expenses) == original_count:
            # No expense was found with the given ID
            return False

        return self.save(expenses)

    def update_expense(self, expense_id: int, **updates: Any) -> bool:
        """Update an expense with new values.

        Args:
            expense_id: The unique identifier of the expense to update.
            **updates: Field names and their new values (amount, category,
                      description, date).

        Returns:
            True if the expense was found and updated, False otherwise.
        """
        if not isinstance(expense_id, int):
            return False

        expenses = self.load()

        for i, expense in enumerate(expenses):
            if expense.id == expense_id:
                # Create updated expense
                for field, value in updates.items():
                    if hasattr(expense, field):
                        # Type validation for known fields
                        if field == "amount" and not isinstance(value, (int, float)):
                            return False
                        if field == "id" and not isinstance(value, int):
                            return False
                        if field in ("category", "description") and not isinstance(value, str):
                            return False
                        # 'date' field - will be validated when constructing Expense
                        setattr(expense, field, value)
                    else:
                        return False

                return self.save(expenses)

        return False
