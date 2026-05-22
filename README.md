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
- Multiusuário
- Analytics financeiros
- Exportação CSV
- Dashboard profissional com sidebar

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
4. classificação inteligente;
5. armazenamento em banco de dados;
6. analytics financeiros;
7. visualização em dashboard web;
8. gerenciamento multiusuário.

---

# Tecnologias utilizadas

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Tesseract OCR
- Pillow
- Passlib
- Python Requests
- Docker

## Frontend

- React
- Vite
- Fetch API
- Recharts
- CSS customizado

## Bot

- python-telegram-bot

---

# Arquitetura

```text
Frontend React
        ↓
API FastAPI
        ↓
OCR Service
        ↓
Parser Inteligente
        ↓
PostgreSQL

Telegram Bot
        ↓
Backend API
```

---

# Funcionalidades implementadas

## 🔐 Autenticação

- Cadastro de usuários
- Login JWT
- Rotas protegidas
- Controle de acesso por usuário
- Sessões autenticadas
- Recuperação de senha via Telegram
- Integração automática de usuários Telegram

---

## 📤 Uploads

- Upload autenticado
- Armazenamento de imagens
- Proteção de arquivos privados
- Upload via dashboard
- Upload via Telegram
- Preview autenticado de imagens
- Suporte para:
  - JPG
  - JPEG
  - PNG
  - PDF

---

## 🤖 OCR Inteligente

OCR local com Tesseract.

Extração automática de:

- valor;
- data;
- estabelecimento;
- categoria;
- forma de pagamento.

---

## 🧠 Parser Inteligente

Reconhecimento automático de:

- comprovantes Nubank;
- Pix;
- transferências;
- comprovantes bancários;
- notas fiscais.

Tratamento de:

- OCR com ruído;
- linhas quebradas;
- datas textuais;
- informações técnicas do comprovante.

---

## 📊 Dashboard Financeiro

- Login web
- Sidebar profissional
- Upload de imagens
- Listagem de gastos
- Visualização autenticada de comprovantes
- Soma total de gastos
- Filtro mensal
- Dashboard financeiro
- Gráfico de gastos por categoria
- Ranking financeiro
- Analytics financeiros
- Edição manual de registros
- Exclusão de gastos
- Perfil do usuário
- Alteração de senha
- Exportação CSV

---

## 📱 Telegram

- Cadastro automático de usuários
- Geração automática de login web
- Reset de senha via comando
- Recebimento de imagens
- Upload automático para API
- Processamento OCR
- Retorno de informações processadas
- Multiusuário

---

# Estrutura do projeto

```text
leitor-notas-mvp/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── main.py
│   │
│   ├── uploads/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── services/
│   │
│   ├── package.json
│   └── Dockerfile
│
├── bot-telegram/
│   ├── bot.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
│
└── README.md
```

---

# Como executar

## Clonar projeto

```bash
git clone https://github.com/BDBento/leitor-notas-mvp.git
```

---

# Configurar variáveis `.env`

## Exemplo:

```env
APP_NAME=Leitor de Notas MVP
APP_ENV=development

DATABASE_URL=postgresql://leitor_user:leitor_pass@postgres:5432/leitor_notas

POSTGRES_DB=leitor_notas
POSTGRES_USER=leitor_user
POSTGRES_PASSWORD=leitor_pass

TELEGRAM_BOT_TOKEN=SEU_TOKEN

BACKEND_URL=http://backend:8000

UPLOAD_DIR=/app/uploads

SECRET_KEY=sua_chave_secreta_super_segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

---

# Subir containers

```bash
docker compose up -d --build
```

---

# URLs do projeto

## Frontend

```text
http://localhost:5173
```

## Backend API

```text
http://localhost:8000
```

## Swagger

```text
http://localhost:8000/docs
```

---

# Fluxo atual

```text
Usuário envia imagem
        ↓
Upload autenticado
        ↓
OCR local
        ↓
Parser inteligente
        ↓
Banco PostgreSQL
        ↓
Dashboard React
        ↓
Analytics financeiros
```

---

# Fluxo Telegram

```text
Usuário inicia bot
        ↓
Cadastro automático
        ↓
Geração de login web
        ↓
Recebe senha temporária
        ↓
Envia comprovante
        ↓
OCR automático
        ↓
Dados registrados no dashboard
```

---

# Segurança implementada

- JWT Authentication
- Rotas protegidas
- Controle de acesso por usuário
- Upload autenticado
- Proteção de arquivos privados
- Multiusuário
- Reset de senha
- Separação de dados por usuário
- Visualização autenticada de imagens

---

# Analytics implementados

- Total de gastos
- Quantidade de comprovantes
- Ranking por categoria
- Gráfico financeiro
- Dashboard mensal
- Exportação CSV

---

# Melhorias futuras

## OCR e IA

- OCR híbrido (Tesseract + OpenAI Vision)
- IA para categorização automática
- IA para correção de OCR
- IA para insights financeiros
- Detecção automática do tipo de comprovante

---

## Dashboard

- Tema dark/light
- Dashboard avançado
- Comparativo mensal
- Metas financeiras
- Insights automáticos
- Exportação Excel/PDF
- Relatórios financeiros
- Upload drag-and-drop

---

## Infraestrutura

- Filas assíncronas com Celery/RabbitMQ
- Cache Redis
- Storage externo
- Deploy cloud
- Observabilidade e logs

---

## Plataformas

- Mobile App
- Integração WhatsApp
- Integração bancária
- API pública

---

# Status do projeto

## 🚧 MVP em desenvolvimento

Projeto funcional em evolução contínua.

Atualmente já possui:

- autenticação;
- OCR;
- parser inteligente;
- dashboard financeiro;
- analytics;
- Telegram;
- multiusuário;
- uploads protegidos;
- gerenciamento de usuários;
- exportação CSV;
- categorização automática;
- sidebar profissional.

---

# Autor

## Bruno Degan Bento

GitHub:

```text
https://github.com/BDBento
```