import pytest
from veiculos import VeiculoBase, Carro, Moto, Caminhao
from pessoa import Motorista
from viagem import Viagem


def criar_carro(placa="ABC1D23", km=1000):
    return Carro(placa, "Fiat", "Argo", 2022, km, 12.0, "ATIVO")


def test_subclasses_definem_tipo_correto():
    assert criar_carro().tipo == "Carro"
    assert Moto("MOT1A23", "Honda", "CG", 2021, 500, 30, "ATIVO").tipo == "Moto"
    assert Caminhao("CAM1A23", "Volvo", "FH", 2020, 50000, 4, "ATIVO").tipo == "Caminhão"


def test_placa_e_identificador_de_igualdade():
    assert criar_carro("ABC1D23") == criar_carro("ABC1D23", km=2000)
    assert criar_carro("ABC1D23") != criar_carro("XYZ9Z99")


def test_veiculos_comparam_quilometragem():
    assert criar_carro(km=100) < criar_carro(km=200)


def test_atualizar_quilometragem_aceita_valor_maior():
    carro = criar_carro(km=100)
    carro.atualizar_quilometragem(150)
    assert carro.quilometragem == 150


def test_atualizar_quilometragem_nao_aceita_reducao():
    carro = criar_carro(km=100)
    with pytest.raises(ValueError, match="menor que a atual"):
        carro.atualizar_quilometragem(99)


def test_quilometragem_negativa_nao_e_aceita():
    carro = criar_carro()
    with pytest.raises(ValueError, match="negativa"):
        carro.quilometragem = -1


def test_ano_invalido_nao_e_aceito():
    carro = criar_carro()
    with pytest.raises(ValueError, match="ano"):
        carro.ano = 0


def test_motorista_nao_aceita_experiencia_negativa():
    motorista = Motorista("Ana", "123", "Motorista", "B", 2, True, [])
    with pytest.raises(ValueError, match="negativa"):
        motorista.experiencia_anos = -1


def test_viagem_nao_aceita_distancia_negativa():
    motorista = Motorista("Ana", "123", "Motorista", "B", 2, True, [])
    viagem = Viagem(motorista, criar_carro(), "A", "B", 10, "2026-01-01")
    with pytest.raises(ValueError, match="negativa"):
        viagem.distancia = -1
