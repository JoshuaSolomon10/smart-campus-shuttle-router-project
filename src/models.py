"""Small domain models for shuttle operations."""
from dataclasses import dataclass, field
from typing import Optional

PRIORITY_BY_CATEGORY = {"Emergency": 0, "Faculty": 1, "Student": 2}

@dataclass
class ShuttleRequest:
    request_id: str
    passenger: str
    origin: str
    destination: str
    category: str
    sequence: int
    status: str = "Pending"
    priority: int = field(init=False)

    def __post_init__(self) -> None:
        if self.category not in PRIORITY_BY_CATEGORY:
            raise ValueError(f"Unsupported category: {self.category}")
        if not self.origin or not self.destination:
            raise ValueError("Origin and destination are required.")
        if self.origin == self.destination:
            raise ValueError("Origin and destination must be different.")
        self.priority = PRIORITY_BY_CATEGORY[self.category]

@dataclass
class Shuttle:
    shuttle_id: str
    status: str = "Available"
    assigned_route: list[str] = field(default_factory=list)
    current_request_id: Optional[str] = None
    completed_trips: int = 0
