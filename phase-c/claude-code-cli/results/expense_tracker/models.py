from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import uuid4


@dataclass
class Expense:
    """Represents a financial expense."""
    id: str
    amount: float
    category: str
    description: str
    date: str

    def __init__(
        self,
        amount: float,
        category: str,
        description: str,
        id: str = None,
        date: str = None,
    ):
        """Initialize an Expense.

        Args:
            amount: The expense amount in currency units
            category: The category of the expense
            description: A description of the expense
            id: Optional UUID string (generated if not provided)
            date: Optional ISO format date string (defaults to today)
        """
        self.id = id or str(uuid4())
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date or datetime.today().isoformat()

    def to_dict(self) -> dict:
        """Convert the Expense to a dictionary.

        Returns:
            Dictionary representation of the Expense
        """
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """Create an Expense from a dictionary.

        Args:
            data: Dictionary containing expense data

        Returns:
            An Expense instance
        """
        return cls(
            id=data.get("id"),
            amount=data.get("amount"),
            category=data.get("category"),
            description=data.get("description"),
            date=data.get("date"),
        )
