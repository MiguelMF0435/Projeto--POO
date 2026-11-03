"""Modelos de pessoas e motoristas da frota."""
from __future__ import annotations
from typing import Any


class PessoaBase:
    """Classe base com dados comuns de pessoas cadastradas."""
    def __init__(self, nome: str, cpf: str, funcao: str) -> None:
        self.nome = nome
        self.cpf = cpf
        self.funcao = funcao

    @property
    def nome(self) -> str:
        return self.__nome

    @nome.setter
    def nome(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("O nome não pode ser vazio.")
        self.__nome = valor.strip()

    @property
    def cpf(self) -> str:
        return self.__cpf

    @cpf.setter
    def cpf(self, valor: str) -> None:
        digitos = "".join(c for c in str(valor) if c.isdigit())
        if not digitos:
            raise ValueError("O CPF não pode ser vazio.")
        self.__cpf = digitos

    @property
    def funcao(self) -> str:
        return self.__funcao

    @funcao.setter
    def funcao(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("A função não pode ser vazia.")
        self.__funcao = valor.strip()


class Motorista(PessoaBase):
    """Pessoa habilitada para conduzir veículos e registrar viagens."""
    CATEGORIAS_VALIDAS = {"A", "B", "C", "D", "E"}
    HIERARQUIA_CNH = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}
    CATEGORIA_POR_TIPO = {"moto": "A", "carro": "B", "caminhao": "C"}

    def __init__(self, nome: str, cpf: str, funcao: str = "Motorista",
                 categoria_cnh: str = "B", experiencia_anos: int = 0,
                 disponibilidade: bool = True, historico_viagens: list[Any] | None = None) -> None:
        super().__init__(nome, cpf, funcao)
        self.categoria_cnh = categoria_cnh
        self.experiencia_anos = experiencia_anos
        self.disponibilidade = disponibilidade
        self._historico_viagens = list(historico_viagens or [])

    @property
    def categoria_cnh(self) -> str:
        return self.__categoria_cnh

    @categoria_cnh.setter
    def categoria_cnh(self, valor: str) -> None:
        categoria = str(valor).strip().upper()
        if categoria not in self.CATEGORIAS_VALIDAS:
            raise ValueError("Categoria da CNH deve ser A, B, C, D ou E.")
        self.__categoria_cnh = categoria

    @property
    def experiencia_anos(self) -> int:
        return self.__experiencia_anos

    @experiencia_anos.setter
    def experiencia_anos(self, valor: int) -> None:
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("A experiência não pode ser negativa e deve ser um inteiro.")
        self.__experiencia_anos = valor

    @property
    def disponibilidade(self) -> bool:
        return self.__disponibilidade

    @disponibilidade.setter
    def disponibilidade(self, valor: bool) -> None:
        self.__disponibilidade = bool(valor)

    @property
    def historico_viagens(self) -> list[Any]:
        return list(self._historico_viagens)

    def adicionar_viagem(self, viagem: Any) -> None:
        if viagem is None:
            raise ValueError("A viagem não pode ser vazia.")
        self._historico_viagens.append(viagem)

    def verificar_compatibilidade(self, tipo_veiculo: str,
                                  configuracao: dict[str, Any] | None = None) -> bool:
        tipo = str(tipo_veiculo).strip().lower().replace("ã", "a")
        minimo = (configuracao or {}).get("cnh_minima", {}).get(
            tipo_veiculo, self.CATEGORIA_POR_TIPO.get(tipo)
        )
        if minimo not in self.HIERARQUIA_CNH:
            return False
        permitidas = {"A": {"A"}, "B": {"B", "C", "D", "E"},
                      "C": {"C", "D", "E"}, "D": {"D", "E"}, "E": {"E"}}
        return self.categoria_cnh in permitidas[minimo]

    def to_dict(self) -> dict[str, Any]:
        return {"nome": self.nome, "cpf": self.cpf, "funcao": self.funcao,
                "categoria_cnh": self.categoria_cnh, "experiencia_anos": self.experiencia_anos,
                "disponibilidade": self.disponibilidade,
                "historico_viagens": self.historico_viagens}
