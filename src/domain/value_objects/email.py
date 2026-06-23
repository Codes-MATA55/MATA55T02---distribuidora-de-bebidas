import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        email = self.value.strip().lower()

        regex = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

        if not re.match(regex, email):
            raise ValueError("E-mail inválido")

        object.__setattr__(self, "value", email)
