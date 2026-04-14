from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass
class Expense:
    amount: float
    category: str
    description: str
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    date: str = field(default_factory=lambda: date.today().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
            "date": self.date,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        return cls(
            id=data["id"],
            amount=data["amount"],
            category=data["category"],
            description=data["description"],
            date=data["date"],
        )
