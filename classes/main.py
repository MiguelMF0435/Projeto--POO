from datetime import datetime

from banco import BancoDeDados
from veiculos import Carro, Moto, Caminhao
from pessoa import Motorista
from viagem import Viagem
from registros import Manutencao, Abastecimento

banco = BancoDeDados()


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
                print(f"Informe um inteiro igual ou superior a {minimo}.")
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


def ler_data():
    while True:
        valor = input("Data e hora (AAAA-MM-DD HH:MM) ou Enter para agora: ").strip()
        if not valor:
            return datetime.now()
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            print("Formato inválido. Exemplo: 2026-10-21 14:30")


def obter_veiculo(placa):
    return next((v for v in banco.listar("veiculos")
                 if v.get("placa", "").upper() == placa.upper()), None)


def cadastrar_veiculo():
    print("\\n--- Cadastro de veículo ---")
    opcoes = {"1": (Carro, "Carro"), "2": (Moto, "Moto"), "3": (Caminhao, "Caminhão")}
    print("1. Carro\\n2. Moto\\n3. Caminhão")
    escolha = input("Tipo: ").strip()
    if escolha not in opcoes:
        print("Tipo inválido.")
        return
    classe, _ = opcoes[escolha]
    dados = banco.carregar()
    placa = ler_texto("Placa: ").upper()
    if any(v.get("placa", "").upper() == placa for v in dados["veiculos"]):
        print("Já existe veículo com essa placa.")
        return

    veiculo = classe(
        placa, ler_texto("Marca: "), ler_texto("Modelo: "),
        ler_int("Ano: ", 1886), ler_float("Quilometragem: ", 0),
        ler_float("Consumo médio (km/l): ", 0),
        ler_texto("Status: ")
    )
    banco.adicionar("veiculos", {
        "placa": veiculo.placa, "marca": veiculo.marca,
        "modelo": veiculo.modelo, "tipo": veiculo.tipo, "ano": veiculo.ano,
        "quilometragem": veiculo.quilometragem,
        "consumo_medio": veiculo.consumo_medio, "status": veiculo.status
    })
    print("Veículo cadastrado e salvo.")


def cadastrar_motorista():
    print("\\n--- Cadastro de motorista ---")
    dados = banco.carregar()
    cpf = ler_texto("CPF: ")
    if any(m.get("cpf") == cpf for m in dados["motoristas"]):
        print("Já existe motorista com esse CPF.")
        return
    nome = ler_texto("Nome: ")
    funcao = ler_texto("Função: ")
    cnh = ler_texto("Categoria da CNH: ").upper()
    experiencia = ler_int("Anos de experiência: ", 0)
    print("1. Disponível\\n2. Indisponível")
    disponibilidade_opcao = input("Escolha: ").strip()
    if disponibilidade_opcao not in ("1", "2"):
        print("Opção inválida.")
        return
    motorista = Motorista(nome, cpf, funcao, cnh, experiencia,
                          disponibilidade_opcao == "1")
    banco.adicionar("motoristas", {
        "nome": motorista.nome, "cpf": motorista.cpf,
        "funcao": motorista.funcao, "categoria_cnh": motorista.categoria_cnh,
        "experiencia_anos": motorista.experiencia_anos,
        "disponibilidade": motorista.disponibilidade, "historico_viagens": []
    })
    print("Motorista cadastrado e salvo.")


def cadastrar_viagem():
    print("\\n--- Registrar viagem ---")
    dados = banco.carregar()
    if not dados["veiculos"] or not dados["motoristas"]:
        print("Cadastre pelo menos um veículo e um motorista antes.")
        return
    placa = ler_texto("Placa do veículo: ").upper()
    veiculo_dados = next((v for v in dados["veiculos"]
                          if v.get("placa", "").upper() == placa), None)
    if not veiculo_dados:
        print("Veículo não encontrado.")
        return
    cpf = ler_texto("CPF do motorista: ")
    motorista_dados = next((m for m in dados["motoristas"] if m.get("cpf") == cpf), None)
    if not motorista_dados:
        print("Motorista não encontrado.")
        return
    if not motorista_dados.get("disponibilidade", False):
        print("O motorista está indisponível.")
        return

    classes_veiculos = {"Carro": Carro, "Moto": Moto, "Caminhão": Caminhao}
    classe = classes_veiculos.get(veiculo_dados.get("tipo"), Carro)
    veiculo = classe(
        veiculo_dados["placa"], veiculo_dados["marca"], veiculo_dados["modelo"],
        int(veiculo_dados["ano"]), float(veiculo_dados["quilometragem"]),
        float(veiculo_dados["consumo_medio"]), veiculo_dados["status"]
    )
    motorista = Motorista(
        motorista_dados["nome"], motorista_dados["cpf"], motorista_dados["funcao"],
        motorista_dados["categoria_cnh"], int(motorista_dados["experiencia_anos"]),
        motorista_dados["disponibilidade"], []
    )
    origem = ler_texto("Origem: ")
    destino = ler_texto("Destino: ")
    distancia = ler_float("Distância (km): ", 0)
    data = ler_data()
    viagem = Viagem(motorista, veiculo, origem, destino, distancia, data)

    banco.adicionar("viagens", {
        "motorista_cpf": viagem.motorista.cpf,
        "motorista_nome": viagem.motorista.nome,
        "veiculo_placa": viagem.veiculo.placa,
        "origem": viagem.origem, "destino": viagem.destino,
        "distancia": viagem.distancia, "data": viagem.data.isoformat()
    })
    # Atualiza quilometragem do veículo no cadastro persistido.
    novos_dados = banco.carregar()
    for item in novos_dados["veiculos"]:
        if item["placa"].upper() == placa:
            item["quilometragem"] = float(item["quilometragem"]) + distancia
            banco.salvar(novos_dados)
            break
    print("Viagem registrada. A viagem foi associada ao motorista e ao veículo pelo CPF e placa.")


def cadastrar_manutencao():
    print("\\n--- Registrar manutenção ---")
    placa = ler_texto("Placa do veículo: ").upper()
    dados = banco.carregar()
    veiculo = next((v for v in dados["veiculos"] if v.get("placa", "").upper() == placa), None)
    if not veiculo:
        print("Veículo não encontrado.")
        return
    data = ler_data()
    tipo = ler_texto("Tipo (preventiva/corretiva): ")
    custo = ler_float("Custo (R$): ", 0)
    descricao = ler_texto("Descrição: ")
    status = ler_texto("Status: ")
    registro = {
        "data": data.isoformat(), "tipo": tipo, "custo": custo,
        "descricao": descricao, "veiculo_placa": placa, "status": status
    }
    banco.adicionar("manutencoes", registro)
    # Atualiza o status do veículo para refletir manutenção em andamento.
    if status.lower() in ("pendente", "em andamento", "em manutenção", "em manutencao"):
        for item in dados["veiculos"]:
            if item.get("placa", "").upper() == placa:
                item["status"] = "Em manutenção"
                break
        banco.salvar(dados)
    print("Manutenção registrada e salva.")


def cadastrar_abastecimento():
    print("\\n--- Registrar abastecimento ---")
    placa = ler_texto("Placa do veículo: ").upper()
    dados = banco.carregar()
    veiculo = next((v for v in dados["veiculos"] if v.get("placa", "").upper() == placa), None)
    if not veiculo:
        print("Veículo não encontrado.")
        return
    data = ler_data()
    combustivel = ler_texto("Tipo de combustível: ")
    litros = ler_float("Litros: ", 0)
    valor = ler_float("Valor pago (R$): ", 0)
    km = ler_float("Quilometragem no abastecimento: ", 0)
    if km < float(veiculo.get("quilometragem", 0)):
        print("Aviso: a quilometragem informada é menor que a quilometragem atual do cadastro.")
    banco.adicionar("abastecimentos", {
        "data": data.isoformat(), "tipo_combustivel": combustivel,
        "litros": litros, "valor_pago": valor,
        "veiculo_placa": placa, "quilometragem": km
    })
    print("Abastecimento registrado e salvo.")


def listar_registros():
    opcoes = {
        "1": ("veiculos", "Veículos"), "2": ("motoristas", "Motoristas"),
        "3": ("viagens", "Viagens"), "4": ("manutencoes", "Manutenções"),
        "5": ("abastecimentos", "Abastecimentos")
    }
    print("\\n--- Consultar registros ---")
    for chave, (_, nome) in opcoes.items():
        print(f"{chave}. {nome}")
    escolha = input("Categoria: ").strip()
    if escolha not in opcoes:
        print("Opção inválida.")
        return
    categoria, titulo = opcoes[escolha]
    registros = banco.listar(categoria)
    print(f"\\n--- {titulo}: {len(registros)} registro(s) ---")
    if not registros:
        print("Nenhum registro encontrado.")
    for indice, registro in enumerate(registros, 1):
        print(f"\\nRegistro {indice}")
        for campo, valor in registro.items():
            print(f"  {campo}: {valor}")


def gerar_relatorio():
    dados = banco.carregar()
    print("\\n" + "=" * 44)
    print("          RELATÓRIO DA FROTA")
    print("=" * 44)
    for categoria, titulo in [
        ("veiculos", "Veículos"), ("motoristas", "Motoristas"),
        ("viagens", "Viagens"), ("manutencoes", "Manutenções"),
        ("abastecimentos", "Abastecimentos")
    ]:
        print(f"{titulo}: {len(dados[categoria])}")

    print("\\nVeículos por tipo:")
    tipos = {}
    for item in dados["veiculos"]:
        tipo = item.get("tipo", "Não informado")
        tipos[tipo] = tipos.get(tipo, 0) + 1
    if tipos:
        for tipo, quantidade in sorted(tipos.items()):
            print(f"  {tipo}: {quantidade}")
    else:
        print("  Nenhum veículo cadastrado.")

    custo_manutencoes = sum(float(x.get("custo", 0)) for x in dados["manutencoes"])
    custo_abastecimentos = sum(float(x.get("valor_pago", 0)) for x in dados["abastecimentos"])
    distancia_total = sum(float(x.get("distancia", 0)) for x in dados["viagens"])
    print(f"\\nDistância total registrada em viagens: {distancia_total:.1f} km")
    print(f"Custo total de manutenções: R$ {custo_manutencoes:.2f}")
    print(f"Custo total de abastecimentos: R$ {custo_abastecimentos:.2f}")
    print(f"Custo total registrado: R$ {custo_manutencoes + custo_abastecimentos:.2f}")
    print("=" * 44)


def main():
    try:
        banco.carregar()
    except (OSError, ValueError) as erro:
        print(f"Não foi possível abrir o banco de dados: {erro}")
        return

    while True:
        print("\\n" + "=" * 44)
        print(" SISTEMA DE GERENCIAMENTO DE FROTA")
        print("=" * 44)
        print("1. Cadastrar veículo")
        print("2. Cadastrar motorista")
        print("3. Registrar viagem")
        print("4. Registrar manutenção")
        print("5. Registrar abastecimento")
        print("6. Consultar registros")
        print("7. Gerar relatório")
        print("0. Sair")
        opcao = input("Escolha uma opção: ").strip()

        acoes = {
            "1": cadastrar_veiculo, "2": cadastrar_motorista,
            "3": cadastrar_viagem, "4": cadastrar_manutencao,
            "5": cadastrar_abastecimento, "6": listar_registros,
            "7": gerar_relatorio
        }
        if opcao == "0":
            print("Encerrando. Os registros já foram salvos no JSON.")
            break
        acao = acoes.get(opcao)
        if not acao:
            print("Opção inválida.")
            continue
        try:
            acao()
        except (OSError, ValueError, TypeError, KeyError) as erro:
            print(f"Não foi possível concluir a operação: {erro}")


if __name__ == "__main__":
    main()
