class ManutenivelMixin:
    """Adiciona ao veículo a capacidade de registrar manutenções."""

    def registrar_manutencao(self, manutencao):
        if not hasattr(self, "_historico_manutencoes"):
            self._historico_manutencoes = []
        self._historico_manutencoes.append(manutencao)

    @property
    def historico_manutencoes(self):
        return list(getattr(self, "_historico_manutencoes", []))


class AbastecivelMixin:
    """Adiciona ao veículo a capacidade de registrar abastecimentos."""

    def abastecer(self, abastecimento):
        if not hasattr(self, "_historico_abastecimentos"):
            self._historico_abastecimentos = []
        self._historico_abastecimentos.append(abastecimento)

    @property
    def historico_abastecimentos(self):
        return list(getattr(self, "_historico_abastecimentos", []))
