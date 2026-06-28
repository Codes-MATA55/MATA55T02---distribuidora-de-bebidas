from __future__ import annotations

from application.CarrierPort import CarrierPort


class CarrierAPIAdapter(CarrierPort):
    def __init__(self, api_client) -> None:
        self.__api = api_client

    def dispatch(self, order_id: str) -> str:
        raw = self.__api.post("/shipments", {"order": order_id})
        return raw["tracking"]["code"]
