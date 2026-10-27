# 💳 Controle de Gastos — Finanças Pessoais

Aplicação web desenvolvida com Python e Flask para registro de receitas e despesas, acompanhamento financeiro, relatórios, gráficos e exportação de dados.

## Situação do projeto

**Desenvolvimento pausado, sem previsão de conclusão.**

O projeto ainda não está finalizado. Este repositório apresenta o código e as interfaces desenvolvidas até o momento.

As funcionalidades precisam de validação completa antes de uma utilização em produção.

## Contexto e objetivo

O projeto tem como objetivo reunir informações financeiras pessoais em um único ambiente.

A proposta é permitir o registro de receitas e despesas por categoria, a consulta do saldo e o acompanhamento dos gastos por meio de indicadores e relatórios.

## Recursos da versão atual

- Cadastro e autenticação de usuários.
- Dashboard com resumo financeiro.
- Registro de receitas e despesas.
- Classificação das transações por categoria.
- Informação de data e método de pagamento.
- Campo para descrição complementar.
- Indicadores de receitas, despesas, saldo e quantidade de transações.
- Gráficos de evolução financeira e gastos por categoria.
- Relatórios com seleção de período.
- Opções de exportação em CSV, Excel e PDF.
- Área de configurações do perfil.
- Gerenciamento de usuários para o administrador.

Os recursos listados fazem parte da versão em desenvolvimento e ainda precisam de testes integrados e revisão.

## 📸 Demonstração do sistema

As imagens apresentam a interface atual do projeto. Clique nas capturas para abrir os arquivos originais.

### Dashboard financeiro

Tela principal com indicadores de receitas, despesas, saldo e transações, acompanhados de gráficos de evolução mensal e distribuição dos gastos por categoria.

<a href="tela%20principal.png">
  <img src="tela%20principal.png" alt="Dashboard do Controle de Gastos" width="900">
</a>

### Nova transação

Formulário para registrar tipo, valor, título, categoria, data, método de pagamento e descrição complementar.

A interface também apresenta uma opção de transação recorrente, cujo comportamento deve ser validado durante a retomada do projeto.

<a href="nova%20transa%C3%A7%C3%A3o.png">
  <img src="nova%20transa%C3%A7%C3%A3o.png" alt="Formulário de nova transação financeira" width="900">
</a>

### Relatórios e exportação

Tela com filtros de período, totais de receitas e despesas, saldo, gráficos e opções de exportação.

<a href="relat%C3%B3rios%281%29.png">
  <img src="relat%C3%B3rios%281%29.png" alt="Relatórios financeiros e opções de exportação" width="900">
</a>

## Fluxo proposto de utilização

1. Criar uma conta e entrar na aplicação.
2. Registrar receitas e despesas.
3. Classificar os lançamentos por categoria.
4. Consultar os indicadores do dashboard.
5. Selecionar um período nos relatórios.
6. Analisar os gráficos e totais.
7. Exportar os dados para consulta externa.

## Organização das transações

| Informação | Finalidade |
|---|---|
| Tipo | Diferenciar receitas e despesas. |
| Valor | Registrar o montante da transação. |
| Título | Identificar o lançamento. |
| Categoria | Organizar a origem ou finalidade do valor. |
| Data | Definir quando a transação ocorreu. |
| Método de pagamento | Informar como a movimentação foi realizada. |
| Descrição | Acrescentar informações complementares. |

## Relatórios e indicadores

A interface apresenta recursos para acompanhar:

- Receitas do período.
- Despesas do período.
- Saldo.
- Quantidade de transações.
- Distribuição dos gastos por categoria.
- Evolução financeira.
- Consultas por semana, mês, ano ou todo o período.

## Exportação de dados

O projeto inclui opções de exportação nos formatos:

| Formato | Uso |
|---|---|
| CSV | Consulta e tratamento dos registros em outras ferramentas. |
| Excel | Organização dos dados em planilhas. |
| PDF | Apresentação dos relatórios em documento. |

A validação dos arquivos gerados faz parte das pendências para conclusão do projeto.

## Tecnologias

| Camada | Tecnologias |
|---|---|
| Backend | Python e Flask |
| Persistência | SQLAlchemy e Flask-SQLAlchemy |
| Banco de dados | SQLite |
| Autenticação | Flask-Login |
| Utilitários web e senhas | Werkzeug |
| Interface | HTML, CSS e JavaScript |
| Gráficos | Chart.js |
| Exportação e tratamento de dados | pandas, openpyxl e ReportLab |
| Versionamento | Git e GitHub |

## Organização do código

A aplicação está localizada na pasta `controle_gastos`.

```text
README.md

controle_gastos/
├── app.py
├── database.py
├── requirements.txt
├── README.md
└── templates/
    ├── base.html
    ├── dashboard.html
    ├── login.html
    ├── register.html
    ├── forgot.html
    ├── reports.html
    ├── users.html
    └── settings.html
```

- **app.py:** aplicação Flask e rotas.
- **database.py:** modelos e configuração de persistência.
- **requirements.txt:** dependências Python.
- **templates:** páginas da interface.
- **README.md da raiz:** apresentação principal do projeto.

## Próximas etapas

Quando o desenvolvimento for retomado, as prioridades são:

- Revisar os fluxos de cadastro e autenticação.
- Validar o registro e a consulta das transações.
- Conferir os cálculos de receitas, despesas e saldo.
- Validar os filtros dos relatórios.
- Testar as exportações CSV, Excel e PDF.
- Revisar o comportamento das transações recorrentes.
- Conferir as permissões administrativas.
- Melhorar o tratamento de erros.
- Validar a instalação em um ambiente limpo.

Não há prazo definido para essas etapas.

## Execução local

As instruções abaixo correspondem à estrutura atual do repositório. Como o projeto está incompleto, podem ser necessários ajustes no ambiente e na aplicação.

### 1. Clonar o repositório

```bash
git clone https://github.com/LovanGoulart/controle-gastos.git
cd controle-gastos
```

### 2. Criar um ambiente virtual

```bash
python -m venv .venv
```

### 3. Ativar o ambiente virtual

**Windows — Git Bash:**

```bash
source .venv/Scripts/activate
```

**Windows — Prompt de Comando:**

```bat
.venv\Scripts\activate.bat
```

**Linux ou macOS:**

```bash
source .venv/bin/activate
```

### 4. Instalar as dependências

```bash
python -m pip install -r controle_gastos/requirements.txt
```

### 5. Entrar na pasta da aplicação e iniciar

```bash
cd controle_gastos
python app.py
```

### 6. Acessar no navegador

```text
http://localhost:5000
```

## Autor

Desenvolvido por **Lovan Goulart** como projeto de controle financeiro pessoal.

[Perfil no GitHub](https://github.com/LovanGoulart)
