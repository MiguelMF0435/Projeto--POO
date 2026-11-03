"""Exceções de domínio para regras de negócio da frota."""
class ManutencaoInvalidaError(ValueError):
    """Indica uma operação de manutenção inválida."""

class AlocacaoInvalidaError(ValueError):
    """Indica que motorista ou veículo não pode ser alocado."""

class PoliticaNaoAtendidaError(ValueError):
    """Indica que uma política configurada não foi atendida."""

class RepositorioError(RuntimeError):
    """Indica falha de leitura ou gravação do repositório."""
