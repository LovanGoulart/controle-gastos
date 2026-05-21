# Sistema de Controle de Gastos Pessoais

Sistema web completo para controle financeiro pessoal, desenvolvido com Python, Flask, HTML, CSS e SQLite.

## Funcionalidades

- **Autenticacao**: Login, Cadastro e Recuperacao de Senha
- **Dashboard**: Painel principal com estatisticas e graficos
- **Transacoes**: Cadastro de receitas e despesas com categorias
- **Relatorios**: Graficos de evolucao mensal e gastos por categoria
- **Exportacao**: Exportar dados em CSV, Excel e PDF
- **Usuarios**: Gerenciamento de usuarios (admin)
- **Configuracoes**: Perfil do usuario

## Tecnologias

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite
- Chart.js
- Lucide Icons

## Instalacao

1. Clone ou extraia o projeto:
```bash
cd controle_gastos
```

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Instale as dependencias:
```bash
pip install -r requirements.txt
```

5. Execute o servidor:
```bash
python app.py
```

6. Acesse no navegador:
```
http://localhost:5000
```

## Primeiro Acesso

O primeiro usuario cadastrado automaticamente se torna **administrador**.

## Estrutura do Projeto

```
controle_gastos/
├── app.py              # Servidor Flask principal
├── database.py         # Modelos e configuracao do banco
├── requirements.txt    # Dependencias Python
├── README.md          # Este arquivo
├── static/            # Arquivos estaticos
│   ├── css/
│   └── js/
└── templates/         # Templates HTML
    ├── base.html      # Template base
    ├── login.html     # Login
    ├── register.html  # Cadastro
    ├── forgot.html    # Recuperar senha
    ├── dashboard.html # Dashboard
    ├── reports.html   # Relatorios
    ├── users.html     # Usuarios
    └── settings.html  # Configuracoes
```

## Licenca

MIT License
