from dataclasses import dataclass
from datetime import date

@dataclass
class Expense:
    id: int
    amount: float
    category: str
    description: str
    date: date