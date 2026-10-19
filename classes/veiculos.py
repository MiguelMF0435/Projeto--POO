from mixins import ManutenivelMixin
from mixins import AbastecivelMixin

class VeiculoBase(ManutenivelMixin, AbastecivelMixin):
    """
    Classe base para representar um veículo da frota.

    Contém as características comuns aos veículos e utiliza
    os mixins ManutenivelMixin e AbastecivelMixin para fornecer
    funcionalidades relacionadas à manutenção e abastecimento.
    """

    def __init__(
        self,
        placa,
        marca,
        modelo,
        tipo,
        ano,
        quilometragem,
        consumo_medio,
        status
    ):
        self.__placa = placa
        self.__marca = marca
        self.__modelo = modelo
        self.__tipo = tipo
        self.__ano = ano
        self.__quilometragem = quilometragem
        self.__consumo_medio = consumo_medio
        self.__status = status

    # =========================
    # placa
    # =========================

    @property
    def placa(self):
        return self.__placa

    @placa.setter
    def placa(self, valor):
        if not valor:
            raise ValueError("A placa não pode ser vazia.")

        self.__placa = valor

    # =========================
    # marca
    # =========================

    @property
    def marca(self):
        return self.__marca

    @marca.setter
    def marca(self, valor):
        if not valor:
            raise ValueError("A marca não pode ser vazia.")

        self.__marca = valor

    # =========================
    # modelo
    # =========================

    @property
    def modelo(self):
        return self.__modelo

    @modelo.setter
    def modelo(self, valor):
        if not valor:
            raise ValueError("O modelo não pode ser vazio.")

        self.__modelo = valor

    # =========================
    # tipo
    # =========================

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, valor):
        if not valor:
            raise ValueError("O tipo não pode ser vazio.")

        self.__tipo = valor

    # =========================
    # ano
    # =========================

    @property
    def ano(self):
        return self.__ano

    @ano.setter
    def ano(self, valor):
        if valor <= 0:
            raise ValueError("O ano deve ser válido.")

        self.__ano = valor

    # =========================
    # quilometragem
    # =========================

    @property
    def quilometragem(self):
        return self.__quilometragem

    @quilometragem.setter
    def quilometragem(self, valor):
        if valor < 0:
            raise ValueError(
                "A quilometragem não pode ser negativa."
            )

        self.__quilometragem = valor

    # =========================
    # consumo médio
    # =========================

    @property
    def consumo_medio(self):
        return self.__consumo_medio

    @consumo_medio.setter
    def consumo_medio(self, valor):
        if valor < 0:
            raise ValueError(
                "O consumo médio não pode ser negativo."
            )

        self.__consumo_medio = valor

    # =========================
    # status
    # =========================

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, valor):
        if not valor:
            raise ValueError("O status não pode ser vazio.")

        self.__status = valor

    # =========================
    # métodos
    # =========================

    def atualizar_quilometragem(self, nova_quilometragem):
        """
        Atualiza a quilometragem do veículo.
        """

        if nova_quilometragem < self.__quilometragem:
            raise ValueError(
                "A nova quilometragem não pode ser menor que a atual."
            )

        self.__quilometragem = nova_quilometragem

    def alterar_status(self, novo_status):
        """
        Altera o status atual do veículo.
        """

        if not novo_status:
            raise ValueError("O status não pode ser vazio.")

        self.__status = novo_status

    def registrar_evento(self):
        """
        Registra um evento relacionado ao veículo.
        """
        pass

    def __str__(self):
        return f"{self.__marca} {self.__modelo} - {self.__placa}"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"placa='{self.__placa}', "
            f"marca='{self.__marca}', "
            f"modelo='{self.__modelo}', "
            f"ano={self.__ano})"
        )

    def __eq__(self, outro):
        if not isinstance(outro, VeiculoBase):
            return NotImplemented

        return self.__placa == outro.__placa

    def __lt__(self, outro):
        if not isinstance(outro, VeiculoBase):
            return NotImplemented

        return self.__quilometragem < outro.__quilometragem

    def __iter__(self):
        yield self.__placa
        yield self.__marca
        yield self.__modelo
        yield self.__tipo
        yield self.__ano
        yield self.__quilometragem
        yield self.__consumo_medio
        yield self.__status


class Carro(VeiculoBase):
    """
    Representa um carro da frota.

    Herda os atributos e comportamentos da classe VeiculoBase.
    """

    def __init__(
        self,
        placa,
        marca,
        modelo,
        ano,
        quilometragem,
        consumo_medio,
        status
    ):
        super().__init__(
            placa,
            marca,
            modelo,
            "Carro",
            ano,
            quilometragem,
            consumo_medio,
            status
        )


class Moto(VeiculoBase):
    """
    Representa uma motocicleta da frota.

    Herda os atributos e comportamentos da classe VeiculoBase.
    """

    def __init__(
        self,
        placa,
        marca,
        modelo,
        ano,
        quilometragem,
        consumo_medio,
        status
    ):
        super().__init__(
            placa,
            marca,
            modelo,
            "Moto",
            ano,
            quilometragem,
            consumo_medio,
            status
        )


class Caminhao(VeiculoBase):
    """
    Representa um caminhão da frota.

    Herda os atributos e comportamentos da classe VeiculoBase.
    """

    def __init__(
        self,
        placa,
        marca,
        modelo,
        ano,
        quilometragem,
        consumo_medio,
        status
    ):
        super().__init__(
            placa,
            marca,
            modelo,
            "Caminhão",
            ano,
            quilometragem,
            consumo_medio,
            status
        )

