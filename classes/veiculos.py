"""Modelos de veículos e seus estados para o sistema de frota."""
from __future__ import annotations

from enum import Enum
from typing import Any, Iterator

from mixins import AbastecivelMixin, ManutenivelMixin


class StatusVeiculo(str, Enum):
    """Estados válidos de um veículo."""
    ATIVO = "ATIVO"
    MANUTENCAO = "MANUTENCAO"
    INATIVO = "INATIVO"

    @classmethod
    def normalizar(cls: type["StatusVeiculo"], valor: "StatusVeiculo | str") -> "StatusVeiculo":
        if isinstance(valor, cls):
            return valor
        texto = str(valor).strip().upper().replace("Ã", "A").replace("Ç", "C")
        aliases = {"EM MANUTENCAO": "MANUTENCAO", "DISPONIVEL": "ATIVO", "NOVO": "ATIVO"}
        try:
            return cls(aliases.get(texto, texto))
        except ValueError as exc:
            raise ValueError("Status deve ser ATIVO, MANUTENCAO ou INATIVO.") from exc


class VeiculoBase(ManutenivelMixin, AbastecivelMixin):
    """Classe base com dados, histórico e comportamento comum dos veículos."""

    def __init__(self, placa: str, marca: str, modelo: str, tipo: str, ano: int,
                 quilometragem: float, consumo_medio: float,
                 status: StatusVeiculo | str = StatusVeiculo.ATIVO) -> None:
        self.placa = placa
        self.marca = marca
        self.modelo = modelo
        self.tipo = tipo
        self.ano = ano
        self.quilometragem = quilometragem
        self.km_ultima_revisao_preventiva = quilometragem
        self.consumo_medio = consumo_medio
        self.status = status
        self._historico_eventos: list[dict[str, Any]] = []
        self._historico_viagens: list[Any] = []
        self._inicializar_manutencoes()
        self._inicializar_abastecimentos()

    @property
    def placa(self) -> str:
        return self.__placa

    @placa.setter
    def placa(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("A placa não pode ser vazia.")
        self.__placa = valor.strip().upper()

    @property
    def marca(self) -> str:
        return self.__marca

    @marca.setter
    def marca(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("A marca não pode ser vazia.")
        self.__marca = valor.strip()

    @property
    def modelo(self) -> str:
        return self.__modelo

    @modelo.setter
    def modelo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("O modelo não pode ser vazio.")
        self.__modelo = valor.strip()

    @property
    def tipo(self) -> str:
        return self.__tipo

    @tipo.setter
    def tipo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("O tipo não pode ser vazio.")
        self.__tipo = valor.strip()

    @property
    def ano(self) -> int:
        return self.__ano

    @ano.setter
    def ano(self, valor: int) -> None:
        if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
            raise ValueError("O ano deve ser um inteiro positivo.")
        self.__ano = valor

    @property
    def quilometragem(self) -> float:
        return self.__quilometragem

    @quilometragem.setter
    def quilometragem(self, valor: float) -> None:
        numero = float(valor)
        if numero < 0:
            raise ValueError("A quilometragem não pode ser negativa.")
        atual = getattr(self, "_VeiculoBase__quilometragem", None)
        if atual is not None and numero < atual:
            raise ValueError("A quilometragem não pode ser reduzida.")
        self.__quilometragem = numero

    @property
    def km_ultima_revisao_preventiva(self) -> float:
        """Quilometragem registrada na revisão preventiva mais recente."""
        return self.__km_ultima_revisao_preventiva

    @km_ultima_revisao_preventiva.setter
    def km_ultima_revisao_preventiva(self, valor: float) -> None:
        numero = float(valor)
        if numero < 0 or numero > self.quilometragem:
            raise ValueError("A quilometragem da última revisão deve estar entre zero e a quilometragem atual.")
        self.__km_ultima_revisao_preventiva = numero

    @property
    def consumo_medio(self) -> float:
        return self.__consumo_medio

    @consumo_medio.setter
    def consumo_medio(self, valor: float) -> None:
        numero = float(valor)
        if numero < 0:
            raise ValueError("O consumo médio não pode ser negativo.")
        self.__consumo_medio = numero

    @property
    def status(self) -> StatusVeiculo:
        return self.__status

    @status.setter
    def status(self, valor: StatusVeiculo | str) -> None:
        self.__status = StatusVeiculo.normalizar(valor)

    @property
    def historico_eventos(self) -> list[dict[str, Any]]:
        return list(self._historico_eventos)

    @property
    def viagens(self) -> list[Any]:
        return list(self._historico_viagens)

    def adicionar_viagem(self, viagem: Any) -> None:
        self._historico_viagens.append(viagem)
        self.registrar_evento({"evento": "viagem", "viagem": viagem})

    def atualizar_quilometragem(self, distancia: float) -> None:
        """Soma a distância percorrida à quilometragem acumulada do veículo.

        Args:
            distancia: Distância percorrida desde a última atualização, em km.

        Raises:
            ValueError: Se a distância for negativa.
        """
        incremento = float(distancia)
        if incremento < 0:
            raise ValueError("A distância percorrida não pode ser negativa.")
        self.__quilometragem += incremento

    def alterar_status(self, novo_status: StatusVeiculo | str) -> None:
        novo = StatusVeiculo.normalizar(novo_status)
        atual = self.status
        transicoes = {
            StatusVeiculo.ATIVO: {StatusVeiculo.MANUTENCAO, StatusVeiculo.INATIVO},
            StatusVeiculo.MANUTENCAO: {StatusVeiculo.ATIVO},
            StatusVeiculo.INATIVO: {StatusVeiculo.ATIVO},
        }
        if novo != atual and novo not in transicoes[atual]:
            raise ValueError(f"Transição de status inválida: {atual.value} → {novo.value}.")
        self.__status = novo
        self.registrar_evento({"evento": "alteração_status", "de": atual.value, "para": novo.value})

    def registrar_evento(self, evento: Any) -> None:
        if evento is None:
            raise ValueError("O evento não pode ser vazio.")
        self._historico_eventos.append(evento if isinstance(evento, dict) else {"evento": str(evento)})

    def __str__(self) -> str:
        return f"{self.marca} {self.modelo} - {self.placa} ({self.status.value})"

    def __repr__(self) -> str:
        return (f"{type(self).__name__}(placa={self.placa!r}, marca={self.marca!r}, "
                f"modelo={self.modelo!r}, ano={self.ano!r}, quilometragem={self.quilometragem!r})")

    def __eq__(self, outro: object) -> bool:
        if not isinstance(outro, VeiculoBase):
            return NotImplemented
        return self.placa == outro.placa

    def __lt__(self, outro: object) -> bool:
        if not isinstance(outro, VeiculoBase):
            return NotImplemented
        return self.quilometragem < outro.quilometragem

    def __iter__(self) -> Iterator[Any]:
        """Itera pelos eventos e históricos de manutenção do veículo."""
        yield from self._historico_eventos
        yield from self._historico_manutencoes

    def to_dict(self) -> dict[str, Any]:
        return {"placa": self.placa, "marca": self.marca, "modelo": self.modelo,
                "tipo": self.tipo, "ano": self.ano, "quilometragem": self.quilometragem,
                "consumo_medio": self.consumo_medio, "status": self.status.value,
                "historico_eventos": self.historico_eventos,
                "historico_manutencoes": [item.to_dict() if hasattr(item, "to_dict") else item
                                          for item in self._historico_manutencoes],
                "historico_abastecimentos": [item.to_dict() if hasattr(item, "to_dict") else item
                                              for item in self._historico_abastecimentos],
                "km_ultima_revisao_preventiva": self.km_ultima_revisao_preventiva}


class Carro(VeiculoBase):
    """Especialização que representa automóveis."""
    def __init__(self, placa: str, marca: str, modelo: str, ano: int, quilometragem: float,
                 consumo_medio: float, status: StatusVeiculo | str = StatusVeiculo.ATIVO) -> None:
        super().__init__(placa, marca, modelo, "Carro", ano, quilometragem, consumo_medio, status)


class Moto(VeiculoBase):
    """Especialização que representa motocicletas."""
    def __init__(self, placa: str, marca: str, modelo: str, ano: int, quilometragem: float,
                 consumo_medio: float, status: StatusVeiculo | str = StatusVeiculo.ATIVO) -> None:
        super().__init__(placa, marca, modelo, "Moto", ano, quilometragem, consumo_medio, status)


class Caminhao(VeiculoBase):
    """Especialização que representa caminhões."""
    def __init__(self, placa: str, marca: str, modelo: str, ano: int, quilometragem: float,
                 consumo_medio: float, status: StatusVeiculo | str = StatusVeiculo.ATIVO) -> None:
        super().__init__(placa, marca, modelo, "Caminhão", ano, quilometragem, consumo_medio, status)
