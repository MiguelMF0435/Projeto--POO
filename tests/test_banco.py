import json
import pytest
from banco import BancoDeDados


def test_banco_cria_estrutura_vazia_quando_arquivo_nao_existe(tmp_path):
    banco = BancoDeDados(tmp_path / "novo.json")
    dados = banco.carregar()
    assert set(dados) == set(BancoDeDados.CATEGORIAS)
    assert all(dados[categoria] == [] for categoria in BancoDeDados.CATEGORIAS)


def test_banco_salva_e_carrega_registros(tmp_path):
    banco = BancoDeDados(tmp_path / "dados.json")
    dados = banco._estrutura_vazia()
    dados["veiculos"].append({"placa": "ABC1D23"})
    banco.salvar(dados)
    assert banco.carregar()["veiculos"] == [{"placa": "ABC1D23"}]


def test_adicionar_e_listar_categoria(sistema):
    sistema.adicionar("motoristas", {"cpf": "123"})
    assert sistema.listar("motoristas") == [{"cpf": "123"}]


def test_categoria_invalida_ao_adicionar_gera_erro(sistema):
    with pytest.raises(ValueError):
        sistema.adicionar("aviões", {})


def test_categoria_invalida_ao_listar_gera_erro(sistema):
    with pytest.raises(ValueError):
        sistema.listar("aviões")


def test_json_corrompido_gera_erro_sem_sobrescrever_arquivo(tmp_path):
    caminho = tmp_path / "dados.json"
    caminho.write_text("{json inválido", encoding="utf-8")
    banco = BancoDeDados(caminho)
    with pytest.raises(ValueError, match="JSON inválido"):
        banco.carregar()
    assert caminho.read_text(encoding="utf-8") == "{json inválido"


def test_categoria_que_nao_e_lista_gera_erro(tmp_path):
    caminho = tmp_path / "dados.json"
    caminho.write_text(json.dumps({"veiculos": {}}), encoding="utf-8")
    with pytest.raises(ValueError, match="deve ser uma lista"):
        BancoDeDados(caminho).carregar()
