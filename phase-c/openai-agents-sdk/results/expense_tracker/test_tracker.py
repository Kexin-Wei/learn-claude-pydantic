import unittest
from datetime import date
from expense_tracker.models import Expense
from expense_tracker.storage import ExpenseStore

class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        self.store = ExpenseStore('test_expenses.json')
        self.store.save_expenses([])  # Clear any existing test data

    def test_add_expense(self):
        expense = Expense(id=1, amount=12.50, category='food', description='Lunch', date=date.today())
        self.store.add_expense(expense)
        expenses = self.store.load_expenses()
        self.assertEqual(len(expenses), 1)
        self.assertEqual(expenses[0].amount, 12.50)

    def test_delete_expense(self):
        expense = Expense(id=1, amount=12.50, category='food', description='Lunch', date=date.today())
        self.store.add_expense(expense)
        self.store.delete_expense(1)
        expenses = self.store.load_expenses()
        self.assertEqual(len(expenses), 0)

    def test_summary(self):
        expense1 = Expense(id=1, amount=12.50, category='food', description='Lunch', date=date.today())
        expense2 = Expense(id=2, amount=45.00, category='transport', description='Taxi', date=date.today())
        self.store.add_expense(expense1)
        self.store.add_expense(expense2)
        summary = self.store.summary()
        self.assertEqual(summary['food'], 12.50)
        self.assertEqual(summary['transport'], 45.00)

if __name__ == '__main__':
    unittest.main()