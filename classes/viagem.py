"""Entidade de domínio que representa uma viagem da frota."""
from __future__ import annotations
from datetime import datetime
from typing import Any


class Viagem:
    """Representa o deslocamento realizado por um motorista e veículo."""
    def __init__(self, motorista: Any, veiculo: Any, origem: str, destino: str,
                 distancia: float, data: datetime | str) -> None:
        self.motorista = motorista
        self.veiculo = veiculo
        self.origem = origem
        self.destino = destino
        self.distancia = distancia
        self.data = data

    @property
    def motorista(self) -> Any: return self.__motorista
    @motorista.setter
    def motorista(self, valor: Any) -> None:
        if valor is None: raise ValueError("A viagem deve possuir um motorista.")
        self.__motorista = valor

    @property
    def veiculo(self) -> Any: return self.__veiculo
    @veiculo.setter
    def veiculo(self, valor: Any) -> None:
        if valor is None: raise ValueError("A viagem deve possuir um veículo.")
        self.__veiculo = valor

    @property
    def origem(self) -> str: return self.__origem
    @origem.setter
    def origem(self, valor: str) -> None:
        if not str(valor).strip(): raise ValueError("A origem não pode ser vazia.")
        self.__origem = str(valor).strip()

    @property
    def destino(self) -> str: return self.__destino
    @destino.setter
    def destino(self, valor: str) -> None:
        if not str(valor).strip(): raise ValueError("O destino não pode ser vazio.")
        self.__destino = str(valor).strip()

    @property
    def distancia(self) -> float: return self.__distancia
    @distancia.setter
    def distancia(self, valor: float) -> None:
        numero = float(valor)
        if numero <= 0: raise ValueError("A distância não pode ser negativa ou igual a zero.")
        self.__distancia = numero

    @property
    def data(self) -> datetime | str: return self.__data
    @data.setter
    def data(self, valor: datetime | str) -> None:
        if valor is None: raise ValueError("A data da viagem é obrigatória.")
        self.__data = valor

    def to_dict(self) -> dict[str, Any]:
        data = self.data.isoformat(timespec="seconds") if isinstance(self.data, datetime) else self.data
        return {"motorista_cpf": getattr(self.motorista, "cpf", ""),
                "motorista_nome": getattr(self.motorista, "nome", ""),
                "veiculo_placa": getattr(self.veiculo, "placa", ""),
                "origem": self.origem, "destino": self.destino,
                "distancia": self.distancia, "data": data}
