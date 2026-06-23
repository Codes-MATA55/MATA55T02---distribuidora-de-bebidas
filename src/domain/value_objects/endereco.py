import re
from dataclasses import dataclass

_VALID_STATES = frozenset({"AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"})

@dataclass(frozen=True)
class Endereco:
    cep: str
    street: str
    street_number: str
    neighbourhood: str
    city: str
    state: str
    additional_address_details: str = ""

    def __post_init__(self) -> None:
        self._validate_cep()
        self._validate_street()
        self._validate_street_number()
        self._validate_neighbourhood()
        self._validate_city()
        self._validate_state()

    def _validate_cep(self) -> None:
        digits_only = re.sub(r'\D', '', self.cep)
        if len(digits_only) != 8:
            raise ValueError(f"CEP inválido: '{self.cep}'. Esperado 8 dígitos.")
        
    def _validate_street(self) -> None:
        if not self.street or not self.street.strip():
            raise ValueError("Rua não pode ser vazia.")

    def _validate_street_number(self) -> None:
        if not self.street_number or not self.street_number.strip():
            raise ValueError("Número não pode ser vazio. Use 'S/N' se não houver.")
        if not re.match(r'^[a-zA-Z0-9/\s-]+$', self.street_number.strip()):
            raise ValueError(f"Número inválido: '{self.street_number}'.")

    def _validate_neighbourhood(self) -> None:
        if not self.neighbourhood or not self.neighbourhood.strip():
            raise ValueError("Bairro não pode ser vazio.")

    def _validate_city(self) -> None:
        if not self.city or not self.city.strip():
            raise ValueError("Cidade não pode ser vazia.")
        if len(self.city.strip()) < 3:
            raise ValueError("Nome de cidade muito curto.")

    def _validate_state(self) -> None:
        if not self.state:
            raise ValueError("UF não pode ser vazia.")
        if self.state.upper() not in _VALID_STATES:
            raise ValueError(f"UF inválida: '{self.state}'. Use a sigla do estado (ex: SP, BA).")

    @property
    def format_cep(self) -> str:
        digits_only = re.sub(r'\D', '', self.cep)
        return f"{digits_only[:5]}-{digits_only[5:]}"

    def __str__(self) -> str:
        additional_address_details = f", {self.additional_address_details}" if self.additional_address_details else ""
        return (
            f"{self.street}, {self.street_number}{additional_address_details} — "
            f"{self.neighbourhood}, {self.city}/{self.state.upper()} — "
            f"CEP {self.format_cep}"
        )