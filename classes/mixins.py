"""Mixins para funcionalidades compartilhadas por veículos."""
class ManutenivelMixin:
    def _inicializar_manutencoes(self):
        self._manutencoes = []

    @property
    def manutencoes(self):
        return list(self._manutencoes)

    def registrar_manutencao(self, manutencao):
        if manutencao is None:
            raise ValueError("A manutenção não pode ser vazia.")
        self._manutencoes.append(manutencao)
        self.alterar_status("MANUTENCAO")

    def concluir_manutencao(self, manutencao=None):
        if self.status != "MANUTENCAO":
            raise ValueError("O veículo não está em manutenção.")
        if manutencao is not None and hasattr(manutencao, "status"):
            manutencao.status = "concluida"
        self.alterar_status("ATIVO")


class AbastecivelMixin:
    def _inicializar_abastecimentos(self):
        self._abastecimentos = []

    @property
    def abastecimentos(self):
        return list(self._abastecimentos)

    def abastecer(self, abastecimento):
        if abastecimento is None:
            raise ValueError("O abastecimento não pode ser vazio.")
        if self.status in ("INATIVO", "MANUTENCAO"):
            raise ValueError("Não é permitido abastecer veículo inativo ou em manutenção.")
        self._abastecimentos.append(abastecimento)
