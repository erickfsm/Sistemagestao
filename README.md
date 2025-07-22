# Sistema de Gestão de Entregas (API Backend)

Este projeto implementa o backend de uma API RESTful para gerenciar entregas, incluindo atribuição de motoristas, gestão de comprovantes, controle de devoluções e autenticação de usuários com diferentes papéis.

## Funcionalidades Implementadas (API)

A API fornece os seguintes endpoints e funcionalidades, protegidos por autenticação JWT e controle de acesso baseado em RBAC:

-   **Gestão de Entregas (`/api/entregas`):**
    -   `POST /`: Cria uma nova entrega.
    -   `GET /`: Lista todas as entregas (com filtros por status, motorista, datas).
    -   `GET /<id>`: Busca uma entrega específica por ID.
    -   `PATCH /<id>/atribuir_motorista`: Atribui uma entrega a um motorista.
    -   `PATCH /<id>/finalizar`: Finaliza uma entrega (registra `DATAFINALIZACAO`).
    -   `POST /previsao/<id>`: Recalcula e salva a previsão de entrega para uma entrega existente.
    -   Cálculo dinâmico de `STATUS`, `DIASATRASO` e `PRAZOMEDIO` na resposta da entrega.

-   **Gestão de Usuários (`/api/usuarios`):**
    -   `POST /cadastro`: Registra um novo usuário (com `nome`, `login`, `senha`, `email` opcional e `role`).
    -   `POST /login`: Autentica um usuário e retorna um JWT (com `role` nas claims).
    -   `GET /perfil`: Retorna o perfil do usuário logado.
    -   `GET /`: Lista todos os usuários (apenas para `admin`).
    -   `GET /admin_teste`: Rota de teste acessível apenas por `admin`.
    -   `GET /agente_ou_admin_teste`: Rota de teste acessível por `agente` ou `admin`.

-   **Gestão de Motoristas (`/api/motoristas`):**
    -   `POST /cadastro`: Registra um novo motorista (acessível por `agente`, `admin`).
    -   `POST /login`: Login do motorista (retorna JWT).
    -   `GET /perfil`: Retorna o perfil do motorista logado.
    -   `GET /minhas_entregas`: Lista as entregas atribuídas ao motorista logado.
    -   `GET /`: Lista todos os motoristas (acessível por `agente`, `admin`).

-   **Gestão de Comprovantes (`/api/comprovantes`):**
    -   `POST /upload`: Envia um arquivo de comprovante e registra seus metadados.
    -   `GET /<id>`: Busca os detalhes de um comprovante por ID.
    -   `GET /<id>/download`: Permite o download do arquivo de comprovante.
    -   `GET /`: Lista todos os comprovantes (acessível por `agente`, `admin`).
    -   `GET /api/entregas/<id>/comprovantes`: Lista todos os comprovantes de uma entrega específica.
    -   `PATCH /<id>`: Atualiza detalhes de um comprovante.
    -   `DELETE /<id>`: Exclui um registro de comprovante e seu arquivo físico.

-   **Gestão de Devoluções (`/api/devolucoes`):**
    -   `POST /`: Registra uma nova devolução.
    -   `GET /<id>`: Busca os detalhes de uma devolução por ID.
    -   `GET /`: Lista todas as devoluções (acessível por `agente`, `admin`).
    -   `GET /api/entregas/<id>/devolucoes`: Lista as devoluções de uma entrega específica.
    -   `PATCH /<id>`: Atualiza detalhes de uma devolução.
    -   `PATCH /<id>/cancelar`: Marca uma devolução como 'cancelada' (mantendo o registro histórico).

## Tecnologias Utilizadas

-   **Python 3.10+**
-   **Flask:** Microframework web para Python.
-   **Flask-SQLAlchemy:** ORM para interação com banco de dados.
-   **Flask-Migrate (Alembic):** Para gerenciar migrações de banco de dados.
-   **Flask-JWT-Extended:** Para autenticação JWT.
-   **Werkzeug:** Utilitários de segurança (hashing de senha) e manipulação de arquivos (uploads).
-   **Workalendar:** Para cálculos de dias úteis e feriados (localidade Brasil).
-   **Psycopg2:** Adaptador PostgreSQL para Python.
-   **PostgreSQL:** Banco de dados relacional.
-   **python-dotenv:** Para carregar variáveis de ambiente.

## Configuração do Ambiente de Desenvolvimento

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/erickfsm/Sistemagestao.git](https://github.com/erickfsm/Sistemagestao.git)
    cd Sistemagestao
    ```
2.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    # No Windows (CMD/PowerShell)
    .\venv\Scripts\activate
    # No Linux/macOS (Bash/Zsh)
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    (Se o arquivo `requirements.txt` ainda não existir, gere-o com `pip freeze > requirements.txt`.)
4.  **Configure o Banco de Dados PostgreSQL:**
    * Crie um banco de dados PostgreSQL (ex: `global_log`).
    * Crie um usuário e senha (ex: `postgres`/`suasenha`).
    * Certifique-se de que o PostgreSQL está acessível do seu computador.
5.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto (na mesma pasta de `app/` e `config.py`) com o seguinte conteúdo:
    ```
    # Variáveis de Banco de Dados PostgreSQL
    DB_USER=seu_usuario_postgres
    DB_PASSWORD=sua_senha_postgres
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=global_log

    # Chaves Secretas
    # Gerar com 'import os; os.urandom(24).hex()' para FLASK_SECRET_KEY
    # Gerar com 'import os; os.urandom(32).hex()' para JWT_SECRET_KEY
    FLASK_SECRET_KEY=sua_chave_secreta_flask_aqui
    JWT_SECRET_KEY=sua_chave_secreta_jwt_aqui

    # Ambiente da Aplicação (Para debug e comportamento em desenvolvimento)
    FLASK_ENV=development
    ```
6.  **Inicialize e Execute as Migrações do Banco de Dados:**
    Com o ambiente virtual ativo, execute os seguintes comandos na raiz do projeto:
    ```bash
    flask db init
    flask db migrate -m "Initial database setup"
    flask db upgrade
    ```
    *(Se você já tem um banco de dados com dados, pode ser necessário ajustar as migrações ou usar `flask db stamp head` se houver problemas de sincronização. Em caso de dúvidas, consulte a documentação do Flask-Migrate.)*

7.  **Crie a Pasta de Uploads:**
    A aplicação espera uma pasta `uploads/comprovantes` na raiz do projeto. Esta pasta será criada automaticamente quando a aplicação for iniciada, mas certifique-se de que o usuário do sistema tem as permissões de escrita adequadas nela.

## Como Executar a Aplicação (API)

No terminal com o ambiente virtual ativado, execute:

```bash
python main.py
A API estará disponível em http://127.0.0.1:5000 (ou http://0.0.0.0:5000 para acesso externo na rede local, dependendo das configurações de rede).

**** Testando a API 

Consulte o código nas pastas app/routes/ para a lista completa de endpoints, seus métodos HTTP, e os requisitos de autenticação/papéis (@jwt_required(), @role_required(['role'])).

Exemplo de Fluxo de Teste:
Criar Usuário Administrador:

POST /api/usuarios/cadastro

Body (JSON): {"nome": "Admin Master", "email": "admin@example.com", "login": "admin.master", "senha": "securepassword", "role": "admin"}

Login do Administrador:

POST /api/usuarios/login

Body (JSON): {"login": "admin.master", "senha": "securepassword"}

Copie o access_token da resposta.

Criar um Usuário Motorista:

POST /api/usuarios/cadastro

Headers: Authorization: Bearer <ADMIN_TOKEN>

Body (JSON): {"nome": "Joao Motorista", "email": "joao.m@example.com", "login": "joao.driver", "senha": "driverpass", "role": "motorista"}

Login do Motorista:

POST /api/usuarios/login

Body (JSON): {"login": "joao.driver", "senha": "driverpass"}

Copie o access_token do motorista.

Criar uma Entrega:

POST /api/entregas

Headers: Authorization: Bearer <ADMIN_TOKEN>, Content-Type: application/json

Body (JSON): Verifique seu modelo Entrega para todos os campos nullable=False. Ex:

JSON

{
    "CODFILIAL": 1, "DTFAT": "2025-07-20 10:00:00", "DTCARREGAMENTO": "2025-07-21 09:00:00",
    "ROMANEIO": 1001, "TIPOVENDA": 1, "NUMNOTA": 12345, "NUMPED": 67890, "CODCLI": 101,
    "CLIENTE": "Cliente ABC", "MUNICIPIO": "Belo Horizonte", "UF": "MG",
    "VL_TOTAL": 100.50, "NUMVOLUME": 1, "TOTPESO": 5.0, "PRAZOENTREGA": 3,
    "CHAVENFE": "CHAVENFE012345678901234567890123456789012",
    "DATAFINALIZACAO": null, "AGENDAMENTO": null, "PREVISAOENTREGA": null
    // Outros campos opcionais podem ser omitidos ou null
}
Anote o id da entrega criada na resposta.

Atribuir Entrega ao Motorista:

PATCH /api/entregas/<ID_ENTREGA_CRIADA>/atribuir_motorista

Headers: Authorization: Bearer <ADMIN_TOKEN>, Content-Type: application/json

Body (JSON): {"motorista_id": <ID_DO_MOTORISTA_JOAO>}

Motorista Vê Suas Entregas:

GET /api/motoristas/minhas_entregas

Headers: Authorization: Bearer <MOTORISTA_JOAO_TOKEN>

Motorista Faz Upload de Comprovante:

POST /api/comprovantes/upload

Headers: Authorization: Bearer <MOTORISTA_JOAO_TOKEN>

Body: form-data com file (selecione um arquivo) e entrega_id (o ID da entrega atribuída).

Motorista Registra Devolução:

POST /api/devolucoes

Headers: Authorization: Bearer <MOTORISTA_JOAO_TOKEN>, Content-Type: application/json

Body (JSON): {"entrega_id": <ID_ENTREGA_CRIADA>, "tipo_devolucao": "Parcial", "motivo": "Produto avariado"}

*** Conclusão

Este projeto demonstra uma API RESTful robusta e segura para a gestão de entregas, com a implementação de funcionalidades essenciais para o ciclo de vida das operações logísticas. A arquitetura modular e o uso de tecnologias como Flask, PostgreSQL e JWT garantem escalabilidade e facilidade de manutenção.

Todas as funcionalidades do backend foram desenvolvidas e testadas em ambiente de desenvolvimento, provendo uma base sólida para a camada de frontend.

Feito por Erick.fsm