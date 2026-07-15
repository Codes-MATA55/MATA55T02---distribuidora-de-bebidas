from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class ValidityWindow:
    expiration_date: date

    def __post_init__(self) -> None:
        if not isinstance(self.expiration_date, date):
            raise ValueError("Expiration date must be a valid date")

    def is_expired(self, reference_date: date | None = None) -> bool:
        reference = reference_date or date.today()
        return self.expiration_date < reference

    def to_isoformat(self) -> str:
        return self.expiration_date.isoformat()
