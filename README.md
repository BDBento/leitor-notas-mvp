# Leitor de Notas MVP

Sistema MVP para leitura automática de notas fiscais, comprovantes Pix e recibos utilizando OCR, com armazenamento estruturado de gastos mensais.

O projeto possui:

- Backend em FastAPI
- Frontend em React
- PostgreSQL
- OCR local com Tesseract
- Bot Telegram
- Docker Compose
- Autenticação JWT
- Dashboard web

---

# Objetivo

Automatizar o controle de gastos pessoais através do envio de imagens de:

- notas fiscais;
- comprovantes Pix;
- recibos;
- comprovantes de pagamento.

As imagens podem ser enviadas:

- pelo dashboard web;
- pelo bot do Telegram.

O sistema realiza:

1. upload da imagem;
2. OCR automático;
3. extração de dados;
4. classificação inicial;
5. armazenamento em banco de dados;
6. exibição em dashboard online.

---

# Tecnologias utilizadas

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Tesseract OCR
- Pillow
- Docker

## Frontend

- React
- Vite
- Fetch API

## Bot

- python-telegram-bot

---

# Arquitetura

```

Frontend React
        ↓
API FastAPI
        ↓
OCR Service
        ↓
Parser Service
        ↓
PostgreSQL

Telegram Bot
        ↓
Backend API

```
---

## Funcionalidades implementadas

```

Autenticação
Cadastro de usuários
Login JWT
Rotas protegidas
Controle de acesso por usuário
Uploads
Upload autenticado
Armazenamento de imagens
Proteção de arquivos privados
OCR
OCR local com Tesseract
Extração automática de:
valor;
data;
estabelecimento;
categoria inicial.
Dashboard
Login web
Upload de imagens
Listagem de gastos
Visualização de comprovantes
Soma total de gastos
Telegram
Recebimento de imagens
Upload automático para API
Processamento OCR
Retorno de informações processadas

```
---
```

leitor-notas-mvp/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   └── auth.py
│   │
│   ├── uploads/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── main.py
│
├── frontend/
│
├── bot-telegram/
│
├── docker-compose.yml
│
└── README.md

```
---


# Como executar
## Clonar projeto
git clone https://github.com/BDBento/leitor-notas-mvp.git


---

# Configurar variáveis .env

## Exemplo:

```

APP_NAME=Leitor de Notas MVP

DATABASE_URL=postgresql://leitor_user:leitor_pass@postgres:5432/leitor_notas

POSTGRES_DB=leitor_notas
POSTGRES_USER=leitor_user
POSTGRES_PASSWORD=leitor_pass

TELEGRAM_BOT_TOKEN=SEU_TOKEN

BACKEND_URL=http://backend:8000

SECRET_KEY=sua_chave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

BOT_USER_EMAIL=usuario@email.com
BOT_USER_PASSWORD=123456

```
---


Subir containers
docker compose up -d --build

----------------------------------------------------------

URLs do projeto

Frontend
http://localhost:5173

Backend API
http://localhost:8000

Swagger
http://localhost:8000/docs

Fluxo atual
Usuário envia imagem
        ↓
Upload autenticado
        ↓
OCR local
        ↓
Parser extrai dados
        ↓
Banco PostgreSQL
        ↓
Dashboard React

----------------------------------------------------------

Melhorias futuras
OCR híbrido (Tesseract + OpenAI Vision)
Filtros avançados
Relatórios mensais
Dashboard financeiro
Gráficos
Exportação Excel/PDF
Categorias inteligentes
Detecção automática de tipo de comprovante
Upload de PDF
Mobile App
Integração WhatsApp
Filas assíncronas com Celery/RabbitMQ
Status do projeto

----------------------------------------------------------

🚧 MVP em desenvolvimento

Projeto funcional em evolução contínua.

----------------------------------------------------------

Autor

Bruno Degan Bento

GitHub:
https://github.com/BDBento