# Sistema de Gestão de Entregas - GLOBAL HOSPITALAR

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3-black?logo=flask)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6?logo=typescript)

## 📖 Descrição do Projeto

O **Sistema de Gestão de Entregas** é uma aplicação Full Stack robusta, projetada para gerenciar e monitorar o ciclo de vida completo de entregas. A plataforma centraliza informações, automatiza o rastreamento através da integração com APIs de transportadoras e fornece ferramentas para gestão manual, garantindo um controle operacional eficiente e resiliente.

O sistema é composto por um **backend RESTful em Python/Flask** e um **frontend moderno e reativo em React/TypeScript**.

---

## ✨ Funcionalidades Principais

* **Autenticação Segura:** Sistema de login unificado para usuários e motoristas com JSON Web Tokens (JWT).
* **Gestão Completa de Entregas:**
    * Criação e visualização de entregas.
    * Importação em massa de entregas via planilhas (`.xlsx`, `.csv`).
    * Filtros avançados por status, data, transportadora, etc.
* **Rastreamento Híbrido:**
    * **Automação via API:** Sincronização automática com as APIs de diversas transportadoras para obter o status e o histórico em tempo real.
    * **Visualização Detalhada:** Um histórico de eventos de rastreamento é armazenado e exibido para cada entrega.
* **Gestão de Comprovantes e Devoluções:**
    * **Anexo Automatizado:** O sistema pode baixar e anexar o comprovante de entrega diretamente da API da transportadora.
    * **Upload Manual:** Interface para upload manual de comprovantes (canhotos, ressalvas) como fallback, garantindo que a operação nunca pare.
    * **Regras de Negócio:** Validação que exige um anexo antes de permitir a finalização de uma entrega.
* **Controle de Acesso Baseado em Papéis (RBAC):** Diferentes níveis de permissão para administradores, agentes e motoristas.

---

## 🛠️ Tecnologias Utilizadas

| Backend (API)                                                                   | Frontend (Interface)                                            |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| **Python 3.10+** | **React 18** (com Hooks)                                        |
| **Flask** & **Flask-SQLAlchemy** | **TypeScript** |
| **PostgreSQL** | **Vite** como ferramenta de build                             |
| **Flask-Migrate** (Alembic)                                                     | **Tailwind CSS** para estilização                               |
| **Flask-JWT-Extended** | **Axios** (ou Fetch API) para requisições                       |
| **Gunicorn** (Servidor de Produção)                                             |                                                                 |
| **Pandas** & **Openpyxl** (Leitura de Planilhas)                                |                                                                 |
| **Requests** (para consumir APIs externas)                                      |                                                                 |

---

## 🚀 Setup e Execução Local

Siga os passos abaixo para configurar o ambiente de desenvolvimento na sua máquina.

### Pré-requisitos
* Python 3.10 ou superior
* Node.js e npm
* PostgreSQL instalado e rodando

### 1. Clonar o Repositório
```bash
git clone [https://github.com/seu-usuario/Sistemagestao.git](https://github.com/seu-usuario/Sistemagestao.git)
cd Sistemagestao
```

### 2. Configuração do Backend
```bash
# Crie e ative um ambiente virtual
python -m venv venv
# No Windows:
# .\venv\Scripts\activate
# No Linux/Mac:
# source venv/bin/activate

# Instale as dependências Python
pip install -r requirements.txt

# Crie o arquivo de variáveis de ambiente
# (Renomeie .env.example para .env e preencha com suas credenciais)
cp .env.example .env

# Aplique as migrações no banco de dados
flask db upgrade
```

### 3. Configuração do Frontend
```bash
# Navegue até a pasta do frontend
cd frontend

# Instale as dependências do Node.js
npm install

# Crie o arquivo de variáveis de ambiente
# (Renomeie .env.example para .env e verifique a URL da API)
cp .env.example .env
```

### 4. Executando a Aplicação
Você precisará de dois terminais abertos.

* **Terminal 1 (Backend):** Na raiz do projeto (`Sistemagestao`), execute:
    ```bash
    python main.py
    ```
    *A API estará rodando em `http://127.0.0.1:5000`.*

* **Terminal 2 (Frontend):** Na pasta `frontend`, execute:
    ```bash
    npm run dev
    ```
    *A interface estará disponível em `http://localhost:5173`.*

---

## ☁️ Publicação (Deployment)

Este projeto está configurado para deploy em plataformas de nuvem modernas. A arquitetura recomendada é:

* **Backend (Flask API):** Publicado como um "Web Service" no **Render** ou **Azure App Service**.
* **Frontend (React App):** Publicado como um site estático no **Vercel** ou **Azure Static Web Apps**.

As variáveis de ambiente devem ser configuradas diretamente na plataforma de hospedagem para garantir a segurança das credenciais.

---

## 🗺️ Visão Geral dos Endpoints da API

Abaixo estão os principais endpoints disponíveis na API. Todos os endpoints protegidos exigem um Bearer Token JWT no cabeçalho `Authorization`.

### Autenticação (`/api/login`)
| Método | Endpoint | Descrição                                  |
|--------|----------|--------------------------------------------|
| `POST` | `/`      | Autentica um usuário ou motorista e retorna um JWT. |

### Entregas (`/api/entregas`)
| Método | Endpoint                    | Descrição                                  |
|--------|-----------------------------|--------------------------------------------|
| `GET`  | `/`                         | Lista todas as entregas (aceita filtros).   |
| `GET`  | `/<id>`                     | Busca uma entrega específica por ID.        |
| `POST` | `/importar-excel`           | Importa entregas de uma planilha.          |
| `GET`  | `/<id>/rastreamento`        | Retorna o histórico de rastreamento.        |
| `POST` | `/<id>/atualizar-rastreamento` | Gatilho para atualizar dados via API externa. |
| `PATCH`| `/finalizar/<id>`           | Finaliza uma entrega (com validações).     |

*(...e assim por diante para os outros recursos como `/usuarios`, `/comprovantes`, `/devolucoes`)*
