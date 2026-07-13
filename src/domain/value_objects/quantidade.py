from dataclasses import dataclass


@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise ValueError("Quantity must be an integer")
        if self.value < 0:
            raise ValueError("Quantity cannot be negative")

    @classmethod
    def positive(cls, value: int) -> "Quantity":
        quantity = cls(value)
        if quantity.value <= 0:
            raise ValueError("Quantity must be greater than zero")
        return quantity

    def add(self, other: "Quantity") -> "Quantity":
        return Quantity(self.value + other.value)

    def subtract(self, other: "Quantity") -> "Quantity":
        if other.value > self.value:
            raise ValueError("Quantity cannot become negative")
        return Quantity(self.value - other.value)
