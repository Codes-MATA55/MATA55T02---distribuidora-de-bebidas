from __future__ import annotations
import uuid

from usuario.value_objects import Cargo


class Usuario:
    def __init__(self, id: str, nome: str, cargo: Cargo):
        self.__id = id
        self.__nome = nome
        self.__cargo = cargo

    @staticmethod
    def criar(nome: str, cargo: Cargo) -> Usuario:
        return Usuario(id=str(uuid.uuid4()), nome=nome, cargo=cargo)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def cargo(self) -> Cargo:
        return self.__cargo

    def pode_autorizar_expedicao(self) -> bool:
        return self.__cargo in {Cargo.SUPERVISOR, Cargo.GERENTE}

    def __str__(self) -> str:
        return f"Usuario[nome={self.__nome}, cargo={self.__cargo.value}]"
