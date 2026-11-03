"""Repositório de persistência JSON (padrão Repository)."""
from __future__ import annotations
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class RepositorioBase(ABC):
    """Contrato independente do mecanismo de persistência."""
    @abstractmethod
    def carregar(self) -> dict[str, list[dict[str, Any]]]: ...
    @abstractmethod
    def salvar(self, dados: dict[str, list[dict[str, Any]]]) -> None: ...
    @abstractmethod
    def adicionar(self, categoria: str, registro: dict[str, Any]) -> None: ...
    @abstractmethod
    def listar(self, categoria: str) -> list[dict[str, Any]]: ...


class RepositorioJSON(RepositorioBase):
    """Implementação concreta do repositório utilizando arquivo JSON."""
    CATEGORIAS = ("veiculos", "motoristas", "viagens", "manutencoes", "abastecimentos")

    def __init__(self, arquivo: str | Path | None = None) -> None:
        self._arquivo = Path(arquivo) if arquivo else Path(__file__).resolve().parent / "base_de_dados.json"

    def _estrutura_vazia(self) -> dict[str, list]:
        return {categoria: [] for categoria in self.CATEGORIAS}

    def carregar(self) -> dict[str, list[dict[str, Any]]]:
        if not self._arquivo.exists():
            dados = self._estrutura_vazia()
            self.salvar(dados)
            return dados
        try:
            with self._arquivo.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except json.JSONDecodeError as erro:
            raise ValueError(f"O arquivo {self._arquivo} contém JSON inválido; ele foi preservado.") from erro
        except OSError as erro:
            from tests.exceptions import RepositorioError
            raise RepositorioError(f"Não foi possível ler {self._arquivo}: {erro}") from erro
        if not isinstance(dados, dict):
            raise ValueError("A estrutura do banco JSON deve ser um objeto.")
        estrutura = self._estrutura_vazia()
        for categoria in self.CATEGORIAS:
            registros = dados.get(categoria, [])
            if not isinstance(registros, list) or any(not isinstance(item, dict) for item in registros):
                raise ValueError(f"A categoria '{categoria}' deve ser uma lista de objetos.")
            estrutura[categoria] = registros
        return estrutura

    def salvar(self, dados: dict[str, list[dict[str, Any]]]) -> None:
        self._arquivo.parent.mkdir(parents=True, exist_ok=True)
        estrutura = self._estrutura_vazia()
        for categoria in self.CATEGORIAS:
            registros = dados.get(categoria, [])
            if not isinstance(registros, list):
                raise ValueError(f"A categoria '{categoria}' deve ser uma lista.")
            estrutura[categoria] = registros
        conteudo = json.dumps(estrutura, ensure_ascii=False, indent=4, allow_nan=False)
        temporario = self._arquivo.with_suffix(self._arquivo.suffix + ".tmp")
        try:
            temporario.write_text(conteudo, encoding="utf-8")
            temporario.replace(self._arquivo)
        except OSError as erro:
            from tests.exceptions import RepositorioError
            temporario.unlink(missing_ok=True)
            raise RepositorioError(f"Não foi possível salvar {self._arquivo}: {erro}") from erro

    def adicionar(self, categoria: str, registro: dict[str, Any]) -> None:
        if categoria not in self.CATEGORIAS:
            raise ValueError(f"Categoria inválida: {categoria}")
        if not isinstance(registro, dict):
            raise TypeError("O registro deve ser um dicionário.")
        dados = self.carregar()
        dados[categoria].append(registro)
        self.salvar(dados)

    def listar(self, categoria: str) -> list[dict[str, Any]]:
        if categoria not in self.CATEGORIAS:
            raise ValueError(f"Categoria inválida: {categoria}")
        return self.carregar()[categoria]

    def popular_seed(self) -> None:
        """Insere dados demonstrativos somente quando o banco está vazio."""
        dados = self.carregar()
        if any(dados[categoria] for categoria in self.CATEGORIAS):
            return
        dados["veiculos"] = [{"placa": "ABC1D23", "marca": "Fiat", "modelo": "Argo",
            "tipo": "Carro", "ano": 2022, "quilometragem": 12000.0,
            "consumo_medio": 12.0, "status": "ATIVO", "historico_eventos": [],
            "km_ultima_revisao_preventiva": 10000.0}]
        dados["motoristas"] = [{"nome": "Ana Silva", "cpf": "12345678901", "funcao": "Motorista",
            "categoria_cnh": "B", "experiencia_anos": 3, "disponibilidade": True,
            "historico_viagens": []}]
        self.salvar(dados)


class BancoDeDados(RepositorioJSON):
    """Nome mantido por compatibilidade com versões anteriores do projeto."""


class RepositorioSQLite(RepositorioBase):
    """Implementação alternativa do contrato Repository usando SQLite."""
    def __init__(self, arquivo: str | Path = "frota.sqlite3") -> None:
        import sqlite3
        self._sqlite3 = sqlite3
        self._arquivo = str(arquivo)
        with self._conectar() as conexao:
            for categoria in RepositorioJSON.CATEGORIAS:
                conexao.execute(
                    f'CREATE TABLE IF NOT EXISTS "{categoria}" '
                    '(id INTEGER PRIMARY KEY AUTOINCREMENT, registro TEXT NOT NULL)'
                )

    def _conectar(self) -> Any:
        """Abre uma conexão SQLite para uma operação do repositório."""
        return self._sqlite3.connect(self._arquivo)

    def carregar(self) -> dict[str, list[dict[str, Any]]]:
        dados = {categoria: [] for categoria in RepositorioJSON.CATEGORIAS}
        try:
            with self._conectar() as conexao:
                for categoria in dados:
                    linhas = conexao.execute(f'SELECT registro FROM "{categoria}" ORDER BY id').fetchall()
                    dados[categoria] = [json.loads(linha[0]) for linha in linhas]
        except self._sqlite3.Error as erro:
            from tests.exceptions import RepositorioError
            raise RepositorioError(f"Falha ao consultar SQLite: {erro}") from erro
        return dados

    def salvar(self, dados: dict[str, list[dict[str, Any]]]) -> None:
        try:
            with self._conectar() as conexao:
                for categoria in RepositorioJSON.CATEGORIAS:
                    conexao.execute(f'DELETE FROM "{categoria}"')
                    conexao.executemany(
                        f'INSERT INTO "{categoria}" (registro) VALUES (?)',
                        [(json.dumps(registro, ensure_ascii=False, allow_nan=False),)
                         for registro in dados.get(categoria, [])]
                    )
        except (self._sqlite3.Error, TypeError, ValueError) as erro:
            from tests.exceptions import RepositorioError
            raise RepositorioError(f"Falha ao salvar no SQLite: {erro}") from erro

    def adicionar(self, categoria: str, registro: dict[str, Any]) -> None:
        if categoria not in RepositorioJSON.CATEGORIAS:
            raise ValueError(f"Categoria inválida: {categoria}")
        with self._conectar() as conexao:
            conexao.execute(f'INSERT INTO "{categoria}" (registro) VALUES (?)',
                            (json.dumps(registro, ensure_ascii=False, allow_nan=False),))

    def listar(self, categoria: str) -> list[dict[str, Any]]:
        if categoria not in RepositorioJSON.CATEGORIAS:
            raise ValueError(f"Categoria inválida: {categoria}")
        with self._conectar() as conexao:
            linhas = conexao.execute(f'SELECT registro FROM "{categoria}" ORDER BY id').fetchall()
        return [json.loads(linha[0]) for linha in linhas]
