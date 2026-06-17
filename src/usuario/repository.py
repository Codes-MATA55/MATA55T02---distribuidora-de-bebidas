from __future__ import annotations
from typing import Dict, Optional

from usuario.aggregate import Usuario


class UsuarioRepository:
    def __init__(self):
        self._usuarios: Dict[str, Usuario] = {}

    def buscar_por_id(self, id: str) -> Optional[Usuario]:
        return self._usuarios.get(id)

    def salvar(self, usuario: Usuario) -> None:
        self._usuarios[usuario.id] = usuario
