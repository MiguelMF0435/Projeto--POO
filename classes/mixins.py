"""Mixins para capacidades de manutenção e abastecimento."""
from __future__ import annotations
from typing import Any


class ManutenivelMixin:
    """Adiciona histórico e operações de manutenção a uma classe."""
    def _inicializar_manutencoes(self) -> None:
        self._historico_manutencoes: list[Any] = []

    @property
    def manutencoes(self) -> list[Any]:
        return list(self._historico_manutencoes)

    def registrar_manutencao(self, manutencao: Any) -> None:
        if manutencao is None:
            raise ValueError("A manutenção não pode ser vazia.")
        self._historico_manutencoes.append(manutencao)
        self.alterar_status("MANUTENCAO")

    def concluir_manutencao(self, manutencao: Any = None) -> None:
        if self.status != "MANUTENCAO":
            raise ValueError("O veículo não está em manutenção.")
        if manutencao is not None and hasattr(manutencao, "status"):
            manutencao.status = "concluida"
        self.alterar_status("ATIVO")


class AbastecivelMixin:
    """Adiciona histórico e operação de abastecimento a uma classe."""
    def _inicializar_abastecimentos(self) -> None:
        self._historico_abastecimentos: list[Any] = []

    @property
    def abastecimentos(self) -> list[Any]:
        return list(self._historico_abastecimentos)

    def abastecer(self, abastecimento: Any) -> None:
        if abastecimento is None:
            raise ValueError("O abastecimento não pode ser vazio.")
        if self.status != "ATIVO":
            raise ValueError("Não é permitido abastecer veículo inativo ou em manutenção.")
        self._historico_abastecimentos.append(abastecimento)
        self.registrar_evento({"evento": "abastecimento", "registro": abastecimento})
