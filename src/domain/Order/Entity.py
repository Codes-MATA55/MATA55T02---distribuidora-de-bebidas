from __future__ import annotations


class Order:
    def __init__(self, id: str) -> None:
        self.__id = id

    @property
    def id(self) -> str:
        return self.__id
