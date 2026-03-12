# MailerWeb Room Booking System

Sistema fullstack para gerenciamento de reservas de salas com notificações assíncronas por email.

## Stack Técnico

### Backend
- **Python 3.11** com **FastAPI**
- **PostgreSQL** para banco de dados
- **SQLAlchemy** como ORM
- **JWT** para autenticação
- **Padrão Outbox** + Worker para mensageria assíncrona
- **Celery/Redis** ou Worker simples para processamento de eventos

### Frontend
- **Next.js 14** (React) com App Router
- **TypeScript**
- **Tailwind CSS** para estilos
- **Zustand** para gerenciamento de estado
- **React Hook Form** + **Zod** para validação de formulários

## Funcionalidades

### Gerenciamento de Salas
- Criar, listar e visualizar salas
- Nome único obrigatório
- Capacidade válida

### Sistema de Reservas
- Criar, editar e cancelar reservas
- Validação de horários (start < end, 15min-8h)
- Detecção de conflitos de horários
- Controle de concorrência com locking
- Participantes por email

### Autenticação
- Registro e login de usuários
- JWT para autenticação
- Rotas protegidas

### Notificações por Email
- Eventos: BOOKING_CREATED, BOOKING_UPDATED, BOOKING_CANCELED
- Padrão Outbox para garantir entrega
- Worker com retry e idempotência

## Decisões Técnicas

### Controle de Concorrência
Para evitar reservas conflitantes criadas simultaneamente, utilizamos `SELECT FOR UPDATE` no PostgreSQL para adquirir um lock exclusivo na sala durante a verificação de conflitos. Isso garante que apenas uma transação por vez pode verificar e criar uma reserva para a mesma sala.

### Padrão Outbox
Utilizamos o padrão Outbox para garantir que as notificações por email sejam enviadas mesmo em caso de falhas:
1. A reserva e o evento são salvos na mesma transação
2. O worker processa eventos pendentes periodicamente
3. Retry automático com limite de tentativas
4. Idempotência via chave única por evento

### Detecção de Conflitos
A lógica de conflito verifica se existe sobreposição entre reservas ativas:
```
new_start < existing_end AND new_end > existing_start
```
Horários "encostados" (end == start) são permitidos.

## Execução Local

### Com Docker (Recomendado)

```bash
# Subir todos os serviços
docker-compose up -d

# Acessar:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - MailHog (emails): http://localhost:8025
```

### Sem Docker

#### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# Rodar o servidor
uvicorn app.main:app --reload --port 8000

# Em outro terminal, rodar o worker
python -m app.workers.simple_worker
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local

# Rodar o servidor de desenvolvimento
npm run dev
```

### Variáveis de Ambiente

#### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mailerweb
SECRET_KEY=your-secret-key-change-in-production
REDIS_URL=redis://localhost:6379/0
SMTP_HOST=localhost
SMTP_PORT=1025
```

#### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## Testes

### Backend
```bash
cd backend
pytest -v
```

### Frontend
```bash
cd frontend
npm test
```

## Estrutura do Projeto

```
desafio-mailerweb/
├── backend/
│   ├── app/
│   │   ├── api/           # Rotas da API
│   │   ├── core/          # Configurações e segurança
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── services/      # Lógica de negócio
│   │   └── workers/       # Worker para processar outbox
│   ├── tests/             # Testes unitários e integração
│   ├── alembic/           # Migrações
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Páginas (App Router)
│   │   ├── components/    # Componentes React
│   │   ├── lib/           # API client e store
│   │   ├── hooks/         # Custom hooks
│   │   └── types/         # TypeScript types
│   ├── __tests__/         # Testes
│   └── package.json
├── docker-compose.yml
└── README.md
```

## API Endpoints

### Autenticação
- `POST /api/auth/register` - Registrar usuário
- `POST /api/auth/login` - Login (retorna JWT)
- `GET /api/auth/me` - Dados do usuário atual

### Salas
- `GET /api/rooms/` - Listar salas
- `POST /api/rooms/` - Criar sala (autenticado)
- `GET /api/rooms/{id}` - Detalhes da sala
- `PUT /api/rooms/{id}` - Atualizar sala
- `DELETE /api/rooms/{id}` - Remover sala

### Reservas
- `GET /api/bookings/` - Listar reservas
- `GET /api/bookings/my` - Minhas reservas
- `POST /api/bookings/` - Criar reserva (autenticado)
- `GET /api/bookings/{id}` - Detalhes da reserva
- `PUT /api/bookings/{id}` - Atualizar reserva
- `POST /api/bookings/{id}/cancel` - Cancelar reserva

## Licença

Este projeto foi desenvolvido como parte do desafio técnico MailerWeb.
