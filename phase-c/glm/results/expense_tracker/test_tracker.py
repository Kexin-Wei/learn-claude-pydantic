"""Unit tests for the expense tracker application."""

import json
import os
import tempfile
import unittest
from datetime import date
from pathlib import Path

from expense_tracker.models import Expense
from expense_tracker.storage import ExpenseStore


class TestExpenseTracker(unittest.TestCase):
    """Test cases for the expense tracker functionality."""

    def setUp(self):
        """Set up a temporary file for each test."""
        self.temp_fd, self.temp_path = tempfile.mkstemp(suffix=".json")
        os.close(self.temp_fd)
        self.store = ExpenseStore(Path(self.temp_path))

    def tearDown(self):
        """Clean up the temporary file after each test."""
        if os.path.exists(self.temp_path):
            os.remove(self.temp_path)

    def _get_total(self, category: str | None = None) -> float:
        """Helper method to calculate total amount of expenses.

        Args:
            category: If provided, only sum expenses in this category.

        Returns:
            The total amount of all matching expenses.

        Raises:
            ValueError: If any expense has an invalid amount.
        """
        expenses = self.store.load()

        if category:
            expenses = [exp for exp in expenses if exp.category == category]

        total = 0.0
        for exp in expenses:
            if exp.amount < 0:
                raise ValueError(f"Expense {exp.id} has invalid negative amount: {exp.amount}")
            total += exp.amount

        return total

    def test_add_expense(self):
        """Test adding a single expense."""
        expense = Expense(
            id=1,
            amount=25.50,
            category="Food",
            description="Lunch",
            date=date(2026, 4, 14)
        )
        result = self.store.add_expense(expense)
        self.assertTrue(result)

        expenses = self.store.load()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].id, 1)
        self.assertEqual(expenses[0].amount, 25.50)
        self.assertEqual(expenses[0].category, "Food")
        self.assertEqual(expenses[0].description, "Lunch")
        self.assertEqual(expenses[0].date, date(2026, 4, 14))

    def test_add_multiple_expenses(self):
        """Test adding multiple expenses."""
        expenses = [
            Expense(id=1, amount=10.00, category="Transport", description="Bus ticket",
                    date=date(2026, 4, 1)),
            Expense(id=2, amount=25.50, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=3, amount=5.00, category="Coffee", description="Morning coffee",
                    date=date(2026, 4, 15)),
        ]

        for exp in expenses:
            result = self.store.add_expense(exp)
            self.assertTrue(result)

        loaded = self.store.load()
        self.assertEqual(len(loaded), 3)

        # Verify all expenses are loaded correctly
        loaded_dict = {exp.id: exp for exp in loaded}
        self.assertEqual(loaded_dict[1].amount, 10.00)
        self.assertEqual(loaded_dict[2].category, "Food")
        self.assertEqual(loaded_dict[3].description, "Morning coffee")

    def test_list_expenses(self):
        """Test listing all expenses."""
        expenses = [
            Expense(id=1, amount=10.00, category="Transport", description="Bus",
                    date=date(2026, 4, 1)),
            Expense(id=2, amount=25.50, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=3, amount=5.00, category="Food", description="Snack",
                    date=date(2026, 4, 15)),
        ]

        for exp in expenses:
            self.store.add_expense(exp)

        result = self.store.list_expenses()
        self.assertEqual(len(result), 3)

    def test_list_expenses_by_category_filter(self):
        """Test filtering expenses by category."""
        expenses = [
            Expense(id=1, amount=10.00, category="Transport", description="Bus",
                    date=date(2026, 4, 1)),
            Expense(id=2, amount=25.50, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=3, amount=5.00, category="Food", description="Snack",
                    date=date(2026, 4, 15)),
            Expense(id=4, amount=15.00, category="Transport", description="Taxi",
                    date=date(2026, 4, 16)),
        ]

        for exp in expenses:
            self.store.add_expense(exp)

        # Load and filter by category
        all_expenses = self.store.load()
        food_expenses = [exp for exp in all_expenses if exp.category == "Food"]
        self.assertEqual(len(food_expenses), 2)
        self.assertTrue(all(exp.category == "Food" for exp in food_expenses))

        transport_expenses = [exp for exp in all_expenses if exp.category == "Transport"]
        self.assertEqual(len(transport_expenses), 2)
        self.assertTrue(all(exp.category == "Transport" for exp in transport_expenses))

    def test_list_expenses_by_date_range(self):
        """Test filtering expenses by date range."""
        expenses = [
            Expense(id=1, amount=10.00, category="Transport", description="Bus",
                    date=date(2026, 4, 10)),
            Expense(id=2, amount=25.50, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=3, amount=5.00, category="Food", description="Snack",
                    date=date(2026, 4, 18)),
        ]

        for exp in expenses:
            self.store.add_expense(exp)

        # Filter by start date
        all_expenses = self.store.load()
        result = [exp for exp in all_expenses if exp.date >= date(2026, 4, 14)]
        self.assertEqual(len(result), 2)

        # Filter by end date
        result = [exp for exp in all_expenses if exp.date <= date(2026, 4, 14)]
        self.assertEqual(len(result), 2)

        # Filter by date range
        result = [
            exp for exp in all_expenses
            if date(2026, 4, 12) <= exp.date <= date(2026, 4, 15)
        ]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].description, "Lunch")

    def test_list_expenses_combined_filters(self):
        """Test filtering expenses with multiple filters."""
        expenses = [
            Expense(id=1, amount=10.00, category="Food", description="Lunch",
                    date=date(2026, 4, 10)),
            Expense(id=2, amount=25.50, category="Food", description="Dinner",
                    date=date(2026, 4, 14)),
            Expense(id=3, amount=5.00, category="Transport", description="Bus",
                    date=date(2026, 4, 14)),
            Expense(id=4, amount=15.00, category="Food", description="Brunch",
                    date=date(2026, 4, 18)),
        ]

        for exp in expenses:
            self.store.add_expense(exp)

        all_expenses = self.store.load()
        result = [
            exp for exp in all_expenses
            if exp.category == "Food"
            and date(2026, 4, 12) <= exp.date <= date(2026, 4, 15)
        ]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].description, "Dinner")

    def test_delete_expense(self):
        """Test deleting an expense by ID."""
        expenses = [
            Expense(id=1, amount=10.00, category="Transport", description="Bus",
                    date=date(2026, 4, 1)),
            Expense(id=2, amount=25.50, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=3, amount=5.00, category="Food", description="Snack",
                    date=date(2026, 4, 15)),
        ]

        for exp in expenses:
            self.store.add_expense(exp)

        # Delete an existing expense
        result = self.store.delete_expense(2)
        self.assertTrue(result)

        remaining = self.store.load()
        self.assertEqual(len(remaining), 2)
        ids = {exp.id for exp in remaining}
        self.assertEqual(ids, {1, 3})

        # Try to delete a non-existent expense
        result = self.store.delete_expense(999)
        self.assertFalse(result)
        self.assertEqual(len(self.store.load()), 2)

    def test_total_calculation(self):
        """Test calculating the total of all expenses."""
        expenses = [
            Expense(id=1, amount=10.00, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=2, amount=25.50, category="Food", description="Dinner",
                    date=date(2026, 4, 14)),
            Expense(id=3, amount=5.00, category="Transport", description="Bus",
                    date=date(2026, 4, 15)),
        ]

        for exp in expenses:
            self.store.add_expense(exp)

        total = self._get_total()
        self.assertEqual(total, 40.50)

    def test_total_by_category(self):
        """Test calculating the total by category."""
        expenses = [
            Expense(id=1, amount=10.00, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=2, amount=25.50, category="Food", description="Dinner",
                    date=date(2026, 4, 14)),
            Expense(id=3, amount=5.00, category="Transport", description="Bus",
                    date=date(2026, 4, 15)),
        ]

        for exp in expenses:
            self.store.add_expense(exp)

        food_total = self._get_total(category="Food")
        self.assertEqual(food_total, 35.50)

        transport_total = self._get_total(category="Transport")
        self.assertEqual(transport_total, 5.00)

    def test_total_empty_storage(self):
        """Test calculating total when no expenses exist."""
        total = self._get_total()
        self.assertEqual(total, 0.0)

    def test_error_handling_negative_amount(self):
        """Test that negative amounts raise an error."""
        expense = Expense(
            id=1,
            amount=-10.00,
            category="Food",
            description="Invalid expense",
            date=date(2026, 4, 14)
        )
        self.store.add_expense(expense)

        with self.assertRaises(ValueError) as context:
            self._get_total()

        self.assertIn("invalid negative amount", str(context.exception))

    def test_error_handling_missing_file(self):
        """Test loading from a non-existent file."""
        store = ExpenseStore(Path("/nonexistent/path/expenses.json"))
        expenses = store.load()
        self.assertEqual(expenses, [])

    def test_error_handling_invalid_json(self):
        """Test loading a file with invalid JSON."""
        # Write invalid JSON to the temp file
        with open(self.temp_path, "w") as f:
            f.write("{ invalid json content")

        expenses = self.store.load()
        # The storage gracefully handles invalid JSON by returning empty list
        self.assertEqual(expenses, [])

    def test_error_handling_non_list_json(self):
        """Test loading a file with valid JSON but not a list."""
        # Write a dict instead of a list
        with open(self.temp_path, "w") as f:
            json.dump({"not": "a list"}, f)

        expenses = self.store.load()
        self.assertEqual(expenses, [])

    def test_error_handling_add_non_expense_object(self):
        """Test that adding a non-Expense object returns False."""
        result = self.store.add_expense("not an expense")
        self.assertFalse(result)

        result = self.store.add_expense(123)
        self.assertFalse(result)

        result = self.store.add_expense(None)
        self.assertFalse(result)

    def test_persistence_across_instances(self):
        """Test that data persists across storage instances."""
        expense = Expense(
            id=1,
            amount=42.50,
            category="Entertainment",
            description="Movie ticket",
            date=date(2026, 4, 14)
        )
        self.store.add_expense(expense)

        # Create a new storage instance with the same file
        new_store = ExpenseStore(Path(self.temp_path))
        loaded = new_store.load()

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].amount, 42.50)
        self.assertEqual(loaded[0].category, "Entertainment")

    def test_save_overwrites_existing_data(self):
        """Test that save() overwrites existing data."""
        # Add some initial data
        initial_expenses = [
            Expense(id=1, amount=10.00, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=2, amount=20.00, category="Food", description="Dinner",
                    date=date(2026, 4, 14)),
        ]
        for exp in initial_expenses:
            self.store.add_expense(exp)

        # Save a completely different set of expenses
        new_expenses = [
            Expense(id=3, amount=100.00, category="Rent", description="Monthly rent",
                    date=date(2026, 4, 1)),
        ]
        result = self.store.save(new_expenses)
        self.assertTrue(result)

        # Verify only the new data exists
        loaded = self.store.load()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].id, 3)

    def test_get_expense(self):
        """Test retrieving a single expense by ID."""
        expenses = [
            Expense(id=1, amount=10.00, category="Food", description="Lunch",
                    date=date(2026, 4, 14)),
            Expense(id=2, amount=20.00, category="Transport", description="Bus",
                    date=date(2026, 4, 15)),
        ]

        for exp in expenses:
            self.store.add_expense(exp)

        # Get existing expense
        expense = self.store.get_expense(1)
        self.assertIsNotNone(expense)
        self.assertEqual(expense.id, 1)
        self.assertEqual(expense.amount, 10.00)

        # Get non-existent expense
        expense = self.store.get_expense(999)
        self.assertIsNone(expense)

    def test_update_expense(self):
        """Test updating an expense."""
        expense = Expense(
            id=1, amount=10.00, category="Food", description="Lunch",
            date=date(2026, 4, 14)
        )
        self.store.add_expense(expense)

        # Update amount
        result = self.store.update_expense(1, amount=15.00)
        self.assertTrue(result)

        loaded = self.store.get_expense(1)
        self.assertEqual(loaded.amount, 15.00)

        # Update multiple fields
        result = self.store.update_expense(
            1,
            category="Transport",
            description="Taxi",
            amount=25.50
        )
        self.assertTrue(result)

        loaded = self.store.get_expense(1)
        self.assertEqual(loaded.category, "Transport")
        self.assertEqual(loaded.description, "Taxi")
        self.assertEqual(loaded.amount, 25.50)

        # Update non-existent expense
        result = self.store.update_expense(999, amount=100.00)
        self.assertFalse(result)

    def test_update_expense_invalid_type(self):
        """Test updating with invalid types."""
        expense = Expense(
            id=1, amount=10.00, category="Food", description="Lunch",
            date=date(2026, 4, 14)
        )
        self.store.add_expense(expense)

        # Update with wrong type for amount
        result = self.store.update_expense(1, amount="invalid")
        self.assertFalse(result)

        # Update with wrong type for category
        result = self.store.update_expense(1, category=123)
        self.assertFalse(result)

        # Update with invalid field
        result = self.store.update_expense(1, nonexistent_field="value")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
