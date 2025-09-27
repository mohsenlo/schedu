from dataclasses import dataclass


@dataclass
class Task:
    """Main Task Model."""

    name: str
    start: str
    end: str
    days: list[str]

    def __repr__(self):
        return f"Task > {self.name}\t From {self.start} To {self.end} in {self.days}"
