from mixins import ManutenivelMixin, AbastecivelMixin


class VeiculoBase(ManutenivelMixin, AbastecivelMixin):
    """Classe base dos veículos da frota."""

    def __init__(self, placa, marca, modelo, tipo, ano,
                 quilometragem, consumo_medio, status):
        self.placa = placa
        self.marca = marca
        self.modelo = modelo
        self.tipo = tipo
        self.ano = ano
        self.quilometragem = quilometragem
        self.consumo_medio = consumo_medio
        self.status = status
        self._viagens = []
        self._historico_manutencoes = []
        self._historico_abastecimentos = []

    @property
    def placa(self): return self.__placa
    @placa.setter
    def placa(self, valor):
        if not valor: raise ValueError("A placa não pode ser vazia.")
        self.__placa = valor.strip().upper()

    @property
    def marca(self): return self.__marca
    @marca.setter
    def marca(self, valor):
        if not valor: raise ValueError("A marca não pode ser vazia.")
        self.__marca = valor

    @property
    def modelo(self): return self.__modelo
    @modelo.setter
    def modelo(self, valor):
        if not valor: raise ValueError("O modelo não pode ser vazio.")
        self.__modelo = valor

    @property
    def tipo(self): return self.__tipo
    @tipo.setter
    def tipo(self, valor):
        if not valor: raise ValueError("O tipo não pode ser vazio.")
        self.__tipo = valor

    @property
    def ano(self): return self.__ano
    @ano.setter
    def ano(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("O ano deve ser um inteiro positivo.")
        self.__ano = valor

    @property
    def quilometragem(self): return self.__quilometragem
    @quilometragem.setter
    def quilometragem(self, valor):
        if valor < 0: raise ValueError("A quilometragem não pode ser negativa.")
        self.__quilometragem = float(valor)

    @property
    def consumo_medio(self): return self.__consumo_medio
    @consumo_medio.setter
    def consumo_medio(self, valor):
        if valor < 0: raise ValueError("O consumo médio não pode ser negativo.")
        self.__consumo_medio = float(valor)

    @property
    def status(self): return self.__status
    @status.setter
    def status(self, valor):
        if not valor: raise ValueError("O status não pode ser vazio.")
        self.__status = valor

    @property
    def viagens(self):
        return list(self._viagens)

    def adicionar_viagem(self, viagem):
        self._viagens.append(viagem)

    def atualizar_quilometragem(self, nova_quilometragem):
        if nova_quilometragem < self.__quilometragem:
            raise ValueError("A nova quilometragem não pode ser menor que a atual.")
        self.__quilometragem = float(nova_quilometragem)

    def alterar_status(self, novo_status):
        if not novo_status: raise ValueError("O status não pode ser vazio.")
        self.__status = novo_status

    def registrar_evento(self, evento):
        """Registra evento genérico na lista de viagens/eventos."""
        if not hasattr(self, "_eventos"):
            self._eventos = []
        self._eventos.append(evento)

    def __str__(self):
        return f"{self.__marca} {self.__modelo} - {self.__placa}"

    def __repr__(self):
        return (f"{type(self).__name__}(placa={self.__placa!r}, "
                f"marca={self.__marca!r}, modelo={self.__modelo!r}, ano={self.__ano})")

    def __eq__(self, outro):
        if not isinstance(outro, VeiculoBase): return NotImplemented
        return self.__placa == outro.__placa

    def __lt__(self, outro):
        if not isinstance(outro, VeiculoBase): return NotImplemented
        return self.__quilometragem < outro.__quilometragem

    def __iter__(self):
        yield from (self.__placa, self.__marca, self.__modelo, self.__tipo,
                    self.__ano, self.__quilometragem, self.__consumo_medio,
                    self.__status)


class Carro(VeiculoBase):
    def __init__(self, placa, marca, modelo, ano, quilometragem, consumo_medio, status):
        super().__init__(placa, marca, modelo, "Carro", ano, quilometragem, consumo_medio, status)


class Moto(VeiculoBase):
    def __init__(self, placa, marca, modelo, ano, quilometragem, consumo_medio, status):
        super().__init__(placa, marca, modelo, "Moto", ano, quilometragem, consumo_medio, status)


class Caminhao(VeiculoBase):
    def __init__(self, placa, marca, modelo, ano, quilometragem, consumo_medio, status):
        super().__init__(placa, marca, modelo, "Caminhão", ano, quilometragem, consumo_medio, status)
