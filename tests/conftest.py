"""Fixtures compartilhadas pelos testes automatizados do projeto."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSES_DIR = ROOT / "classes"
if str(CLASSES_DIR) not in sys.path:
    sys.path.insert(0, str(CLASSES_DIR))

import pytest
import main as app
from banco import BancoDeDados


@pytest.fixture
def sistema(tmp_path, monkeypatch):
    """Redireciona banco e configurações para arquivos temporários."""
    banco = BancoDeDados(tmp_path / "base_de_dados.json")
    monkeypatch.setattr(app, "banco", banco)
    monkeypatch.setattr(app, "SETTINGS_PATH", tmp_path / "settings.json")
    banco.salvar(banco._estrutura_vazia())
    app.carregar_configuracoes()
    return banco


@pytest.fixture
def veiculo_ativo(sistema):
    veiculo = {
        "placa": "ABC1D23", "marca": "Fiat", "modelo": "Argo",
        "tipo": "Carro", "ano": 2022, "quilometragem": 1000.0,
        "consumo_medio": 12.0, "status": "ATIVO",
        "historico_eventos": [], "km_ultima_revisao_preventiva": 1000.0,
    }
    sistema.adicionar("veiculos", veiculo)
    return veiculo


@pytest.fixture
def motorista_b(sistema):
    motorista = {
        "nome": "Ana Silva", "cpf": "12345678900", "funcao": "Motorista",
        "categoria_cnh": "B", "experiencia_anos": 3,
        "disponibilidade": True, "historico_viagens": [],
    }
    sistema.adicionar("motoristas", motorista)
    return motorista


def fornecer_entradas(monkeypatch, *entradas):
    iterator = iter(entradas)
    monkeypatch.setattr("builtins.input", lambda _="": next(iterator))
