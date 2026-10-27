import pytest
import main as app
from exceptions import AlocacaoInvalidaError, ManutencaoInvalidaError, PoliticaNaoAtendidaError
from conftest import fornecer_entradas


def test_compatibilidade_cnh_moto():
    assert app.compatibilidade_cnh("A", "Moto")
    assert not app.compatibilidade_cnh("B", "Moto")


def test_compatibilidade_cnh_carro():
    assert app.compatibilidade_cnh("B", "Carro")
    assert app.compatibilidade_cnh("E", "Carro")
    assert not app.compatibilidade_cnh("A", "Carro")


def test_compatibilidade_cnh_caminhao():
    assert app.compatibilidade_cnh("C", "Caminhão")
    assert app.compatibilidade_cnh("D", "Caminhao")
    assert not app.compatibilidade_cnh("B", "Caminhão")


def test_viagem_atualiza_km_e_historicos(sistema, veiculo_ativo, motorista_b, monkeypatch, capsys):
    fornecer_entradas(monkeypatch, "abc1d23", "12345678900", "Juazeiro", "Crato", "25")
    app.registrar_viagem()
    dados = sistema.carregar()
    assert dados["veiculos"][0]["quilometragem"] == 1025.0
    assert len(dados["viagens"]) == 1
    assert len(dados["motoristas"][0]["historico_viagens"]) == 1
    assert "Viagem registrada" in capsys.readouterr().out


def test_viagem_bloqueia_cnh_incompativel(sistema, veiculo_ativo, motorista_b, monkeypatch):
    motorista_b["categoria_cnh"] = "A"
    sistema.salvar({**sistema.carregar(), "motoristas": [motorista_b]})
    fornecer_entradas(monkeypatch, "ABC1D23", "12345678900")
    with pytest.raises(AlocacaoInvalidaError, match="incompatível"):
        app.registrar_viagem()
    assert sistema.listar("viagens") == []


def test_viagem_bloqueia_veiculo_inativo(sistema, veiculo_ativo, motorista_b, monkeypatch):
    veiculo_ativo["status"] = "INATIVO"
    sistema.salvar({**sistema.carregar(), "veiculos": [veiculo_ativo]})
    fornecer_entradas(monkeypatch, "ABC1D23")
    with pytest.raises(AlocacaoInvalidaError):
        app.registrar_viagem()


def test_viagem_bloqueia_veiculo_em_manutencao(sistema, veiculo_ativo, monkeypatch):
    veiculo_ativo["status"] = "MANUTENCAO"
    sistema.salvar({**sistema.carregar(), "veiculos": [veiculo_ativo]})
    fornecer_entradas(monkeypatch, "ABC1D23")
    with pytest.raises(AlocacaoInvalidaError):
        app.registrar_viagem()


def test_viagem_bloqueia_motorista_indisponivel(sistema, veiculo_ativo, motorista_b, monkeypatch):
    motorista_b["disponibilidade"] = False
    sistema.salvar({**sistema.carregar(), "motoristas": [motorista_b]})
    fornecer_entradas(monkeypatch, "ABC1D23", "12345678900")
    with pytest.raises(AlocacaoInvalidaError, match="disponível"):
        app.registrar_viagem()


def test_viagem_bloqueia_quando_revisao_venceu(sistema, veiculo_ativo, motorista_b, monkeypatch):
    veiculo_ativo["quilometragem"] = 11000
    sistema.salvar({**sistema.carregar(), "veiculos": [veiculo_ativo]})
    fornecer_entradas(monkeypatch, "ABC1D23")
    with pytest.raises(PoliticaNaoAtendidaError, match="Revisão preventiva"):
        app.registrar_viagem()


def test_manutencao_altera_status_do_veiculo(sistema, veiculo_ativo, monkeypatch, capsys):
    fornecer_entradas(monkeypatch, "ABC1D23", "1", "250", "Troca de óleo")
    app.registrar_manutencao()
    assert sistema.listar("veiculos")[0]["status"] == "MANUTENCAO"
    assert sistema.listar("manutencoes")[0]["status"] == "em_andamento"
    assert "MANUTENCAO" in capsys.readouterr().out


def test_manutencao_nao_pode_iniciar_em_veiculo_inativo(sistema, veiculo_ativo, monkeypatch):
    veiculo_ativo["status"] = "INATIVO"
    sistema.salvar({**sistema.carregar(), "veiculos": [veiculo_ativo]})
    fornecer_entradas(monkeypatch, "ABC1D23")
    with pytest.raises(ManutencaoInvalidaError):
        app.registrar_manutencao()


def test_concluir_manutencao_libera_veiculo_e_atualiza_revisao(sistema, veiculo_ativo, monkeypatch):
    veiculo_ativo["status"] = "MANUTENCAO"
    veiculo_ativo["quilometragem"] = 1200
    dados = sistema.carregar()
    dados["veiculos"] = [veiculo_ativo]
    dados["manutencoes"] = [{"veiculo_placa": "ABC1D23", "tipo": "preventiva", "status": "em_andamento"}]
    sistema.salvar(dados)
    fornecer_entradas(monkeypatch, "ABC1D23")
    app.concluir_manutencao()
    atualizado = sistema.listar("veiculos")[0]
    assert atualizado["status"] == "ATIVO"
    assert atualizado["km_ultima_revisao_preventiva"] == 1200
    assert sistema.listar("manutencoes")[0]["status"] == "concluida"


def test_abastecimento_registra_primeiro_evento(sistema, veiculo_ativo, monkeypatch):
    fornecer_entradas(monkeypatch, "ABC1D23", "Gasolina", "30", "180", "1000")
    app.registrar_abastecimento()
    abastecimentos = sistema.listar("abastecimentos")
    assert len(abastecimentos) == 1
    assert abastecimentos[0]["litros"] == 30
    assert abastecimentos[0]["consumo_calculado_km_l"] is None


def test_abastecimento_calcula_consumo_com_registro_anterior(sistema, veiculo_ativo, monkeypatch):
    sistema.adicionar("abastecimentos", {"veiculo_placa": "ABC1D23", "quilometragem": 1000})
    fornecer_entradas(monkeypatch, "ABC1D23", "Gasolina", "40", "240", "1480")
    app.registrar_abastecimento()
    atualizado = sistema.listar("veiculos")[0]
    assert atualizado["consumo_medio"] == 12.0
    assert sistema.listar("abastecimentos")[-1]["consumo_calculado_km_l"] == 12.0


def test_abastecimento_bloqueia_veiculo_nao_ativo(sistema, veiculo_ativo, monkeypatch):
    veiculo_ativo["status"] = "MANUTENCAO"
    sistema.salvar({**sistema.carregar(), "veiculos": [veiculo_ativo]})
    fornecer_entradas(monkeypatch, "ABC1D23")
    with pytest.raises(ValueError, match="ATIVOS"):
        app.registrar_abastecimento()


def test_abastecimento_rejeita_km_inferior_e_pede_novo_valor(sistema, veiculo_ativo, monkeypatch, capsys):
    fornecer_entradas(monkeypatch, "ABC1D23", "Gasolina", "20", "100", "999", "1000")
    app.registrar_abastecimento()
    assert "Informe um valor igual ou superior a 1000.0" in capsys.readouterr().out
    assert sistema.listar("abastecimentos")[0]["quilometragem"] == 1000
