
# main.py

from banco import BancoDeDados
from veiculos import Carro, Moto, Caminhao
from pessoa import Motorista


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


def cadastrar_veiculo():
    print("\n--- Cadastro de veículo ---")
    print("1. Carro")
    print("2. Moto")
    print("3. Caminhão")

    opcoes = {
        "1": Carro,
        "2": Moto,
        "3": Caminhao,
    }

    tipo = input("Tipo de veículo: ").strip()

    if tipo not in opcoes:
        print("Tipo inválido.")
        return

    placa = ler_texto("Placa: ").upper()

    dados = banco.carregar()
    if any(v.get("placa", "").upper() == placa
           for v in dados["veiculos"]):
        print("Já existe um veículo cadastrado com essa placa.")
        return

    marca = ler_texto("Marca: ")
    modelo = ler_texto("Modelo: ")
    ano = ler_int("Ano: ", 1886)
    quilometragem = ler_float("Quilometragem: ", 0)
    consumo = ler_float("Consumo médio: ", 0)
    status = ler_texto("Status (disponível, em viagem, manutenção etc.): ")

    veiculo = opcoes[tipo](
        placa,
        marca,
        modelo,
        ano,
        quilometragem,
        consumo,
        status,
    )

    registro = {
        "placa": veiculo.placa,
        "marca": veiculo.marca,
        "modelo": veiculo.modelo,
        "tipo": veiculo.tipo,
        "ano": veiculo.ano,
        "quilometragem": veiculo.quilometragem,
        "consumo_medio": veiculo.consumo_medio,
        "status": veiculo.status,
    }

    banco.adicionar("veiculos", registro)
    print("Veículo cadastrado e salvo com sucesso!")


def cadastrar_motorista():
    print("\n--- Cadastro de motorista ---")

    cpf = ler_texto("CPF: ")

    dados = banco.carregar()
    if any(m.get("cpf") == cpf for m in dados["motoristas"]):
        print("Já existe um motorista cadastrado com esse CPF.")
        return

    nome = ler_texto("Nome: ")
    funcao = ler_texto("Função: ")
    categoria_cnh = ler_texto("Categoria da CNH: ").upper()
    experiencia = ler_int("Anos de experiência: ", 0)

    print("Disponibilidade:")
    print("1. Disponível")
    print("2. Indisponível")
    opcao = input("Escolha: ").strip()

    if opcao not in ("1", "2"):
        print("Opção inválida.")
        return

    disponibilidade = opcao == "1"

    motorista = Motorista(
        nome,
        cpf,
        funcao,
        categoria_cnh,
        experiencia,
        disponibilidade,
    )

    registro = {
        "nome": motorista.nome,
        "cpf": motorista.cpf,
        "funcao": motorista.funcao,
        "categoria_cnh": motorista.categoria_cnh,
        "experiencia_anos": motorista.experiencia_anos,
        "disponibilidade": motorista.disponibilidade,
        "historico_viagens": [],
    }

    banco.adicionar("motoristas", registro)
    print("Motorista cadastrado e salvo com sucesso!")


def listar_registros():
    categorias = {
        "1": ("veiculos", "Veículos"),
        "2": ("motoristas", "Motoristas"),
        "3": ("viagens", "Viagens"),
        "4": ("manutencoes", "Manutenções"),
        "5": ("abastecimentos", "Abastecimentos"),
    }

    print("\n--- Consultar registros ---")
    for chave, (_, nome) in categorias.items():
        print(f"{chave}. {nome}")

    opcao = input("Escolha a categoria: ").strip()

    if opcao not in categorias:
        print("Opção inválida.")
        return

    categoria, nome = categorias[opcao]
    registros = banco.listar(categoria)

    print(f"\n--- {nome} cadastrados: {len(registros)} ---")

    if not registros:
        print("Nenhum registro encontrado.")
        return

    for indice, registro in enumerate(registros, start=1):
        print(f"\nRegistro {indice}")
        for campo, valor in registro.items():
            print(f"  {campo}: {valor}")


def gerar_relatorio():
    dados = banco.carregar()

    print("\n" + "=" * 40)
    print("       RELATÓRIO DA FROTA")
    print("=" * 40)

    print(f"Total de veículos: {len(dados['veiculos'])}")
    print(f"Total de motoristas: {len(dados['motoristas'])}")
    print(f"Total de viagens: {len(dados['viagens'])}")
    print(f"Total de manutenções: {len(dados['manutencoes'])}")
    print(f"Total de abastecimentos: {len(dados['abastecimentos'])}")

    print("\nVeículos por tipo:")
    tipos = {}
    for veiculo in dados["veiculos"]:
        tipo = veiculo.get("tipo", "Não informado")
        tipos[tipo] = tipos.get(tipo, 0) + 1

    if tipos:
        for tipo, quantidade in sorted(tipos.items()):
            print(f"  {tipo}: {quantidade}")
    else:
        print("  Nenhum veículo cadastrado.")

    custo_manutencoes = sum(
        float(registro.get("custo", 0))
        for registro in dados["manutencoes"]
    )
    custo_abastecimentos = sum(
        float(registro.get("valor_pago", 0))
        for registro in dados["abastecimentos"]
    )

    print(f"\nCusto total de manutenções: R$ {custo_manutencoes:.2f}")
    print(f"Custo total de abastecimentos: R$ {custo_abastecimentos:.2f}")
    print("=" * 40)


def main():
    # Cria o arquivo, se necessário, e verifica se pode ser carregado.
    try:
        banco.carregar()
    except (OSError, ValueError) as erro:
        print(f"Não foi possível abrir o banco de dados: {erro}")
        return

    while True:
        print("\n" + "=" * 40)
        print(" SISTEMA DE GERENCIAMENTO DE FROTA")
        print("=" * 40)
        print("1. Cadastrar veículo")
        print("2. Cadastrar motorista")
        print("3. Consultar registros")
        print("4. Gerar relatório")
        print("0. Sair")

        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                cadastrar_veiculo()
            elif opcao == "2":
                cadastrar_motorista()
            elif opcao == "3":
                listar_registros()
            elif opcao == "4":
                gerar_relatorio()
            elif opcao == "0":
                print("Dados salvos. Encerrando o sistema.")
                break
            else:
                print("Opção inválida.")
        except (OSError, ValueError, TypeError) as erro:
            print(f"Não foi possível concluir a operação: {erro}")


if __name__ == "__main__":
    main()
