from __future__ import annotations

from application.RoutingPort import RoutingPort


class RoutingAPIAdapter(RoutingPort):
    def __init__(self, api_client) -> None:
        self.__api = api_client

    def best_route(self, stops: list[str]) -> list[str]:
        raw = self.__api.post("/routes", {"stops": stops})
        return [leg["address"] for leg in raw["route"]["legs"]]
