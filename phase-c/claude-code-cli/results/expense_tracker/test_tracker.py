import json
import tempfile
import unittest
from pathlib import Path

from expense_tracker.models import Expense
from expense_tracker.storage import ExpenseStore


class TestExpenseModel(unittest.TestCase):

    def test_to_dict_roundtrip(self):
        e = Expense(amount=10.0, category="food", description="Lunch")
        d = e.to_dict()
        e2 = Expense.from_dict(d)
        self.assertEqual(e.id, e2.id)
        self.assertEqual(e.amount, e2.amount)
        self.assertEqual(e.category, e2.category)


class TestExpenseStore(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.filepath = Path(self.tmp.name)
        self.filepath.unlink()  # start with no file
        self.store = ExpenseStore(filepath=str(self.filepath))

    def tearDown(self):
        if self.filepath.exists():
            self.filepath.unlink()

    def test_add_and_list(self):
        self.store.add(12.50, "food", "Lunch")
        self.store.add(45.00, "transport", "Taxi")
        expenses = self.store.list_expenses()
        self.assertEqual(len(expenses), 2)

    def test_delete(self):
        exp = self.store.add(5.0, "misc", "Coffee")
        self.assertTrue(self.store.delete(exp.id))
        self.assertEqual(len(self.store.list_expenses()), 0)

    def test_summary(self):
        self.store.add(10.0, "food", "A")
        self.store.add(20.0, "food", "B")
        self.store.add(5.0, "transport", "C")
        s = self.store.summary()
        self.assertAlmostEqual(s["food"], 30.0)
        self.assertAlmostEqual(s["transport"], 5.0)

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.store.add(-1, "food", "Bad")

    def test_missing_file_returns_empty(self):
        self.assertEqual(self.store.list_expenses(), [])

    def test_filter_by_category(self):
        self.store.add(10.0, "food", "A")
        self.store.add(5.0, "transport", "B")
        self.assertEqual(len(self.store.list_expenses(category="food")), 1)


if __name__ == "__main__":
    unittest.main()
