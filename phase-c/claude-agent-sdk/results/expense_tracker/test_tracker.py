"""Unit tests for expense_tracker models and storage."""

import sys
import os
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from expense_tracker.models import Expense
from expense_tracker.storage import ExpenseStore


class TestExpenseModel(unittest.TestCase):
    def test_expense_round_trip(self):
        """Create an Expense, serialise to dict, deserialise back, and verify equality."""
        original = Expense(amount=42.50, category="food", description="Lunch")
        data = original.to_dict()
        restored = Expense.from_dict(data)

        self.assertEqual(restored.amount, original.amount)
        self.assertEqual(restored.category, original.category)
        self.assertEqual(restored.description, original.description)
        self.assertEqual(restored.id, original.id)
        self.assertEqual(restored.date, original.date)


class TestExpenseStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            suffix=".json", delete=False
        )
        self.tmp.close()
        self.filepath = self.tmp.name
        self.store = ExpenseStore(filepath=self.filepath)

    def tearDown(self):
        try:
            os.unlink(self.filepath)
        except FileNotFoundError:
            pass

    def test_add_and_list(self):
        """Add an expense and verify it appears in list_all."""
        expense = Expense(amount=9.99, category="snacks", description="Chips")
        self.store.add(expense)

        results = self.store.list_all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].amount, 9.99)
        self.assertEqual(results[0].category, "snacks")
        self.assertEqual(results[0].id, expense.id)

    def test_delete(self):
        """Add an expense, delete it by id, and verify the list is empty."""
        expense = Expense(amount=5.00, category="coffee", description="Latte")
        self.store.add(expense)

        deleted = self.store.delete(expense.id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.store.list_all()), 0)

    def test_delete_nonexistent(self):
        """Deleting a nonexistent id returns False."""
        self.assertFalse(self.store.delete("no-such-id"))

    def test_summary(self):
        """Add expenses in different categories and verify summary totals."""
        self.store.add(Expense(amount=10.00, category="food", description="Lunch"))
        self.store.add(Expense(amount=20.00, category="food", description="Dinner"))
        self.store.add(Expense(amount=5.00, category="transport", description="Bus"))

        totals = self.store.summary()
        self.assertAlmostEqual(totals["food"], 30.00)
        self.assertAlmostEqual(totals["transport"], 5.00)
        self.assertEqual(len(totals), 2)

    def test_list_filter_category(self):
        """Add expenses in different categories and filter by one."""
        self.store.add(Expense(amount=15.00, category="food", description="Salad"))
        self.store.add(Expense(amount=3.50, category="drink", description="Tea"))
        self.store.add(Expense(amount=12.00, category="food", description="Pizza"))

        food_only = self.store.list_all(category="food")
        self.assertEqual(len(food_only), 2)
        for exp in food_only:
            self.assertEqual(exp.category, "food")


if __name__ == "__main__":
    unittest.main()
