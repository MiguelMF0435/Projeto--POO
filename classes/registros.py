"""Entidades de domínio para manutenções e abastecimentos."""
from __future__ import annotations
from datetime import datetime
from typing import Any


class Manutencao:
    """Representa um serviço preventivo ou corretivo associado a um veículo."""
    TIPOS_VALIDOS = {"preventiva", "corretiva"}

    def __init__(self, data: datetime | str, tipo: str, custo: float,
                 descricao: str, veiculo: Any,
                 status: str = "em_andamento") -> None:
        self.data = data
        self.tipo = tipo
        self.custo = custo
        self.descricao = descricao
        self.veiculo = veiculo
        self.status = status

    @property
    def data(self) -> datetime | str:
        return self.__data

    @data.setter
    def data(self, valor: datetime | str) -> None:
        if valor is None:
            raise ValueError("A data da manutenção é obrigatória.")
        self.__data = valor

    @property
    def tipo(self) -> str:
        return self.__tipo

    @tipo.setter
    def tipo(self, valor: str) -> None:
        tipo = str(valor).strip().lower()
        if tipo not in self.TIPOS_VALIDOS:
            raise ValueError("Tipo deve ser preventiva ou corretiva.")
        self.__tipo = tipo

    @property
    def custo(self) -> float:
        return self.__custo

    @custo.setter
    def custo(self, valor: float) -> None:
        numero = float(valor)
        if numero < 0:
            raise ValueError("O custo não pode ser negativo.")
        self.__custo = numero

    @property
    def descricao(self) -> str:
        return self.__descricao

    @descricao.setter
    def descricao(self, valor: str) -> None:
        if not str(valor).strip():
            raise ValueError("A descrição não pode ser vazia.")
        self.__descricao = str(valor).strip()

    @property
    def veiculo(self) -> Any:
        return self.__veiculo

    @veiculo.setter
    def veiculo(self, valor: Any) -> None:
        if valor is None:
            raise ValueError("A manutenção deve estar associada a um veículo.")
        self.__veiculo = valor

    @property
    def status(self) -> str:
        return self.__status

    @status.setter
    def status(self, valor: str) -> None:
        status = str(valor).strip().lower()
        if status not in {"em_andamento", "concluida", "cancelada"}:
            raise ValueError("Status de manutenção inválido.")
        self.__status = status

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para um registro serializável em JSON."""
        data = self.data.isoformat(timespec="seconds") if isinstance(self.data, datetime) else self.data
        return {"data": data, "tipo": self.tipo, "custo": self.custo,
                "descricao": self.descricao,
                "veiculo_placa": getattr(self.veiculo, "placa", ""),
                "status": self.status}


class Abastecimento:
    """Representa o abastecimento de um veículo e sua quilometragem."""
    def __init__(self, data: datetime | str, tipo_combustivel: str,
                 litros: float, valor_pago: float, veiculo: Any,
                 quilometragem: float) -> None:
        self.data = data
        self.tipo_combustivel = tipo_combustivel
        self.litros = litros
        self.valor_pago = valor_pago
        self.veiculo = veiculo
        self.quilometragem = quilometragem

    @property
    def data(self) -> datetime | str:
        return self.__data

    @data.setter
    def data(self, valor: datetime | str) -> None:
        if valor is None:
            raise ValueError("A data do abastecimento é obrigatória.")
        self.__data = valor

    @property
    def tipo_combustivel(self) -> str:
        return self.__tipo_combustivel

    @tipo_combustivel.setter
    def tipo_combustivel(self, valor: str) -> None:
        if not str(valor).strip():
            raise ValueError("O tipo de combustível não pode ser vazio.")
        self.__tipo_combustivel = str(valor).strip()

    @property
    def litros(self) -> float:
        return self.__litros

    @litros.setter
    def litros(self, valor: float) -> None:
        numero = float(valor)
        if numero <= 0:
            raise ValueError("A quantidade de litros deve ser positiva.")
        self.__litros = numero

    @property
    def valor_pago(self) -> float:
        return self.__valor_pago

    @valor_pago.setter
    def valor_pago(self, valor: float) -> None:
        numero = float(valor)
        if numero < 0:
            raise ValueError("O valor pago não pode ser negativo.")
        self.__valor_pago = numero

    @property
    def veiculo(self) -> Any:
        return self.__veiculo

    @veiculo.setter
    def veiculo(self, valor: Any) -> None:
        if valor is None:
            raise ValueError("O abastecimento deve estar associado a um veículo.")
        self.__veiculo = valor

    @property
    def quilometragem(self) -> float:
        return self.__quilometragem

    @quilometragem.setter
    def quilometragem(self, valor: float) -> None:
        numero = float(valor)
        if numero < 0:
            raise ValueError("A quilometragem não pode ser negativa.")
        self.__quilometragem = numero

    def to_dict(self) -> dict[str, Any]:
        """Converte a entidade para um registro serializável em JSON."""
        data = self.data.isoformat(timespec="seconds") if isinstance(self.data, datetime) else self.data
        return {"data": data, "tipo_combustivel": self.tipo_combustivel,
                "litros": self.litros, "valor_pago": self.valor_pago,
                "veiculo_placa": getattr(self.veiculo, "placa", ""),
                "quilometragem": self.quilometragem}
