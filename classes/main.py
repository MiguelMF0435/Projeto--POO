
"""CLI do Sistema de Gerenciamento de Frota de Veículos."""

import sys
import json
from pathlib import Path
from datetime import datetime

PASTA_CLASSES = str(Path(__file__).resolve().parent)

if PASTA_CLASSES not in sys.path:
    sys.path.insert(0, PASTA_CLASSES)

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich.align import Align
from rich import box

from banco import BancoDeDados
from exceptions import (
    AlocacaoInvalidaError,
    ManutencaoInvalidaError,
    PoliticaNaoAtendidaError
)


# ============================================================
# CONFIGURAÇÕES E INICIALIZAÇÃO
# ============================================================

console = Console()
banco = BancoDeDados()

SETTINGS_PATH = Path(__file__).resolve().parent / "settings.json"


def carregar_configuracoes():
    """Carrega políticas configuráveis ou cria settings.json."""
    padrao = {
        "limite_km_revisao_preventiva": 10000,
        "consumo_minimo_km_l": {
            "Carro": 5.0,
            "Moto": 15.0,
            "Caminhão": 2.0
        },
        "consumo_maximo_km_l": {
            "Carro": 25.0,
            "Moto": 45.0,
            "Caminhão": 8.0
        },
        "custos_manutencao": {
            "preventiva": 250.0,
            "corretiva": 500.0
        },
        "cnh_minima": {
            "Moto": "A",
            "Carro": "B",
            "Caminhão": "C"
        }
    }

    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(
            json.dumps(padrao, ensure_ascii=False, indent=4),
            encoding="utf-8"
        )
        return padrao

    with SETTINGS_PATH.open("r", encoding="utf-8") as arquivo:
        config = json.load(arquivo)

    for chave, valor in padrao.items():
        config.setdefault(chave, valor)

    return config


# ============================================================
# INTERFACE VISUAL - RICH
# ============================================================

def exibir_cabecalho():
    """Exibe a identidade visual do sistema."""
    titulo = Text()
    titulo.append("FROTA", style="bold cyan")
    titulo.append(" MANAGER", style="bold white")
    titulo.append(
        "\nSistema de Gerenciamento de Veículos",
        style="dim"
    )

    console.print()
    console.print(
        Panel(
            Align.center(titulo),
            border_style="cyan",
            box=box.DOUBLE,
            padding=(1, 2)
        )
    )


def exibir_secao(titulo):
    """Exibe o título de uma operação."""
    console.print()
    console.print(
        Panel(
            f"[bold white]{titulo}[/bold white]",
            border_style="blue",
            box=box.ROUNDED,
            padding=(0, 2)
        )
    )


def exibir_menu(titulo, opcoes, descricao=None):
    """Exibe um menu organizado em tabela."""
    tabela = Table(
        show_header=False,
        box=box.SIMPLE_HEAVY,
        expand=True,
        border_style="cyan",
        padding=(0, 2)
    )

    tabela.add_column(
        "Opção",
        style="bold cyan",
        width=10,
        justify="center"
    )

    tabela.add_column("Descrição", style="white")

    for numero, descricao_opcao in opcoes:
        tabela.add_row(f"[{numero}]", descricao_opcao)

    conteudo = []

    if descricao:
        conteudo.append(Text(descricao, style="dim"))

    conteudo.append(tabela)

    console.print()
    console.print(
        Panel(
            Group(*conteudo),
            title=f"[bold cyan]{titulo}[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
    )


def sucesso(mensagem):
    console.print(f"\n[bold green]✓[/bold green] {mensagem}")


def erro(mensagem):
    console.print(f"\n[bold red]✗[/bold red] {mensagem}")


def aviso(mensagem):
    console.print(f"\n[bold yellow]![/bold yellow] {mensagem}")


def informacao(mensagem):
    console.print(f"\n[cyan]ℹ[/cyan] {mensagem}")


def pausar():
    """Aguarda o usuário antes de retornar ao menu."""
    console.input("\n[dim]Pressione ENTER para continuar...[/dim]")


def criar_tabela(titulo, colunas):
    """Cria uma tabela padronizada."""
    tabela = Table(
        title=f"[bold cyan]{titulo}[/bold cyan]",
        box=box.ROUNDED,
        show_lines=True,
        expand=True,
        border_style="cyan"
    )

    for coluna in colunas:
        tabela.add_column(
            coluna.replace("_", " ").title(),
            style="white",
            overflow="fold"
        )

    return tabela


# ============================================================
# FUNÇÕES DE ENTRADA DE DADOS
# ============================================================

def ler_texto(mensagem):
    while True:
        valor = Prompt.ask(f"[cyan]{mensagem}[/cyan]").strip()

        if valor:
            return valor

        erro("O campo não pode ficar vazio.")


def ler_int(mensagem, minimo=None):
    while True:
        try:
            valor = IntPrompt.ask(f"[cyan]{mensagem}[/cyan]")

            if minimo is not None and valor < minimo:
                aviso(
                    f"Informe um valor igual ou superior a {minimo}."
                )
                continue

            return valor

        except ValueError:
            erro("Informe um número inteiro válido.")


def ler_float(mensagem, minimo=None):
    while True:
        try:
            entrada = Prompt.ask(f"[cyan]{mensagem}[/cyan]")
            valor = float(entrada.replace(",", "."))

            if minimo is not None and valor < minimo:
                aviso(
                    f"Informe um valor igual ou superior a {minimo}."
                )
                continue

            return valor

        except ValueError:
            erro("Informe um número válido.")


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def normalizar_status(status):
    status = status.strip().upper().replace("Á", "A").replace("Ã", "A")

    aliases = {
        "ATIVO": "ATIVO",
        "DISPONIVEL": "ATIVO",
        "MANUTENCAO": "MANUTENCAO",
        "EM MANUTENCAO": "MANUTENCAO",
        "INATIVO": "INATIVO"
    }

    if status not in aliases:
        raise ValueError(
            "Status deve ser ATIVO, MANUTENCAO ou INATIVO."
        )

    return aliases[status]


def buscar_por_chave(categoria, chave, valor):
    for registro in banco.listar(categoria):
        if str(registro.get(chave, "")).upper() == str(valor).upper():
            return registro

    return None


def salvar_atualizacao(categoria, registro):
    dados = banco.carregar()

    chave = (
        "placa" if categoria == "veiculos"
        else "cpf" if categoria == "motoristas"
        else None
    )

    if chave:
        for i, item in enumerate(dados[categoria]):
            if item.get(chave) == registro.get(chave):
                dados[categoria][i] = registro
                break

    banco.salvar(dados)


def compatibilidade_cnh(categoria_cnh, tipo_veiculo):
    categoria = categoria_cnh.upper().strip()
    tipo = tipo_veiculo.lower().replace("ã", "a")

    if tipo == "moto":
        return categoria == "A"

    if tipo == "carro":
        return categoria in {"B", "C", "D", "E"}

    if tipo == "caminhao":
        return categoria in {"C", "D", "E"}

    return False


# ============================================================
# CADASTRO DE VEÍCULOS
# ============================================================

def cadastrar_veiculo():
    exibir_secao("CADASTRO DE VEÍCULO")

    opcoes = {
        "1": "Carro",
        "2": "Moto",
        "3": "Caminhão"
    }

    exibir_menu(
        "TIPO DE VEÍCULO",
        [
            ("1", "Carro"),
            ("2", "Moto"),
            ("3", "Caminhão")
        ]
    )

    tipo = Prompt.ask("[cyan]Selecione o tipo[/cyan]")

    if tipo not in opcoes:
        erro("Tipo inválido.")
        return

    placa = ler_texto("Placa").upper()

    if buscar_por_chave("veiculos", "placa", placa):
        erro("Já existe um veículo com essa placa.")
        return

    marca = ler_texto("Marca")
    modelo = ler_texto("Modelo")

    ano = ler_int("Ano", 1886)

    if ano > datetime.now().year + 1:
        erro("O ano informado é inválido.")
        return

    km = ler_float("Quilometragem", 0)
    consumo = ler_float("Consumo médio (km/l)", 0)

    dados = {
        "placa": placa,
        "marca": marca,
        "modelo": modelo,
        "tipo": opcoes[tipo],
        "ano": ano,
        "quilometragem": km,
        "consumo_medio": consumo,
        "status": "ATIVO",
        "historico_eventos": [
            {
                "data": datetime.now().isoformat(timespec="seconds"),
                "evento": "entrada"
            }
        ],
        "km_ultima_revisao_preventiva": km
    }

    banco.adicionar("veiculos", dados)

    sucesso("Veículo cadastrado como ATIVO e salvo.")


# ============================================================
# CADASTRO DE MOTORISTAS
# ============================================================

def cadastrar_motorista():
    exibir_secao("CADASTRO DE MOTORISTA")

    cpf = ler_texto("CPF").strip()

    if buscar_por_chave("motoristas", "cpf", cpf):
        erro("Já existe um motorista com esse CPF.")
        return

    nome = ler_texto("Nome")
    categoria = ler_texto("Categoria CNH (A, B, C, D ou E)").upper()

    if categoria not in {"A", "B", "C", "D", "E"}:
        erro("Categoria inválida.")
        return

    experiencia = ler_int("Experiência em anos", 0)

    disponibilidade = Prompt.ask(
        "[cyan]Está disponível?[/cyan]",
        choices=["s", "n"],
        default="s"
    ).lower()

    banco.adicionar(
        "motoristas",
        {
            "nome": nome,
            "cpf": cpf,
            "funcao": "Motorista",
            "categoria_cnh": categoria,
            "experiencia_anos": experiencia,
            "disponibilidade": disponibilidade == "s",
            "historico_viagens": []
        }
    )

    sucesso("Motorista cadastrado e salvo.")


# ============================================================
# LISTAGEM DE REGISTROS
# ============================================================

def listar_categoria(categoria, titulo):
    registros = banco.listar(categoria)

    if not registros:
        aviso(f"Nenhum registro de {titulo.lower()} encontrado.")
        return

    campos = list(registros[0].keys())

    tabela = Table(
        title=f"[bold cyan]{titulo.upper()}[/bold cyan]",
        box=box.ROUNDED,
        show_lines=True,
        expand=True,
        border_style="cyan"
    )

    tabela.add_column("#", style="dim", justify="center")

    for campo in campos:
        tabela.add_column(
            campo.replace("_", " ").title(),
            style="white",
            overflow="fold"
        )

    for indice, registro in enumerate(registros, 1):
        valores = []

        for campo in campos:
            valor = registro.get(campo, "-")

            if isinstance(valor, (dict, list)):
                valor = json.dumps(
                    valor,
                    ensure_ascii=False
                )

            if isinstance(valor, bool):
                valor = "Sim" if valor else "Não"

            valores.append(str(valor))

        tabela.add_row(str(indice), *valores)

    console.print()
    console.print(tabela)

    informacao(f"Total de registros: {len(registros)}")


# ============================================================
# REGISTRO DE VIAGENS
# ============================================================

def registrar_viagem():
    exibir_secao("REGISTRAR VIAGEM")

    placa = ler_texto("Placa do veículo").upper()
    veiculo = buscar_por_chave("veiculos", "placa", placa)

    if not veiculo:
        aviso("Veículo não encontrado.")
        return

    if veiculo.get("status") != "ATIVO":
        raise AlocacaoInvalidaError(
            "Veículo em manutenção ou inativo não pode ser alocado."
        )

    config = carregar_configuracoes()

    intervalo = float(config["limite_km_revisao_preventiva"])

    km_desde_revisao = (
        veiculo["quilometragem"]
        - veiculo.get("km_ultima_revisao_preventiva", 0)
    )

    if km_desde_revisao >= intervalo:
        raise PoliticaNaoAtendidaError(
            "Revisão preventiva obrigatória. "
            "Registre a manutenção antes de uma nova viagem."
        )

    cpf = ler_texto("CPF do motorista")

    motorista = buscar_por_chave("motoristas", "cpf", cpf)

    if not motorista:
        aviso("Motorista não encontrado.")
        return

    if not motorista.get("disponibilidade", False):
        raise AlocacaoInvalidaError(
            "O motorista não está disponível."
        )

    if not compatibilidade_cnh(
        motorista.get("categoria_cnh", ""),
        veiculo["tipo"]
    ):
        raise AlocacaoInvalidaError(
            f"CNH {motorista.get('categoria_cnh')} "
            f"incompatível com {veiculo['tipo']}."
        )

    origem = ler_texto("Origem")
    destino = ler_texto("Destino")
    distancia = ler_float("Distância percorrida (km)", 0.01)

    viagem = {
        "motorista_cpf": motorista["cpf"],
        "motorista_nome": motorista["nome"],
        "veiculo_placa": veiculo["placa"],
        "origem": origem,
        "destino": destino,
        "distancia": distancia,
        "data": datetime.now().isoformat(timespec="seconds")
    }

    dados = banco.carregar()
    dados["viagens"].append(viagem)

    veiculo["quilometragem"] = round(
        float(veiculo["quilometragem"]) + distancia,
        2
    )

    veiculo.setdefault("historico_eventos", []).append(
        {
            "data": viagem["data"],
            "evento": "saída/viagem",
            "distancia": distancia
        }
    )

    motorista.setdefault("historico_viagens", []).append(
        {
            "data": viagem["data"],
            "veiculo_placa": placa,
            "origem": origem,
            "destino": destino,
            "distancia": distancia
        }
    )

    for i, v in enumerate(dados["veiculos"]):
        if v["placa"] == placa:
            dados["veiculos"][i] = veiculo

    for i, m in enumerate(dados["motoristas"]):
        if m["cpf"] == cpf:
            dados["motoristas"][i] = motorista

    banco.salvar(dados)

    sucesso(
        f"Viagem registrada. Quilometragem atual: "
        f"{veiculo['quilometragem']:.1f} km."
    )

    if (
        veiculo["quilometragem"]
        - veiculo.get("km_ultima_revisao_preventiva", 0)
    ) >= intervalo:
        aviso(
            "A revisão preventiva está vencida. "
            "Não será possível registrar outra viagem até a revisão."
        )


# ============================================================
# MANUTENÇÕES
# ============================================================

def registrar_manutencao():
    exibir_secao("REGISTRAR MANUTENÇÃO")

    placa = ler_texto("Placa do veículo").upper()
    veiculo = buscar_por_chave("veiculos", "placa", placa)

    if not veiculo:
        aviso("Veículo não encontrado.")
        return

    if veiculo.get("status") == "INATIVO":
        raise ManutencaoInvalidaError(
            "Não é possível iniciar manutenção em veículo INATIVO."
        )

    if veiculo.get("status") == "MANUTENCAO":
        raise ManutencaoInvalidaError(
            "O veículo já está em manutenção. "
            "Conclua o serviço atual primeiro."
        )

    exibir_menu(
        "TIPO DE MANUTENÇÃO",
        [
            ("1", "Preventiva"),
            ("2", "Corretiva")
        ]
    )

    escolha = Prompt.ask("[cyan]Selecione o tipo[/cyan]")

    tipos = {
        "1": "preventiva",
        "2": "corretiva"
    }

    if escolha not in tipos:
        erro("Tipo inválido.")
        return

    tipo = tipos[escolha]

    config = carregar_configuracoes()

    custo_padrao = float(
        config["custos_manutencao"].get(tipo, 0)
    )

    custo = ler_float(
        f"Custo (padrão R$ {custo_padrao:.2f})",
        0
    )

    descricao = ler_texto("Descrição")

    data = datetime.now().isoformat(timespec="seconds")

    registro = {
        "data": data,
        "tipo": tipo,
        "custo": custo,
        "descricao": descricao,
        "veiculo_placa": placa,
        "status": "em_andamento"
    }

    dados = banco.carregar()
    dados["manutencoes"].append(registro)

    veiculo["status"] = "MANUTENCAO"

    veiculo.setdefault("historico_eventos", []).append(
        {
            "data": data,
            "evento": "manutenção iniciada",
            "tipo": tipo
        }
    )

    for i, v in enumerate(dados["veiculos"]):
        if v["placa"] == placa:
            dados["veiculos"][i] = veiculo

    banco.salvar(dados)

    sucesso("Manutenção registrada. Veículo alterado para MANUTENCAO.")


def concluir_manutencao():
    exibir_secao("CONCLUIR MANUTENÇÃO")

    placa = ler_texto(
        "Placa do veículo cuja manutenção será concluída"
    ).upper()

    dados = banco.carregar()

    veiculo = next(
        (v for v in dados["veiculos"] if v["placa"] == placa),
        None
    )

    if not veiculo:
        aviso("Veículo não encontrado.")
        return

    manutencao = next(
        (
            m for m in reversed(dados["manutencoes"])
            if m["veiculo_placa"] == placa
            and m["status"] == "em_andamento"
        ),
        None
    )

    if not manutencao or veiculo["status"] != "MANUTENCAO":
        raise ManutencaoInvalidaError(
            "Não existe manutenção em andamento para esse veículo."
        )

    manutencao["status"] = "concluida"

    data = datetime.now().isoformat(timespec="seconds")

    veiculo["status"] = "ATIVO"

    veiculo.setdefault("historico_eventos", []).append(
        {
            "data": data,
            "evento": "manutenção concluída"
        }
    )

    if manutencao["tipo"] == "preventiva":
        veiculo["km_ultima_revisao_preventiva"] = veiculo["quilometragem"]

    banco.salvar(dados)

    sucesso("Manutenção concluída. Veículo liberado como ATIVO.")


# ============================================================
# ABASTECIMENTOS
# ============================================================

def registrar_abastecimento():
    exibir_secao("REGISTRAR ABASTECIMENTO")

    placa = ler_texto("Placa do veículo").upper()
    veiculo = buscar_por_chave("veiculos", "placa", placa)

    if not veiculo:
        aviso("Veículo não encontrado.")
        return

    if veiculo.get("status") != "ATIVO":
        raise ValueError(
            "Só é permitido abastecer veículos ATIVOS."
        )

    combustivel = ler_texto("Tipo de combustível")
    litros = ler_float("Litros abastecidos", 0.01)
    valor = ler_float("Valor pago (R$)", 0)

    km = ler_float(
        "Quilometragem atual no painel",
        veiculo["quilometragem"]
    )

    if km < veiculo["quilometragem"]:
        raise ValueError(
            "A quilometragem do abastecimento não pode ser "
            "menor que a registrada no veículo."
        )

    dados = banco.carregar()

    anterior = next(
        (
            a for a in reversed(dados["abastecimentos"])
            if a["veiculo_placa"] == placa
        ),
        None
    )

    consumo_calculado = None

    if anterior:
        distancia = km - float(anterior["quilometragem"])

        if distancia > 0:
            consumo_calculado = round(distancia / litros, 2)
            veiculo["consumo_medio"] = consumo_calculado

    data = datetime.now().isoformat(timespec="seconds")

    registro = {
        "data": data,
        "tipo_combustivel": combustivel,
        "litros": litros,
        "valor_pago": valor,
        "veiculo_placa": placa,
        "quilometragem": km,
        "consumo_calculado_km_l": consumo_calculado
    }

    dados["abastecimentos"].append(registro)

    veiculo["quilometragem"] = km

    veiculo.setdefault("historico_eventos", []).append(
        {
            "data": data,
            "evento": "abastecimento",
            "litros": litros
        }
    )

    for i, v in enumerate(dados["veiculos"]):
        if v["placa"] == placa:
            dados["veiculos"][i] = veiculo

    banco.salvar(dados)

    sucesso("Abastecimento registrado.")

    if consumo_calculado is not None:
        informacao(
            f"Consumo calculado: {consumo_calculado:.2f} km/l"
        )

        config = carregar_configuracoes()

        minimo = float(
            config["consumo_minimo_km_l"].get(veiculo["tipo"], 0)
        )

        maximo = float(
            config["consumo_maximo_km_l"].get(
                veiculo["tipo"],
                float("inf")
            )
        )

        if not minimo <= consumo_calculado <= maximo:
            aviso(
                f"Consumo fora da faixa configurada "
                f"({minimo:.1f} a {maximo:.1f} km/l)."
            )


# ============================================================
# STATUS DOS VEÍCULOS
# ============================================================

def alterar_status_veiculo():
    exibir_secao("GERENCIAR STATUS DO VEÍCULO")

    placa = ler_texto("Placa").upper()

    dados = banco.carregar()

    veiculo = next(
        (v for v in dados["veiculos"] if v["placa"] == placa),
        None
    )

    if not veiculo:
        aviso("Veículo não encontrado.")
        return

    exibir_menu(
        "GERENCIAR STATUS",
        [
            ("1", "Desativar veículo"),
            ("2", "Reativar veículo")
        ]
    )

    opcao = Prompt.ask("[cyan]Selecione uma operação[/cyan]")

    data = datetime.now().isoformat(timespec="seconds")

    if opcao == "1":
        if veiculo["status"] == "MANUTENCAO":
            raise ValueError(
                "Conclua a manutenção antes de desativar o veículo."
            )

        veiculo["status"] = "INATIVO"
        evento = "desativação"

    elif opcao == "2":
        if veiculo["status"] != "INATIVO":
            raise ValueError(
                "Somente veículos INATIVOS podem ser reativados."
            )

        veiculo["status"] = "ATIVO"
        evento = "reativação"

    else:
        erro("Opção inválida.")
        return

    veiculo.setdefault("historico_eventos", []).append(
        {
            "data": data,
            "evento": evento
        }
    )

    banco.salvar(dados)

    sucesso(f"Status atualizado para {veiculo['status']}.")


# ============================================================
# EDIÇÃO E REMOÇÃO DE VEÍCULOS
# ============================================================

def editar_veiculo():
    exibir_secao("EDITAR VEÍCULO")

    placa = ler_texto("Placa do veículo a editar").upper()

    veiculo = buscar_por_chave("veiculos", "placa", placa)

    if not veiculo:
        aviso("Veículo não encontrado.")
        return

    informacao("Deixe vazio para manter o valor atual.")

    for campo in ("marca", "modelo"):
        valor = Prompt.ask(
            f"[cyan]{campo.title()}[/cyan] "
            f"[dim][{veiculo[campo]}][/dim]",
            default=""
        ).strip()

        if valor:
            veiculo[campo] = valor

    valor = Prompt.ask(
        f"[cyan]Consumo médio[/cyan] "
        f"[dim][{veiculo['consumo_medio']}][/dim]",
        default=""
    ).strip()

    if valor:
        consumo = float(valor.replace(",", "."))

        if consumo < 0:
            raise ValueError("Consumo não pode ser negativo.")

        veiculo["consumo_medio"] = consumo

    salvar_atualizacao("veiculos", veiculo)

    sucesso("Veículo atualizado.")


def remover_veiculo():
    exibir_secao("REMOVER VEÍCULO")

    placa = ler_texto("Placa do veículo a remover").upper()

    dados = banco.carregar()

    veiculo = next(
        (v for v in dados["veiculos"] if v["placa"] == placa),
        None
    )

    if not veiculo:
        aviso("Veículo não encontrado.")
        return

    if any(
        t.get("veiculo_placa") == placa
        for c in ("viagens", "manutencoes", "abastecimentos")
        for t in dados[c]
    ):
        raise ValueError(
            "Não é possível excluir veículo com viagens, "
            "manutenções ou abastecimentos vinculados. Desative-o."
        )

    dados["veiculos"] = [
        v for v in dados["veiculos"]
        if v["placa"] != placa
    ]

    banco.salvar(dados)

    sucesso("Veículo removido.")


# ============================================================
# RELATÓRIOS
# ============================================================

def gerar_relatorios():
    dados = banco.carregar()
    config = carregar_configuracoes()

    exibir_menu(
        "RELATÓRIOS DA FROTA",
        [
            ("1", "Status geral da frota"),
            ("2", "Custos de manutenção por tipo de veículo"),
            ("3", "Ranking de eficiência de combustível"),
            ("4", "Viagens por motorista"),
            ("5", "Quilometragem média por tipo"),
            ("6", "Alertas de consumo e revisão"),
            ("0", "Voltar ao menu principal")
        ],
        "Selecione o relatório que deseja consultar."
    )

    escolha = Prompt.ask("[cyan]Relatório[/cyan]")

    if escolha == "0":
        return

    veiculos = dados["veiculos"]

    # --------------------------------------------------------
    # 1. STATUS DA FROTA
    # --------------------------------------------------------

    if escolha == "1":
        tabela = criar_tabela(
            "STATUS DA FROTA",
            ["Status", "Quantidade"]
        )

        for status in ("ATIVO", "MANUTENCAO", "INATIVO"):
            quantidade = sum(
                v.get("status") == status
                for v in veiculos
            )

            tabela.add_row(status, str(quantidade))

        console.print(tabela)

    # --------------------------------------------------------
    # 2. CUSTOS DE MANUTENÇÃO
    # --------------------------------------------------------

    elif escolha == "2":
        custos = {}

        placas = {
            v["placa"]: v
            for v in veiculos
        }

        for manutencao in dados["manutencoes"]:
            veiculo = placas.get(
                manutencao.get("veiculo_placa")
            )

            if veiculo:
                tipo = veiculo["tipo"]

                custos.setdefault(tipo, []).append(
                    float(manutencao.get("custo", 0))
                )

        tabela = criar_tabela(
            "CUSTOS DE MANUTENÇÃO",
            ["Tipo de veículo", "Custo total", "Custo médio"]
        )

        for tipo, valores in sorted(custos.items()):
            total = sum(valores)
            media = total / len(valores)

            tabela.add_row(
                tipo,
                f"R$ {total:.2f}",
                f"R$ {media:.2f}"
            )

        if not custos:
            aviso("Sem manutenções registradas.")
        else:
            console.print(tabela)

    # --------------------------------------------------------
    # 3. RANKING DE EFICIÊNCIA
    # --------------------------------------------------------

    elif escolha == "3":
        ranking = sorted(
            veiculos,
            key=lambda v: float(v.get("consumo_medio", 0)),
            reverse=True
        )

        tabela = criar_tabela(
            "RANKING DE EFICIÊNCIA",
            ["Posição", "Placa", "Tipo", "Consumo médio"]
        )

        for posicao, veiculo in enumerate(ranking, 1):
            tabela.add_row(
                str(posicao),
                veiculo["placa"],
                veiculo["tipo"],
                f"{float(veiculo.get('consumo_medio', 0)):.2f} km/l"
            )

        if not ranking:
            aviso("Nenhum veículo cadastrado.")
        else:
            console.print(tabela)

    # --------------------------------------------------------
    # 4. VIAGENS POR MOTORISTA
    # --------------------------------------------------------

    elif escolha == "4":
        contagem = {}

        for viagem in dados["viagens"]:
            cpf = viagem.get("motorista_cpf", "?")
            contagem[cpf] = contagem.get(cpf, 0) + 1

        motoristas = {
            m["cpf"]: m["nome"]
            for m in dados["motoristas"]
        }

        tabela = criar_tabela(
            "VIAGENS POR MOTORISTA",
            ["Motorista", "CPF", "Quantidade de viagens"]
        )

        for cpf, quantidade in sorted(
            contagem.items(),
            key=lambda item: item[1],
            reverse=True
        ):
            tabela.add_row(
                motoristas.get(cpf, cpf),
                cpf,
                str(quantidade)
            )

        if not contagem:
            aviso("Sem viagens registradas.")
        else:
            console.print(tabela)

    # --------------------------------------------------------
    # 5. QUILOMETRAGEM MÉDIA
    # --------------------------------------------------------

    elif escolha == "5":
        por_tipo = {}

        for veiculo in veiculos:
            por_tipo.setdefault(
                veiculo["tipo"], []
            ).append(
                float(veiculo.get("quilometragem", 0))
            )

        tabela = criar_tabela(
            "QUILOMETRAGEM MÉDIA",
            ["Tipo de veículo", "Quilometragem média"]
        )

        for tipo, kms in sorted(por_tipo.items()):
            media = sum(kms) / len(kms)

            tabela.add_row(
                tipo,
                f"{media:.2f} km"
            )

        if not por_tipo:
            aviso("Sem veículos cadastrados.")
        else:
            console.print(tabela)

    # --------------------------------------------------------
    # 6. ALERTAS
    # --------------------------------------------------------

    elif escolha == "6":
        intervalo = float(
            config["limite_km_revisao_preventiva"]
        )

        tabela = criar_tabela(
            "ALERTAS DA FROTA",
            ["Veículo", "Tipo de alerta", "Detalhes"]
        )

        alertas = 0

        for veiculo in veiculos:
            km_revisao = float(
                veiculo.get("km_ultima_revisao_preventiva", 0)
            )

            km_desde = (
                float(veiculo.get("quilometragem", 0))
                - km_revisao
            )

            if km_desde >= intervalo:
                tabela.add_row(
                    veiculo["placa"],
                    "[red]Revisão vencida[/red]",
                    f"{km_desde:.0f} km desde a revisão"
                )

                alertas += 1

            minimo = float(
                config["consumo_minimo_km_l"].get(
                    veiculo["tipo"], 0
                )
            )

            maximo = float(
                config["consumo_maximo_km_l"].get(
                    veiculo["tipo"], float("inf")
                )
            )

            consumo = float(
                veiculo.get("consumo_medio", 0)
            )

            if consumo and not minimo <= consumo <= maximo:
                tabela.add_row(
                    veiculo["placa"],
                    "[yellow]Consumo fora da faixa[/yellow]",
                    (
                        f"{consumo:.2f} km/l "
                        f"(faixa {minimo}-{maximo})"
                    )
                )

                alertas += 1

        if alertas:
            console.print(tabela)
            aviso(f"Foram encontrados {alertas} alerta(s).")
        else:
            sucesso("Nenhum alerta no momento.")

    else:
        erro("Opção inválida.")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def main():
    """Inicializa e executa o sistema de gerenciamento de frota."""

    try:
        banco.carregar()
        carregar_configuracoes()

    except (OSError, ValueError, json.JSONDecodeError) as erro_inicial:
        erro(f"Falha ao inicializar o sistema: {erro_inicial}")
        return

    while True:
        console.clear()
        exibir_cabecalho()

        exibir_menu(
            "MENU PRINCIPAL",
            [
                ("01", "Cadastrar veículo"),
                ("02", "Cadastrar motorista"),
                ("03", "Consultar registros"),
                ("04", "Registrar viagem / Alocar veículo"),
                ("05", "Registrar manutenção"),
                ("06", "Concluir manutenção e liberar veículo"),
                ("07", "Registrar abastecimento"),
                ("08", "Gerenciar status dos veículos"),
                ("09", "Editar veículo"),
                ("10", "Remover veículo"),
                ("11", "Relatórios da frota"),
                ("00", "Encerrar sistema")
            ],
            "Utilize o código da operação desejada."
        )

        opcao = Prompt.ask(
            "\n[bold cyan]FROTA MANAGER[/bold cyan] "
            "[dim]›[/dim] Operação"
        )

        try:
            if opcao == "01":
                console.clear()
                cadastrar_veiculo()

            elif opcao == "02":
                console.clear()
                cadastrar_motorista()

            elif opcao == "03":
                console.clear()

                categorias = {
                    "1": ("veiculos", "Veículos"),
                    "2": ("motoristas", "Motoristas"),
                    "3": ("viagens", "Viagens"),
                    "4": ("manutencoes", "Manutenções"),
                    "5": ("abastecimentos", "Abastecimentos")
                }

                exibir_menu(
                    "CONSULTAR REGISTROS",
                    [
                        ("1", "Veículos"),
                        ("2", "Motoristas"),
                        ("3", "Viagens"),
                        ("4", "Manutenções"),
                        ("5", "Abastecimentos"),
                        ("0", "Voltar")
                    ]
                )

                categoria = Prompt.ask(
                    "[cyan]Categoria[/cyan]"
                )

                if categoria == "0":
                    continue

                item = categorias.get(categoria)

                if item:
                    console.clear()
                    listar_categoria(*item)
                else:
                    erro("Categoria inválida.")

            elif opcao == "04":
                console.clear()
                registrar_viagem()

            elif opcao == "05":
                console.clear()
                registrar_manutencao()

            elif opcao == "06":
                console.clear()
                concluir_manutencao()

            elif opcao == "07":
                console.clear()
                registrar_abastecimento()

            elif opcao == "08":
                console.clear()
                alterar_status_veiculo()

            elif opcao == "09":
                console.clear()
                editar_veiculo()

            elif opcao == "10":
                console.clear()
                remover_veiculo()

            elif opcao == "11":
                console.clear()
                gerar_relatorios()

            elif opcao == "00":
                console.print(
                    Panel(
                        "[bold green]Sistema encerrado com sucesso![/bold green]\n"
                        "[dim]Os dados foram preservados no banco de dados.[/dim]",
                        border_style="green",
                        box=box.ROUNDED
                    )
                )
                break

            else:
                aviso("Opção inválida.")

        except (
            OSError,
            ValueError,
            TypeError,
            AlocacaoInvalidaError,
            ManutencaoInvalidaError,
            PoliticaNaoAtendidaError
        ) as erro_operacao:
            erro(f"Operação não realizada: {erro_operacao}")

        if opcao != "00":
            pausar()


if __name__ == "__main__":
    main()
