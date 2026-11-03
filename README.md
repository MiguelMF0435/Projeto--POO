# Sistema de Gerenciamento de Frota de Veículos

## 1. Descrição do projeto

Sistema de linha de comando (CLI) para gerenciamento de uma frota de veículos de uma empresa de transporte.

O sistema tem como objetivo centralizar o cadastro e o controle de veículos e motoristas, permitindo registrar viagens, manutenções e abastecimentos, além de disponibilizar relatórios de desempenho e aplicar regras de negócio configuráveis.

O projeto é desenvolvido utilizando conceitos de Programação Orientada a Objetos, incluindo encapsulamento, herança simples, herança múltipla por meio de mixins, métodos especiais, tratamento de exceções, persistência de dados e testes automatizados.

## 2. Objetivos

- Gerenciar o cadastro de veículos da empresa.
- Gerenciar o cadastro de motoristas.
- Controlar manutenções preventivas e corretivas.
- Registrar abastecimentos e calcular o consumo dos veículos.
- Associar motoristas e veículos para realização de viagens.
- Atualizar automaticamente a quilometragem dos veículos.
- Impedir operações que violem as regras de negócio.
- Gerar relatórios de custos, consumo, viagens e quilometragem.
- Permitir que políticas sejam configuradas por meio de `settings.json`.
- Aplicar conceitos de POO de forma organizada e desacoplada.
- Separar as responsabilidades das classes de domínio, serviços e persistência.

---

# 3. Funcionalidades

## 3.1 Cadastro de veículos

O sistema deverá permitir:

- Criar veículos.
- Listar veículos.
- Consultar veículos.
- Atualizar informações.
- Excluir veículos.
- Alterar o status.
- Registrar eventos relacionados ao veículo.
- Consultar o histórico de eventos e manutenções.

### Dados do veículo

- Placa.
- Marca.
- Modelo.
- Tipo.
- Ano.
- Quilometragem.
- Consumo médio.
- Status.

### Tipos

- Carro.
- Moto.
- Caminhão.

### Status

Representados por um `Enum`:

- `ATIVO`
- `MANUTENCAO`
- `INATIVO`

### Histórico de eventos

- Entrada.
- Saída.
- Manutenção.
- Abastecimento.
- Desativação.
- Reativação.

## 3.2 Cadastro de motoristas

O sistema deverá permitir:

- Cadastrar motorista.
- Listar motoristas.
- Editar motorista.
- Remover motorista.
- Consultar disponibilidade.
- Consultar histórico de viagens.
- Verificar compatibilidade entre CNH e tipo de veículo.

### Dados

- Nome.
- CPF.
- Função.
- Categoria da CNH.
- Tempo de experiência em anos.
- Disponibilidade.
- Histórico de viagens.

O motorista será uma especialização da classe `Pessoa`, herdando seus atributos e comportamentos.

## 3.3 Manutenções

O sistema deverá permitir registrar manutenções associadas a um veículo.

### Dados

- Data.
- Tipo.
- Custo.
- Descrição.
- Veículo associado.
- Status.

### Tipos

- Preventiva.
- Corretiva.

Ao iniciar uma manutenção, o veículo deverá passar para `MANUTENCAO`. Ao concluir o serviço, poderá retornar para `ATIVO`.

O sistema deverá calcular o custo total e médio de manutenção por tipo de veículo.

## 3.4 Abastecimentos

O sistema deverá permitir registrar abastecimentos.

### Dados

- Data.
- Tipo de combustível.
- Litros.
- Valor pago.
- Veículo associado.
- Quilometragem no momento do abastecimento.

Os registros serão utilizados para calcular o consumo médio dos veículos e identificar aqueles fora da faixa configurada.

O histórico de abastecimentos deverá ser mantido pelo veículo por meio do `AbastecivelMixin`.

## 3.5 Viagens e alocação

O sistema deverá associar motorista e veículo e registrar cada viagem.

### Dados da viagem

- Motorista.
- Veículo.
- Origem.
- Destino.
- Distância percorrida.
- Data.

Após uma viagem, a quilometragem do veículo deverá ser atualizada automaticamente, e a viagem deverá ser adicionada ao histórico do motorista.

### Validações

A alocação deverá ser bloqueada quando:

- O veículo estiver em manutenção.
- O veículo estiver inativo.
- A CNH do motorista for incompatível.
- O motorista não estiver disponível.
- O veículo precisar realizar revisão preventiva obrigatória.

## 3.6 Relatórios

### Relatório de manutenção

- Custo total por tipo de veículo.
- Custo médio por tipo de veículo.
- Quantidade de manutenções realizadas.

### Relatório de combustível

- Consumo médio por veículo.
- Veículos fora do padrão.
- Ranking de eficiência de combustível.

### Relatório de motoristas

- Total de viagens por motorista.

### Relatório de quilometragem

- Quilometragem média por tipo de veículo.
- Quilometragem acumulada.
- Veículos com revisão preventiva vencida.

### Relatório de status da frota

- Quantidade de veículos ativos.
- Quantidade de veículos em manutenção.
- Quantidade de veículos inativos.

## 3.7 Configurações

As políticas e parâmetros serão armazenados em `settings.json`.

- Limite de quilometragem para revisão preventiva.
- Faixa mínima e máxima de consumo médio por tipo de veículo.
- Custos padrão por tipo de manutenção.
- Categoria mínima de CNH por tipo de veículo.

### Exemplo de configuração

```json
{
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
```

> Os valores são exemplos de configuração e poderão ser ajustados sem necessidade de modificar as classes de domínio.

---

# 4. Regras de negócio

## 4.1 Compatibilidade de CNH

| Tipo de veículo | Categoria mínima |
|---|---|
| Moto | A |
| Carro | B |
| Caminhão | C |

O sistema deverá impedir que um motorista seja associado a um veículo incompatível com sua CNH.

A validação deverá considerar as categorias superiores que também permitem a condução do veículo.

## 4.2 Revisão preventiva

A revisão preventiva deverá ocorrer de acordo com o limite configurado em `settings.json`.

O valor previsto na especificação é de **10.000 km**, mas deverá ser configurável.

O sistema deverá calcular a quilometragem percorrida desde a última revisão preventiva e bloquear novas viagens quando o limite for atingido.

## 4.3 Consumo

O consumo médio deverá ser calculado com base nos registros de abastecimento.

O valor calculado deverá ser comparado com a faixa configurada para o tipo de veículo.

Veículos fora da faixa deverão ser identificados nos relatórios.

## 4.4 Estados do veículo

Os estados serão representados por um `Enum`.

```text
ATIVO
  |
  | Iniciar manutenção
  v
MANUTENCAO
  |
  | Concluir manutenção
  v
ATIVO

ATIVO
  |
  | Desativar
  v
INATIVO
  |
  | Reativar
  v
ATIVO
```

Veículos em manutenção ou inativos não poderão ser alocados.

As transições de estado deverão ser validadas para impedir operações inconsistentes.

---

# 5. Modelagem Orientada a Objetos

## 5.1 Diagrama de classes simplificado

```text
                         Pessoa
                           |
                           v
                       Motorista
                           |
                           | realiza
                           v
                         Viagem
                           ^
                           |
                           | utiliza
                           |
                         Veiculo
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
        Carro             Moto           Caminhao
          |                |                |
          +----------------+----------------+
                           |
                +----------+----------+
                |                     |
                v                     v
        AbastecivelMixin      ManutenivelMixin
                |                     |
                v                     v
          Abastecimento           Manutencao
```

### Relacionamentos principais

```text
Pessoa
  |
  +-- Motorista
        |
        +-- realiza várias Viagens

Veiculo
  |
  +-- possui histórico de eventos
  |
  +-- possui histórico de Abastecimentos
  |
  +-- possui histórico de Manutenções
  |
  +-- participa de várias Viagens

Viagem
  |
  +-- referencia um Motorista
  |
  +-- referencia um Veiculo

Manutencao
  |
  +-- referencia um Veiculo

Abastecimento
  |
  +-- referencia um Veiculo
```

---

# 6. Classes, atributos e métodos

## 6.1 Veiculo

Classe base abstrata ou geral dos veículos.

Responsável por armazenar os dados comuns e controlar o comportamento dos veículos.

### Atributos privados

| Atributo | Descrição |
|---|---|
| `_placa` | Identificação do veículo |
| `_marca` | Fabricante |
| `_modelo` | Modelo do veículo |
| `_tipo` | Tipo de veículo |
| `_ano` | Ano de fabricação |
| `_quilometragem` | Quilometragem acumulada |
| `_consumo_medio` | Consumo médio em km/l |
| `_status` | Estado atual do veículo |

O acesso aos atributos deverá ser realizado por meio de propriedades (`@property`), com setters para os campos que permitirem alteração.

### Métodos principais

| Método | Responsabilidade |
|---|---|
| `atualizar_quilometragem(distancia: float)` | Atualizar a quilometragem após uma viagem |
| `alterar_status(novo_status)` | Modificar o estado do veículo mediante validação |
| `registrar_evento(evento)` | Adicionar um evento ao histórico |
| `__init__()` | Inicializar os atributos do veículo |

### Métodos especiais

| Método | Responsabilidade |
|---|---|
| `__str__()` | Retornar um resumo legível do veículo |
| `__repr__()` | Retornar uma representação adequada para depuração |
| `__eq__()` | Comparar veículos utilizando a placa |
| `__lt__()` | Permitir ordenar veículos pela quilometragem |
| `__iter__()` | Permitir iterar sobre o histórico de manutenções e eventos |

A comparação de igualdade deverá considerar a placa como identificador único.

A ordenação deverá considerar a quilometragem acumulada.

A iteração deverá disponibilizar os registros do histórico do veículo.

## 6.2 Carro

Especialização da classe `Veiculo`.

```python
class Carro(Veiculo):
    pass
```

Representa veículos do tipo carro.

Deverá herdar os atributos, propriedades e métodos da classe base.

## 6.3 Moto

Especialização da classe `Veiculo`.

```python
class Moto(Veiculo):
    pass
```

Representa veículos do tipo motocicleta.

Deverá herdar os atributos, propriedades e métodos da classe base.

## 6.4 Caminhao

Especialização da classe `Veiculo`.

```python
class Caminhao(Veiculo):
    pass
```

Representa veículos do tipo caminhão.

Deverá herdar os atributos, propriedades e métodos da classe base.

## 6.5 Pessoa

Classe base para representar pessoas cadastradas no sistema.

### Atributos privados

- `_nome`
- `_cpf`
- `_funcao`

O acesso aos atributos deverá ser controlado por propriedades.

A classe deverá centralizar as informações comuns às especializações de pessoas.

## 6.6 Motorista

Especialização da classe `Pessoa`.

```python
class Motorista(Pessoa):
    pass
```

### Atributos privados adicionais

| Atributo | Descrição |
|---|---|
| `_categoria_cnh` | Categoria da habilitação |
| `_experiencia_anos` | Tempo de experiência |
| `_disponibilidade` | Indica se o motorista está disponível |
| `_historico_viagens` | Lista de viagens realizadas |

### Métodos principais

| Método | Responsabilidade |
|---|---|
| `adicionar_viagem(viagem: Viagem)` | Adicionar uma viagem ao histórico |
| `verificar_compatibilidade(tipo_veiculo)` | Verificar se a CNH permite conduzir determinado veículo |

## 6.7 Viagem

Representa uma viagem realizada por um motorista utilizando um veículo.

### Atributos privados

- `_motorista`
- `_veiculo`
- `_origem`
- `_destino`
- `_distancia`
- `_data`

### Responsabilidades

- Associar motorista e veículo.
- Validar as condições necessárias para a alocação.
- Registrar a viagem.
- Atualizar a quilometragem do veículo.
- Adicionar a viagem ao histórico do motorista.

## 6.8 Manutencao

Representa uma manutenção realizada ou em andamento em um veículo.

### Atributos privados

- `_data`
- `_tipo`
- `_custo`
- `_descricao`
- `_veiculo`
- `_status`

### Tipos

- Preventiva.
- Corretiva.

### Responsabilidades

- Registrar os dados da manutenção.
- Associar a manutenção ao veículo.
- Controlar o andamento do serviço.
- Atualizar o status do veículo.
- Registrar a conclusão da manutenção.

## 6.9 Abastecimento

Representa um abastecimento realizado em determinado veículo.

### Atributos privados

- `_data`
- `_tipo_combustivel`
- `_litros`
- `_valor_pago`
- `_veiculo`
- `_quilometragem_momento`

### Responsabilidades

- Registrar o abastecimento.
- Associar o registro ao veículo.
- Atualizar o histórico de abastecimentos.
- Disponibilizar os dados para cálculo de consumo médio.

---

# 7. Herança e Mixins

## 7.1 Herança simples

A herança simples deverá permitir a reutilização de atributos e métodos das classes base.

### Hierarquia de veículos

```text
Veiculo
  |
  +-- Carro
  |
  +-- Moto
  |
  +-- Caminhao
```

### Hierarquia de pessoas

```text
Pessoa
  |
  +-- Motorista
```

## 7.2 Herança múltipla

A herança múltipla será utilizada por meio de mixins, permitindo adicionar comportamentos específicos às classes de veículos.

### AbastecivelMixin

Responsável pelas funcionalidades relacionadas ao abastecimento.

#### Atributos

- `_historico_abastecimentos`: lista contendo os abastecimentos realizados pelo veículo.

#### Métodos

- `abastecer(abastecimento: Abastecimento)`: registra um novo abastecimento e adiciona ao histórico.

### ManutenivelMixin

Responsável pelas funcionalidades relacionadas à manutenção.

#### Atributos

- `_historico_manutencoes`: lista contendo as manutenções associadas ao veículo.

#### Métodos

- `registrar_manutencao(manutencao: Manutencao)`: registra uma nova manutenção e adiciona ao histórico.

### Aplicação dos mixins

As especializações de veículos deverão combinar os comportamentos dos mixins por meio de herança múltipla.

Exemplo conceitual:

```python
class Carro(Veiculo, AbastecivelMixin, ManutenivelMixin):
    pass
```

A mesma composição poderá ser utilizada em `Moto` e `Caminhao`.

Os mixins deverão manter responsabilidades específicas, evitando concentrar funcionalidades distintas na classe `Veiculo`.

---

# 8. Encapsulamento

Os atributos das classes deverão ser privados ou protegidos por convenção, utilizando o prefixo `_`.

O acesso e a alteração dos atributos serão controlados por propriedades (`@property`).

### Exemplo

```python
class Veiculo:

    def __init__(self, placa, marca, modelo):
        self._placa = placa
        self._marca = marca
        self._modelo = modelo

    @property
    def placa(self):
        return self._placa

    @property
    def marca(self):
        return self._marca

    @marca.setter
    def marca(self, valor):
        if not valor:
            raise ValueError("A marca não pode ficar vazia.")

        self._marca = valor
```

### Validações previstas

- Quilometragem não pode ser negativa.
- Consumo não pode ser negativo.
- Dados obrigatórios não podem estar vazios.
- CPF e placa deverão ser identificadores únicos.
- CNH deve ser compatível com o veículo.
- Veículo em manutenção não pode ser alocado.
- Veículo inativo não pode ser alocado.
- Valores de abastecimento e manutenção deverão respeitar as validações correspondentes.

---

# 9. Métodos especiais

Os métodos especiais deverão ser implementados nas classes em que fizerem sentido, proporcionando comportamentos integrados aos recursos da linguagem Python.

| Método | Finalidade | Aplicação |
|---|---|---|
| `__str__()` | Resumo legível do objeto | Exibição de veículos |
| `__repr__()` | Representação para depuração | Inspeção de objetos |
| `__eq__()` | Comparação de igualdade | Comparação de veículos pela placa |
| `__lt__()` | Comparação de ordem | Ordenação pela quilometragem |
| `__iter__()` | Permitir iteração | Percorrer históricos de eventos e manutenções |

### Exemplos de utilização

```python
print(veiculo)
```

```python
print(repr(veiculo))
```

```python
veiculo_1 == veiculo_2
```

```python
veiculos_ordenados = sorted(veiculos)
```

```python
for evento in veiculo:
    print(evento)
```

---

# 10. Padrões de projeto

## 10.1 Repository

Responsável por abstrair a persistência dos dados.

```text
Repository
    |
    +-- JsonRepository
    |
    +-- SqliteRepository
```

Permite trocar a forma de armazenamento sem modificar as classes de domínio.

As operações de persistência deverão ser realizadas por meio de uma interface ou contrato comum.

## 10.2 Strategy

Poderá ser utilizado para implementar diferentes estratégias de cálculo, como custos de manutenção ou políticas de consumo.

```text
Strategy
    |
    +-- Basica
    |
    +-- Complexa
    |
    +-- Pesada
```

A estratégia escolhida poderá ser utilizada sem modificar a classe que executa o cálculo.

## 10.3 State / Enum

Os estados do veículo serão representados por `Enum`:

```python
from enum import Enum


class StatusVeiculo(Enum):
    ATIVO = "ATIVO"
    MANUTENCAO = "MANUTENCAO"
    INATIVO = "INATIVO"
```

O controle de estados deverá impedir transições inválidas.

## 10.4 Observer

Opcionalmente, poderá registrar ou comunicar automaticamente eventos, como conclusão de manutenção ou necessidade de revisão.

---

# 11. Persistência

A persistência deverá ser desacoplada das classes de domínio.

Inicialmente será utilizado JSON, com possibilidade de implementação de SQLite.

```text
Camada de domínio
        |
        v
Interface Repository
        |
        +-------------------+
        |                   |
        v                   v
 JsonRepository       SqliteRepository
        |                   |
        v                   v
 Arquivo JSON          Banco SQLite
```

### Requisitos

- Utilizar `json.dump()` e `json.load()` na implementação JSON.
- Permitir cadastrar, consultar, atualizar e remover registros.
- Manter os relacionamentos entre veículos, motoristas e transações.
- Garantir que os dados sejam recuperados após reiniciar o sistema.
- Tratar erros de leitura e gravação.
- Disponibilizar um conjunto inicial de dados (*seed*) para testes e demonstração.
- Permitir trocar a implementação do repositório sem modificar as classes de domínio.

O repositório deverá ser responsável pela conversão entre os dados persistidos e as informações utilizadas pelo sistema.

---

# 12. Tratamento de erros

Serão utilizadas exceções personalizadas para representar situações específicas do domínio e da persistência.

```text
ManutencaoInvalidaError
AlocacaoInvalidaError
PoliticaNaoAtendidaError
RepositorioError
```

### Descrição das exceções

| Exceção | Responsabilidade |
|---|---|
| `ManutencaoInvalidaError` | Representar operações inválidas relacionadas à manutenção |
| `AlocacaoInvalidaError` | Representar problemas de alocação, como veículo indisponível ou CNH incompatível |
| `PoliticaNaoAtendidaError` | Representar violações das políticas configuradas |
| `RepositorioError` | Representar falhas de leitura, gravação, consulta ou atualização dos dados persistidos |

### Exemplos

- Tentar iniciar manutenção em veículo inativo.
- Tentar concluir manutenção inexistente.
- Tentar alocar veículo em manutenção.
- Tentar alocar motorista com CNH incompatível.
- Tentar realizar viagem sem disponibilidade do motorista.
- Tentar registrar viagem quando a revisão preventiva estiver vencida.
- Falha ao carregar ou salvar dados no repositório.

---

# 13. Interface CLI

O sistema será disponibilizado por meio de uma interface de linha de comando.

A interface deverá permitir a execução das operações de cadastro, consulta, atualização, remoção, gerenciamento e geração de relatórios.

### Funcionalidades disponíveis

```text
01 - Cadastrar veículo
02 - Cadastrar motorista
03 - Consultar registros
04 - Registrar viagem / Alocar veículo
05 - Registrar manutenção
06 - Concluir manutenção
07 - Registrar abastecimento
08 - Gerenciar status dos veículos
09 - Editar veículo
10 - Remover veículo
11 - Relatórios da frota
00 - Encerrar sistema
```

### Interface visual

A biblioteca `Rich` será utilizada para melhorar a apresentação da interface no terminal.

Recursos utilizados:

- `Panel`: organização visual dos menus.
- `Table`: apresentação de registros e relatórios.
- `Prompt`: entrada e validação de informações.
- `Console`: gerenciamento da saída no terminal.
- Estilos e cores: diferenciação de mensagens de sucesso, erro e alerta.

A camada de interface deverá ser independente das regras de negócio e das classes de domínio.

---

# 14. Estrutura planejada

```text
Projeto-POO/
|
├── README.md
├── requirements.txt
├── settings.json
|
├── src/
|   |
|   ├── models/
|   |   ├── veiculo.py
|   |   ├── carro.py
|   |   ├── moto.py
|   |   ├── caminhao.py
|   |   ├── pessoa.py
|   |   ├── motorista.py
|   |   ├── viagem.py
|   |   ├── manutencao.py
|   |   └── abastecimento.py
|   |
|   ├── mixins/
|   |   ├── abastecivel.py
|   |   └── manutenivel.py
|   |
|   ├── repositories/
|   |   ├── repository.py
|   |   ├── json_repository.py
|   |   └── sqlite_repository.py
|   |
|   ├── services/
|   |   ├── frota_service.py
|   |   ├── manutencao_service.py
|   |   └── relatorio_service.py
|   |
|   ├── exceptions/
|   |   └── exceptions.py
|   |
|   └── cli/
|       └── main.py
|
├── data/
|   └── frota.json
|
└── tests/
    ├── test_veiculo.py
    ├── test_motorista.py
    ├── test_manutencao.py
    ├── test_abastecimento.py
    ├── test_viagem.py
    └── test_relatorios.py
```

> A estrutura é uma referência de organização arquitetural. A estrutura física do repositório poderá ser ajustada conforme a implementação, mantendo a separação de responsabilidades.

---

# 15. Testes

Os testes serão desenvolvidos com `pytest`.

O projeto deverá possuir pelo menos 15 testes, contemplando casos de sucesso e erro.

### Testes de veículos

- Criar veículo válido.
- Impedir quilometragem negativa.
- Comparar veículos pela placa.
- Ordenar veículos pela quilometragem.
- Alterar status.
- Registrar eventos.
- Testar iteração sobre o histórico.

### Testes de motoristas

- Criar motorista.
- Validar categoria da CNH.
- Verificar disponibilidade.
- Adicionar viagem ao histórico.
- Verificar compatibilidade com veículos.

### Testes de viagens

- Realizar alocação válida.
- Bloquear veículo em manutenção.
- Bloquear veículo inativo.
- Bloquear CNH incompatível.
- Bloquear motorista indisponível.
- Atualizar quilometragem após viagem.

### Testes de manutenção

- Registrar manutenção.
- Concluir manutenção.
- Impedir manutenção inválida.
- Atualizar status do veículo.
- Calcular custo médio.

### Testes de abastecimento

- Registrar abastecimento.
- Atualizar histórico.
- Calcular consumo.
- Identificar consumo fora da faixa.

### Testes de persistência e relatórios

- Salvar e recuperar dados.
- Tratar erros de persistência.
- Gerar relatórios de status.
- Gerar relatórios de manutenção.
- Gerar relatórios de consumo e viagens.

---

# 16. Type hints e documentação

O código deverá utilizar *type hints* nas funções e métodos, especificando os tipos dos parâmetros e retornos.

### Exemplo

```python
def atualizar_quilometragem(self, distancia: float) -> None:
    ...
```

Classes e métodos principais deverão possuir docstrings seguindo Google Style ou NumPy Style.

A documentação deverá descrever:

- Objetivo da classe.
- Responsabilidade dos métodos.
- Parâmetros recebidos.
- Valores retornados.
- Exceções que podem ser lançadas.

---

# 17. Como executar

## Pré-requisitos

- Python 3.x.
- Git.
- Pip.

## Clonar

```bash
git clone <URL_DO_REPOSITORIO>
```

## Entrar na pasta

```bash
cd Projeto--POO
```

## Criar ambiente virtual

```bash
python -m venv .venv
```

## Ativar no Windows

```bash
.venv\Scripts\activate
```

## Instalar dependências

```bash
pip install -r requirements.txt
```

### Dependências principais

```text
rich
pytest
```

## Executar

O comando deverá corresponder à estrutura de diretórios efetivamente utilizada no projeto.

Exemplo para a estrutura com diretório `classes`:

```bash
python classes/main.py
```

## Executar testes

```bash
pytest
```

Para obter uma saída mais detalhada:

```bash
pytest -v
```

---

# 18. Decisões de design

## Separação entre domínio e persistência

As classes de domínio não serão responsáveis diretamente por salvar ou carregar dados.

Essa responsabilidade ficará nos repositórios, permitindo alterar a tecnologia de armazenamento sem modificar as regras de negócio.

## Uso de herança

A hierarquia `Veiculo → Carro/Moto/Caminhao` representa especializações dos veículos.

A hierarquia `Pessoa → Motorista` permite reutilizar atributos e comportamentos comuns.

## Uso de mixins

Os mixins adicionam comportamentos específicos, como abastecimento e manutenção, evitando concentrar todas as responsabilidades em uma única classe.

## Encapsulamento

Os atributos serão protegidos por propriedades, permitindo validar os valores antes de realizar alterações nos objetos.

## Métodos especiais

Os métodos especiais serão utilizados para facilitar a representação, comparação, ordenação e iteração dos objetos.

## Enum

Os estados dos veículos serão representados por uma enumeração, evitando a utilização de valores textuais inconsistentes.

## Configurações externas

Políticas variáveis, como limite de revisão, consumo, custos e CNH mínima, ficarão no `settings.json`.

Dessa forma, os parâmetros poderão ser modificados sem alterar as classes de domínio.

## Interface independente

A interface CLI será responsável apenas pela interação com o usuário.

As regras de negócio deverão permanecer nas classes e serviços responsáveis por cada operação.

## Tratamento de erros

Exceções personalizadas serão utilizadas para representar erros específicos, facilitando a identificação e o tratamento de operações inválidas.

---

# 19. Critérios de aceite

- [ ] Herança simples.
- [ ] Herança múltipla com mixins.
- [ ] Encapsulamento com `@property`.
- [ ] Atributos privados nas classes principais.
- [ ] Utilização de `Enum` para os estados dos veículos.
- [ ] Métodos especiais `__str__`, `__repr__`, `__eq__`, `__lt__` e `__iter__`.
- [ ] Implementação de `AbastecivelMixin`.
- [ ] Implementação de `ManutenivelMixin`.
- [ ] Histórico de abastecimentos e manutenções nos veículos.
- [ ] Métodos de gerenciamento do histórico de viagens dos motoristas.
- [ ] Entidades de Viagem, Manutencao e Abastecimento.
- [ ] Exceções personalizadas.
- [ ] Pelo menos um padrão de projeto.
- [ ] Regras de negócio configuráveis.
- [ ] Validação de CNH.
- [ ] Bloqueio de veículos indisponíveis.
- [ ] Transições corretas de estado.
- [ ] Revisão preventiva configurável.
- [ ] Validação de consumo.
- [ ] Persistência desacoplada.
- [ ] Possibilidade de utilizar diferentes repositórios.
- [ ] Seed de dados.
- [ ] Pelo menos 15 testes.
- [ ] Pelo menos 3 relatórios.
- [ ] Type hints.
- [ ] Docstrings.
- [ ] Interface CLI funcional.
- [ ] Instruções de execução.
- [ ] README com modelagem e decisões de design.

---

# 20. Cronograma

## Semana 1 — Modelagem OO e definição

- Definição das classes.
- UML textual.
- README inicial.
- Classes iniciais e docstrings.

## Semana 2 — Classes e encapsulamento

- `Veiculo`, `Carro`, `Moto`, `Caminhao` e `Motorista`.
- `@property`.
- Métodos especiais.
- Primeiros testes.

## Semana 3 — Herança, relacionamentos e persistência

- Relacionamentos entre classes.
- Relação veículo/motorista.
- Viagens.
- Persistência JSON.
- Relatório inicial.

## Semana 4 — Regras e integração

- CNH.
- Bloqueios de alocação.
- Manutenção.
- Abastecimento.
- Atualização de quilometragem.
- CLI.
- Testes dos fluxos.

## Semana 5 — Refinamento e documentação

- Padrões de projeto.
- Relatórios consolidados.
- README final.
- Testes finais.
- Tag `v1.0`.

---

# 21. Tecnologias

- **Python:** linguagem de programação utilizada no desenvolvimento.
- **JSON:** persistência inicial dos dados.
- **SQLite:** alternativa de armazenamento.
- **Rich:** construção da interface visual no terminal.
- **pytest:** execução dos testes automatizados.
- **Git:** controle de versão.
- **GitHub:** hospedagem e colaboração no projeto.

---

# 22. Status do projeto

Projeto em desenvolvimento.

- [x] Definição do tema.
- [x] Levantamento inicial dos requisitos.
- [ ] Modelagem UML.
- [ ] Implementação das classes.
- [ ] Encapsulamento.
- [ ] Herança.
- [ ] Herança múltipla / Mixins.
- [ ] Persistência.
- [ ] Regras de negócio.
- [ ] Interface CLI.
- [ ] Relatórios.
- [ ] Testes.
- [ ] Documentação final.
- [ ] Release `v1.0`.
