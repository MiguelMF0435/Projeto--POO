"""CLI do Sistema de Gerenciamento de Frota de Veículos."""
from datetime import datetime
import json
from pathlib import Path

from banco import BancoDeDados
from exceptions import AlocacaoInvalidaError, ManutencaoInvalidaError, PoliticaNaoAtendidaError

banco = BancoDeDados()
SETTINGS_PATH = Path(__file__).resolve().parent / "settings.json"


def carregar_configuracoes():
    """Carrega políticas configuráveis; cria settings.json com padrões se faltar."""
    padrao = {
        "limite_km_revisao_preventiva": 10000,
        "consumo_minimo_km_l": {"Carro": 5.0, "Moto": 15.0, "Caminhão": 2.0},
        "consumo_maximo_km_l": {"Carro": 25.0, "Moto": 45.0, "Caminhão": 8.0},
        "custos_manutencao": {"preventiva": 250.0, "corretiva": 500.0},
        "cnh_minima": {"Moto": "A", "Carro": "B", "Caminhão": "C"},
    }
    if not SETTINGS_PATH.exists():
        SETTINGS_PATH.write_text(json.dumps(padrao, ensure_ascii=False, indent=4), encoding="utf-8")
        return padrao
    with SETTINGS_PATH.open("r", encoding="utf-8") as arquivo:
        config = json.load(arquivo)
    for chave, valor in padrao.items():
        config.setdefault(chave, valor)
    return config


def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("O campo não pode ficar vazio.")


def ler_int(mensagem, minimo=None):
    while True:
        try:
            valor = int(input(mensagem))
            if minimo is not None and valor < minimo:
                print(f"Informe um valor igual ou superior a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Informe um número inteiro válido.")


def ler_float(mensagem, minimo=None):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))
            if minimo is not None and valor < minimo:
                print(f"Informe um valor igual ou superior a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Informe um número válido.")


def normalizar_status(status):
    status = status.strip().upper().replace("Á", "A").replace("Ã", "A")
    aliases = {"ATIVO": "ATIVO", "DISPONIVEL": "ATIVO", "MANUTENCAO": "MANUTENCAO", "EM MANUTENCAO": "MANUTENCAO", "INATIVO": "INATIVO"}
    if status not in aliases:
        raise ValueError("Status deve ser ATIVO, MANUTENCAO ou INATIVO.")
    return aliases[status]


def buscar_por_chave(categoria, chave, valor):
    for registro in banco.listar(categoria):
        if str(registro.get(chave, "")).upper() == str(valor).upper():
            return registro
    return None


def salvar_atualizacao(categoria, registro):
    dados = banco.carregar()
    chave = "placa" if categoria == "veiculos" else "cpf" if categoria == "motoristas" else None
    if chave:
        for i, item in enumerate(dados[categoria]):
            if item.get(chave) == registro.get(chave):
                dados[categoria][i] = registro
                break
    banco.salvar(dados)


def cadastrar_veiculo():
    print("\n--- Cadastro de veículo ---\n1. Carro\n2. Moto\n3. Caminhão")
    opcoes = {"1": "Carro", "2": "Moto", "3": "Caminhão"}
    tipo = input("Tipo: ").strip()
    if tipo not in opcoes:
        print("Tipo inválido."); return
    placa = ler_texto("Placa: ").upper()
    if buscar_por_chave("veiculos", "placa", placa):
        print("Já existe um veículo com essa placa."); return
    marca, modelo = ler_texto("Marca: "), ler_texto("Modelo: ")
    ano = ler_int("Ano: ", 1886)
    if ano > datetime.now().year + 1:
        print("O ano informado é inválido."); return
    km = ler_float("Quilometragem: ", 0)
    consumo = ler_float("Consumo médio (km/l): ", 0)
    dados = {"placa": placa, "marca": marca, "modelo": modelo, "tipo": opcoes[tipo], "ano": ano,
             "quilometragem": km, "consumo_medio": consumo, "status": "ATIVO",
             "historico_eventos": [{"data": datetime.now().isoformat(timespec="seconds"), "evento": "entrada"}],
             "km_ultima_revisao_preventiva": km}
    banco.adicionar("veiculos", dados)
    print("Veículo cadastrado como ATIVO e salvo.")


def cadastrar_motorista():
    print("\n--- Cadastro de motorista ---")
    cpf = ler_texto("CPF: ").strip()
    if buscar_por_chave("motoristas", "cpf", cpf):
        print("Já existe um motorista com esse CPF."); return
    nome = ler_texto("Nome: ")
    categoria = ler_texto("Categoria CNH (A, B, C, D ou E): ").upper()
    if categoria not in {"A", "B", "C", "D", "E"}:
        print("Categoria inválida."); return
    experiencia = ler_int("Experiência em anos: ", 0)
    disponibilidade = input("Está disponível? (s/n): ").strip().lower()
    if disponibilidade not in {"s", "n"}:
        print("Resposta inválida."); return
    banco.adicionar("motoristas", {"nome": nome, "cpf": cpf, "funcao": "Motorista", "categoria_cnh": categoria,
                                   "experiencia_anos": experiencia, "disponibilidade": disponibilidade == "s",
                                   "historico_viagens": []})
    print("Motorista cadastrado e salvo.")


def listar_categoria(categoria, titulo):
    registros = banco.listar(categoria)
    print(f"\n--- {titulo}: {len(registros)} ---")
    if not registros:
        print("Nenhum registro encontrado."); return
    for i, registro in enumerate(registros, 1):
        print(f"\n{i}.")
        for campo, valor in registro.items():
            print(f"  {campo}: {valor}")


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


def registrar_viagem():
    print("\n--- Registrar viagem ---")
    placa = ler_texto("Placa do veículo: ").upper()
    veiculo = buscar_por_chave("veiculos", "placa", placa)
    if not veiculo:
        print("Veículo não encontrado."); return
    if veiculo.get("status") != "ATIVO":
        raise AlocacaoInvalidaError("Veículo em manutenção ou inativo não pode ser alocado.")
    config = carregar_configuracoes()
    intervalo = float(config["limite_km_revisao_preventiva"])
    km_desde_revisao = veiculo["quilometragem"] - veiculo.get("km_ultima_revisao_preventiva", 0)
    if km_desde_revisao >= intervalo:
        raise PoliticaNaoAtendidaError("Revisão preventiva obrigatória. Registre a manutenção antes de uma nova viagem.")
    cpf = ler_texto("CPF do motorista: ")
    motorista = buscar_por_chave("motoristas", "cpf", cpf)
    if not motorista:
        print("Motorista não encontrado."); return
    if not motorista.get("disponibilidade", False):
        raise AlocacaoInvalidaError("O motorista não está disponível.")
    if not compatibilidade_cnh(motorista.get("categoria_cnh", ""), veiculo["tipo"]):
        raise AlocacaoInvalidaError(f"CNH {motorista.get('categoria_cnh')} incompatível com {veiculo['tipo']}.")
    origem, destino = ler_texto("Origem: "), ler_texto("Destino: ")
    distancia = ler_float("Distância percorrida (km): ", 0.01)
    viagem = {"motorista_cpf": motorista["cpf"], "motorista_nome": motorista["nome"], "veiculo_placa": veiculo["placa"],
              "origem": origem, "destino": destino, "distancia": distancia,
              "data": datetime.now().isoformat(timespec="seconds")}
    dados = banco.carregar()
    dados["viagens"].append(viagem)
    veiculo["quilometragem"] = round(float(veiculo["quilometragem"]) + distancia, 2)
    veiculo.setdefault("historico_eventos", []).append({"data": viagem["data"], "evento": "saída/viagem", "distancia": distancia})
    motorista.setdefault("historico_viagens", []).append({"data": viagem["data"], "veiculo_placa": placa, "origem": origem, "destino": destino, "distancia": distancia})
    for i, v in enumerate(dados["veiculos"]):
        if v["placa"] == placa: dados["veiculos"][i] = veiculo
    for i, m in enumerate(dados["motoristas"]):
        if m["cpf"] == cpf: dados["motoristas"][i] = motorista
    banco.salvar(dados)
    print(f"Viagem registrada. Quilometragem atual do veículo: {veiculo['quilometragem']:.1f} km.")
    if veiculo["quilometragem"] - veiculo.get("km_ultima_revisao_preventiva", 0) >= intervalo:
        print("ALERTA: a revisão preventiva está vencida; não será possível registrar outra viagem até a revisão.")


def registrar_manutencao():
    print("\n--- Registrar manutenção ---")
    placa = ler_texto("Placa do veículo: ").upper()
    veiculo = buscar_por_chave("veiculos", "placa", placa)
    if not veiculo:
        print("Veículo não encontrado."); return
    if veiculo.get("status") == "INATIVO":
        raise ManutencaoInvalidaError("Não é possível iniciar manutenção em veículo INATIVO.")
    if veiculo.get("status") == "MANUTENCAO":
        raise ManutencaoInvalidaError("O veículo já está em manutenção. Conclua o serviço atual primeiro.")
    print("1. Preventiva\n2. Corretiva")
    escolha = input("Tipo: ").strip()
    tipos = {"1": "preventiva", "2": "corretiva"}
    if escolha not in tipos:
        print("Tipo inválido."); return
    tipo = tipos[escolha]
    config = carregar_configuracoes()
    custo_padrao = float(config["custos_manutencao"].get(tipo, 0))
    custo = ler_float(f"Custo (padrão R$ {custo_padrao:.2f}): ", 0)
    descricao = ler_texto("Descrição: ")
    data = datetime.now().isoformat(timespec="seconds")
    registro = {"data": data, "tipo": tipo, "custo": custo, "descricao": descricao,
                "veiculo_placa": placa, "status": "em_andamento"}
    dados = banco.carregar()
    dados["manutencoes"].append(registro)
    veiculo["status"] = "MANUTENCAO"
    veiculo.setdefault("historico_eventos", []).append({"data": data, "evento": "manutenção iniciada", "tipo": tipo})
    for i, v in enumerate(dados["veiculos"]):
        if v["placa"] == placa: dados["veiculos"][i] = veiculo
    banco.salvar(dados)
    print("Manutenção registrada. Veículo alterado para MANUTENCAO.")


def concluir_manutencao():
    placa = ler_texto("Placa do veículo cuja manutenção será concluída: ").upper()
    dados = banco.carregar()
    veiculo = next((v for v in dados["veiculos"] if v["placa"] == placa), None)
    if not veiculo:
        print("Veículo não encontrado."); return
    manutencao = next((m for m in reversed(dados["manutencoes"]) if m["veiculo_placa"] == placa and m["status"] == "em_andamento"), None)
    if not manutencao or veiculo["status"] != "MANUTENCAO":
        raise ManutencaoInvalidaError("Não existe manutenção em andamento para esse veículo.")
    manutencao["status"] = "concluida"
    data = datetime.now().isoformat(timespec="seconds")
    veiculo["status"] = "ATIVO"
    veiculo.setdefault("historico_eventos", []).append({"data": data, "evento": "manutenção concluída"})
    if manutencao["tipo"] == "preventiva":
        veiculo["km_ultima_revisao_preventiva"] = veiculo["quilometragem"]
    banco.salvar(dados)
    print("Manutenção concluída. Veículo liberado como ATIVO.")


def registrar_abastecimento():
    print("\n--- Registrar abastecimento ---")
    placa = ler_texto("Placa do veículo: ").upper()
    veiculo = buscar_por_chave("veiculos", "placa", placa)
    if not veiculo:
        print("Veículo não encontrado."); return
    if veiculo.get("status") != "ATIVO":
        raise ValueError("Só é permitido abastecer veículos ATIVOS.")
    combustivel = ler_texto("Tipo de combustível: ")
    litros = ler_float("Litros abastecidos: ", 0.01)
    valor = ler_float("Valor pago (R$): ", 0)
    km = ler_float("Quilometragem atual no painel: ", veiculo["quilometragem"])
    if km < veiculo["quilometragem"]:
        raise ValueError("A quilometragem do abastecimento não pode ser menor que a registrada no veículo.")
    dados = banco.carregar()
    anterior = next((a for a in reversed(dados["abastecimentos"]) if a["veiculo_placa"] == placa), None)
    consumo_calculado = None
    if anterior:
        distancia = km - float(anterior["quilometragem"])
        if distancia > 0:
            consumo_calculado = round(distancia / litros, 2)
            veiculo["consumo_medio"] = consumo_calculado
    data = datetime.now().isoformat(timespec="seconds")
    registro = {"data": data, "tipo_combustivel": combustivel, "litros": litros, "valor_pago": valor,
                "veiculo_placa": placa, "quilometragem": km, "consumo_calculado_km_l": consumo_calculado}
    dados["abastecimentos"].append(registro)
    veiculo["quilometragem"] = km
    veiculo.setdefault("historico_eventos", []).append({"data": data, "evento": "abastecimento", "litros": litros})
    for i, v in enumerate(dados["veiculos"]):
        if v["placa"] == placa: dados["veiculos"][i] = veiculo
    banco.salvar(dados)
    print("Abastecimento registrado.")
    if consumo_calculado is not None:
        print(f"Consumo calculado: {consumo_calculado:.2f} km/l")
        config = carregar_configuracoes()
        minimo = float(config["consumo_minimo_km_l"].get(veiculo["tipo"], 0))
        maximo = float(config["consumo_maximo_km_l"].get(veiculo["tipo"], float("inf")))
        if not minimo <= consumo_calculado <= maximo:
            print(f"ALERTA: consumo fora da faixa configurada ({minimo:.1f} a {maximo:.1f} km/l).")


def alterar_status_veiculo():
    placa = ler_texto("Placa: ").upper()
    dados = banco.carregar()
    veiculo = next((v for v in dados["veiculos"] if v["placa"] == placa), None)
    if not veiculo:
        print("Veículo não encontrado."); return
    print("1. Desativar veículo\n2. Reativar veículo")
    opcao = input("Opção: ").strip()
    data = datetime.now().isoformat(timespec="seconds")
    if opcao == "1":
        if veiculo["status"] == "MANUTENCAO":
            raise ValueError("Conclua a manutenção antes de desativar o veículo.")
        veiculo["status"] = "INATIVO"
        evento = "desativação"
    elif opcao == "2":
        if veiculo["status"] != "INATIVO":
            raise ValueError("Somente veículos INATIVOS podem ser reativados por esta opção.")
        veiculo["status"] = "ATIVO"
        evento = "reativação"
    else:
        print("Opção inválida."); return
    veiculo.setdefault("historico_eventos", []).append({"data": data, "evento": evento})
    banco.salvar(dados)
    print(f"Status atualizado para {veiculo['status']}.")


def editar_veiculo():
    placa = ler_texto("Placa do veículo a editar: ").upper()
    veiculo = buscar_por_chave("veiculos", "placa", placa)
    if not veiculo:
        print("Veículo não encontrado."); return
    print("Deixe vazio para manter o valor atual.")
    for campo in ("marca", "modelo"):
        valor = input(f"{campo.title()} [{veiculo[campo]}]: ").strip()
        if valor: veiculo[campo] = valor
    valor = input(f"Consumo médio [{veiculo['consumo_medio']}]: ").strip()
    if valor:
        consumo = float(valor.replace(",", "."))
        if consumo < 0: raise ValueError("Consumo não pode ser negativo.")
        veiculo["consumo_medio"] = consumo
    salvar_atualizacao("veiculos", veiculo)
    print("Veículo atualizado.")


def remover_veiculo():
    placa = ler_texto("Placa do veículo a remover: ").upper()
    dados = banco.carregar()
    veiculo = next((v for v in dados["veiculos"] if v["placa"] == placa), None)
    if not veiculo:
        print("Veículo não encontrado."); return
    if any(t.get("veiculo_placa") == placa for c in ("viagens", "manutencoes", "abastecimentos") for t in dados[c]):
        raise ValueError("Não é possível excluir veículo com viagens, manutenções ou abastecimentos vinculados. Desative-o.")
    dados["veiculos"] = [v for v in dados["veiculos"] if v["placa"] != placa]
    banco.salvar(dados)
    print("Veículo removido.")


def gerar_relatorios():
    dados = banco.carregar()
    config = carregar_configuracoes()
    print("\n========== RELATÓRIOS DA FROTA ==========")
    print("1. Status da frota")
    print("2. Custos de manutenção por tipo de veículo")
    print("3. Ranking de eficiência de combustível")
    print("4. Viagens por motorista")
    print("5. Quilometragem média por tipo")
    print("6. Alertas de consumo e revisão")
    escolha = input("Relatório: ").strip()
    veiculos = dados["veiculos"]
    if escolha == "1":
        for status in ("ATIVO", "MANUTENCAO", "INATIVO"):
            print(f"{status}: {sum(v.get('status') == status for v in veiculos)}")
    elif escolha == "2":
        custos = {}
        placas = {v["placa"]: v for v in veiculos}
        for m in dados["manutencoes"]:
            v = placas.get(m.get("veiculo_placa"))
            if v:
                chave = v["tipo"]
                custos.setdefault(chave, []).append(float(m.get("custo", 0)))
        for tipo, valores in sorted(custos.items()):
            print(f"{tipo}: total R$ {sum(valores):.2f}; média R$ {sum(valores)/len(valores):.2f}")
        if not custos: print("Sem manutenções registradas.")
    elif escolha == "3":
        ranking = sorted(veiculos, key=lambda v: float(v.get("consumo_medio", 0)), reverse=True)
        for pos, v in enumerate(ranking, 1):
            print(f"{pos}. {v['placa']} ({v['tipo']}): {float(v.get('consumo_medio', 0)):.2f} km/l")
    elif escolha == "4":
        contagem = {}
        for viagem in dados["viagens"]:
            cpf = viagem.get("motorista_cpf", "?")
            contagem[cpf] = contagem.get(cpf, 0) + 1
        motoristas = {m["cpf"]: m["nome"] for m in dados["motoristas"]}
        for cpf, quantidade in sorted(contagem.items(), key=lambda item: item[1], reverse=True):
            print(f"{motoristas.get(cpf, cpf)}: {quantidade} viagem(ns)")
        if not contagem: print("Sem viagens registradas.")
    elif escolha == "5":
        por_tipo = {}
        for v in veiculos: por_tipo.setdefault(v["tipo"], []).append(float(v.get("quilometragem", 0)))
        for tipo, kms in sorted(por_tipo.items()): print(f"{tipo}: {sum(kms)/len(kms):.2f} km de média")
        if not por_tipo: print("Sem veículos cadastrados.")
    elif escolha == "6":
        intervalo = float(config["limite_km_revisao_preventiva"])
        alertas = 0
        for v in veiculos:
            km_revisao = float(v.get("km_ultima_revisao_preventiva", 0))
            km_desde = float(v.get("quilometragem", 0)) - km_revisao
            if km_desde >= intervalo:
                print(f"REVISÃO VENCIDA: {v['placa']} — {km_desde:.0f} km desde a revisão."); alertas += 1
            minimo = float(config["consumo_minimo_km_l"].get(v["tipo"], 0))
            maximo = float(config["consumo_maximo_km_l"].get(v["tipo"], float("inf")))
            consumo = float(v.get("consumo_medio", 0))
            if consumo and not minimo <= consumo <= maximo:
                print(f"CONSUMO FORA DA FAIXA: {v['placa']} — {consumo:.2f} km/l (faixa {minimo}-{maximo})."); alertas += 1
        if not alertas: print("Nenhum alerta no momento.")
    else:
        print("Opção inválida.")


def main():
    try:
        banco.carregar()
        carregar_configuracoes()
    except (OSError, ValueError, json.JSONDecodeError) as erro:
        print(f"Falha ao inicializar o sistema: {erro}"); return
    while True:
        print("\n======= SISTEMA DE GERENCIAMENTO DE FROTA =======")
        print("1. Cadastrar veículo")
        print("2. Cadastrar motorista")
        print("3. Listar registros")
        print("4. Registrar viagem / alocar veículo")
        print("5. Registrar manutenção")
        print("6. Concluir manutenção e liberar veículo")
        print("7. Registrar abastecimento")
        print("8. Desativar / reativar veículo")
        print("9. Editar veículo")
        print("10. Remover veículo")
        print("11. Relatórios")
        print("0. Sair")
        opcao = input("Opção: ").strip()
        try:
            if opcao == "1": cadastrar_veiculo()
            elif opcao == "2": cadastrar_motorista()
            elif opcao == "3":
                categorias = {"1": ("veiculos", "Veículos"), "2": ("motoristas", "Motoristas"), "3": ("viagens", "Viagens"), "4": ("manutencoes", "Manutenções"), "5": ("abastecimentos", "Abastecimentos")}
                for k, (_, nome) in categorias.items(): print(f"{k}. {nome}")
                item = categorias.get(input("Categoria: ").strip())
                if item: listar_categoria(*item)
                else: print("Opção inválida.")
            elif opcao == "4": registrar_viagem()
            elif opcao == "5": registrar_manutencao()
            elif opcao == "6": concluir_manutencao()
            elif opcao == "7": registrar_abastecimento()
            elif opcao == "8": alterar_status_veiculo()
            elif opcao == "9": editar_veiculo()
            elif opcao == "10": remover_veiculo()
            elif opcao == "11": gerar_relatorios()
            elif opcao == "0": print("Dados salvos. Até logo!"); break
            else: print("Opção inválida.")
        except (OSError, ValueError, TypeError, AlocacaoInvalidaError, ManutencaoInvalidaError, PoliticaNaoAtendidaError) as erro:
            print(f"Operação não realizada: {erro}")


if __name__ == "__main__":
    main()
