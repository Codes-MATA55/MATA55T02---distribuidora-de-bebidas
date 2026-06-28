from __future__ import annotations

from application.AddressValidationPort import AddressValidationPort


class AddressValidationAPIAdapter(AddressValidationPort):
    def __init__(self, api_client) -> None:
        self.__api = api_client

    def resolve(self, zip_code: str) -> str:
        raw = self.__api.get(f"/cep/{zip_code}")
        return f"{raw['logradouro']}, {raw['localidade']}-{raw['uf']}"
