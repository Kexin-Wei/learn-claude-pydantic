"""Data models for the expense tracker application."""

import dataclasses
from datetime import date


@dataclasses.dataclass
class Expense:
    """Represents a single expense record.

    Attributes:
        id: Unique identifier for the expense.
        amount: The monetary value of the expense.
        category: The category the expense belongs to (e.g., 'Food', 'Transport').
        description: A brief description of the expense.
        date: The date the expense was incurred.
    """

    id: int
    amount: float
    category: str
    description: str
    date: date

    def to_dict(self) -> dict:
        """Convert the expense to a dictionary for JSON serialization.

        The date field is converted to an ISO 8601 formatted string.

        Returns:
            A dictionary representation of the expense.
        """
        return dataclasses.asdict(self) | {"date": self.date.isoformat()}

    @classmethod
    def from_dict(cls, data: dict):
        """Create an Expense instance from dictionary data.

        Args:
            data: Dictionary containing expense data with keys:
                - id: int
                - amount: float
                - category: str
                - description: str
                - date: ISO 8601 date string or date object

        Returns:
            A new Expense instance.

        Raises:
            TypeError: If data is not a dictionary.
            KeyError: If required keys are missing.
            ValueError: If data values are of incorrect types.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")

        # Parse date from string if needed
        date_value = data["date"]
        if isinstance(date_value, str):
            date_value = date.fromisoformat(date_value)

        return cls(
            id=int(data["id"]),
            amount=float(data["amount"]),
            category=str(data["category"]),
            description=str(data["description"]),
            date=date_value,
        )
