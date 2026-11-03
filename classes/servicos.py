"""Serviços de aplicação: regras de negócio independentes da CLI."""
from __future__ import annotations
from typing import Any
from tests.exceptions import AlocacaoInvalidaError, PoliticaNaoAtendidaError
from pessoa import Motorista
from veiculos import StatusVeiculo, VeiculoBase


class FrotaService:
    """Centraliza validações de alocação e políticas operacionais da frota."""
    @staticmethod
    def validar_veiculo(veiculo: VeiculoBase, configuracao: dict[str, Any],
                        km_ultima_revisao: float = 0) -> None:
        if veiculo.status != StatusVeiculo.ATIVO:
            raise AlocacaoInvalidaError("Veículo em manutenção ou inativo não pode ser alocado.")
        limite = float(configuracao["limite_km_revisao_preventiva"])
        if veiculo.quilometragem - float(km_ultima_revisao) >= limite:
            raise PoliticaNaoAtendidaError(
                "Revisão preventiva obrigatória. Registre a manutenção antes de uma nova viagem."
            )

    @staticmethod
    def validar_motorista(veiculo: VeiculoBase, motorista: Motorista,
                          configuracao: dict[str, Any]) -> None:
        if not motorista.disponibilidade:
            raise AlocacaoInvalidaError("O motorista não está disponível.")
        if not motorista.verificar_compatibilidade(veiculo.tipo, configuracao):
            raise AlocacaoInvalidaError(
                f"CNH {motorista.categoria_cnh} incompatível com {veiculo.tipo}."
            )

    @staticmethod
    def consumo_fora_da_faixa(tipo: str, consumo: float,
                              configuracao: dict[str, Any]) -> bool:
        minimo = float(configuracao["consumo_minimo_km_l"].get(tipo, 0))
        maximo = float(configuracao["consumo_maximo_km_l"].get(tipo, float("inf")))
        return consumo > 0 and not minimo <= consumo <= maximo
