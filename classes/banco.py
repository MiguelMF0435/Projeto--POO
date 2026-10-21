import json
from pathlib import Path


class BancoDeDados:
    """Leitura e gravação dos registros em base_de_dados.json."""

    CATEGORIAS = (
        "veiculos", "motoristas", "viagens",
        "manutencoes", "abastecimentos"
    )

    def __init__(self, arquivo=None):
        self.__arquivo = (
            Path(arquivo) if arquivo
            else Path(__file__).resolve().parent / "base_de_dados.json"
        )

    def _estrutura_vazia(self):
        return {categoria: [] for categoria in self.CATEGORIAS}

    def carregar(self):
        if not self.__arquivo.exists():
            dados = self._estrutura_vazia()
            self.salvar(dados)
            return dados

        try:
            with self.__arquivo.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except json.JSONDecodeError as erro:
            raise ValueError(
                f"{self.__arquivo.name} contém JSON inválido. "
                "O arquivo foi preservado; corrija-o antes de continuar."
            ) from erro

        if not isinstance(dados, dict):
            raise ValueError("A estrutura do JSON deve ser um objeto.")

        estrutura = self._estrutura_vazia()
        for categoria in self.CATEGORIAS:
            registros = dados.get(categoria, [])
            if not isinstance(registros, list):
                raise ValueError(f"A categoria '{categoria}' deve ser uma lista.")
            estrutura[categoria] = registros
        return estrutura

    def salvar(self, dados):
        self.__arquivo.parent.mkdir(parents=True, exist_ok=True)
        estrutura = self._estrutura_vazia()
        for categoria in self.CATEGORIAS:
            estrutura[categoria] = dados.get(categoria, [])

        conteudo = json.dumps(
            estrutura, ensure_ascii=False, indent=4, allow_nan=False
        )
        temporario = self.__arquivo.with_suffix(".tmp")
        temporario.write_text(conteudo, encoding="utf-8")
        temporario.replace(self.__arquivo)

    def adicionar(self, categoria, registro):
        if categoria not in self.CATEGORIAS:
            raise ValueError(f"Categoria inválida: {categoria}")
        dados = self.carregar()
        dados[categoria].append(registro)
        self.salvar(dados)

    def listar(self, categoria):
        if categoria not in self.CATEGORIAS:
            raise ValueError(f"Categoria inválida: {categoria}")
        return self.carregar()[categoria]
