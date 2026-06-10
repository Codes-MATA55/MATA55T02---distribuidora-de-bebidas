import re
from dataclasses import dataclass

_UFS_VALIDAS = frozenset({"AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"})

@dataclass(frozen=True)
class Endereco:
    cep: str
    rua: str
    numero: str
    bairro: str
    cidade: str
    uf: str
    complemento: str = ""

    def __post_init__(self) -> None:
        self._validar_cep()
        self._validar_rua()
        self._validar_numero()
        self._validar_bairro()
        self._validar_cidade()
        self._validar_uf()

    def _validar_cep(self) -> None:
        apenas_digitos = re.sub(r'\D', '', self.cep)
        if len(apenas_digitos) != 8:
            raise ValueError(f"CEP inválido: '{self.cep}'. Esperado 8 dígitos.")
        
    def _validar_rua(self) -> None:
        if not self.rua or not self.rua.strip():
            raise ValueError("Rua não pode ser vazia.")

    def _validar_numero(self) -> None:
        if not self.numero or not self.numero.strip():
            raise ValueError("Número não pode ser vazio. Use 'S/N' se não houver.")
        if not re.match(r'^[a-zA-Z0-9/\s-]+$', self.numero.strip()):
            raise ValueError(f"Número inválido: '{self.numero}'.")

    def _validar_bairro(self) -> None:
        if not self.bairro or not self.bairro.strip():
            raise ValueError("Bairro não pode ser vazio.")

    def _validar_cidade(self) -> None:
        if not self.cidade or not self.cidade.strip():
            raise ValueError("Cidade não pode ser vazia.")
        if len(self.cidade.strip()) < 3:
            raise ValueError("Nome de cidade muito curto.")

    def _validar_uf(self) -> None:
        if not self.uf:
            raise ValueError("UF não pode ser vazia.")
        if self.uf.upper() not in _UFS_VALIDAS:
            raise ValueError(f"UF inválida: '{self.uf}'. Use a sigla do estado (ex: SP, BA).")

    @property
    def cep_formatado(self) -> str:
        apenas_digitos = re.sub(r'\D', '', self.cep)
        return f"{apenas_digitos[:5]}-{apenas_digitos[5:]}"

    def __str__(self) -> str:
        complemento = f", {self.complemento}" if self.complemento else ""
        return (
            f"{self.rua}, {self.numero}{complemento} — "
            f"{self.bairro}, {self.cidade}/{self.uf.upper()} — "
            f"CEP {self.cep_formatado}"
        )