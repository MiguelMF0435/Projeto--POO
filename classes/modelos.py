"""Compatibilidade de imports antigos; os modelos ficam nos módulos especializados."""
from pessoa import PessoaBase, Motorista
from veiculos import VeiculoBase, Carro, Moto, Caminhao, StatusVeiculo
from viagem import Viagem
from registros import Manutencao, Abastecimento
from mixins import ManutenivelMixin, AbastecivelMixin

__all__ = ["PessoaBase", "Motorista", "VeiculoBase", "Carro", "Moto", "Caminhao",
           "StatusVeiculo", "Viagem", "Manutencao", "Abastecimento",
           "ManutenivelMixin", "AbastecivelMixin"]
