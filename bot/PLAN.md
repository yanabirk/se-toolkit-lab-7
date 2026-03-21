# LMS Telegram Bot - Development Plan

## Overview

This document outlines the implementation plan for the LMS Telegram Bot across four tasks. The bot provides students with access to their learning management system through Telegram, including lab information, scores, and Q&A capabilities powered by an LLM.

## Architecture Principles

### 1. Separation of Concerns
Handlers are pure functions that take input and return text. They have no dependency on Telegram. This enables:
- **Test mode**: `--test` flag calls handlers directly without Telegram
- **Unit testing**: Test handlers in isolation
- **Transport independence**: Same logic works with Telegram, CLI, or web

### 2. Configuration via Environment
All secrets (bot token, API keys) loaded from `.env.bot.secret` using pydantic-settings. This keeps secrets out of code and makes configuration explicit.

### 3. Layered Architecture
```
bot.py (entry point) → handlers/ (business logic) → services/ (external APIs)
```

## Task 1: Plan and Scaffold (Current)

**Goal**: Create project structure with testable handler architecture.

**Deliverables**:
- `bot/bot.py` - Entry point with `--test` mode
- `bot/handlers/` - Command handlers (no Telegram dependency)
- `bot/config.py` - Environment variable loading
- `bot/pyproject.toml` - Dependencies (aiogram, httpx, pydantic-settings)
- `bot/PLAN.md` - This document
- `.env.bot.example` - Template for environment variables

**Acceptance Criteria**:
- `cd bot && uv sync` works without errors
- `uv run bot.py --test "/start"` prints welcome message
- `uv run bot.py --test "/help"` prints command list
- All five commands (`/start`, `/help`, `/health`, `/labs`, `/scores`) work in test mode

## Task 2: Backend Integration

**Goal**: Connect handlers to the LMS backend API.

**Implementation**:
1. Create `bot/services/lms_api.py` - API client with Bearer token auth
2. Update handlers to call real API endpoints instead of placeholders
3. Add error handling for network failures, authentication errors
4. Create `.env.bot.secret` on VM with real credentials

**Key Pattern**: API client reads `LMS_API_BASE_URL` and `LMS_API_KEY` from environment. All requests include `Authorization: Bearer <key>` header.

**Acceptance Criteria**:
- `/health` returns actual backend status
- `/labs` fetches real lab list from backend
- `/scores <lab_id>` returns actual scores from backend
- Graceful error messages when backend is unavailable

## Task 3: Intent Recognition with LLM

**Goal**: Enable natural language queries like "what labs are available?"

**Implementation**:
1. Create `bot/services/llm_client.py` - LLM client for intent recognition
2. Define tool descriptions for each handler (what it does, when to call it)
3. Update `handle_message()` to use LLM for routing instead of regex
4. LLM decides which tool to call based on user input

**Key Insight**: The LLM reads tool descriptions to decide which function to call. Description quality matters more than prompt engineering.

**Acceptance Criteria**:
- Plain text queries work: "show my scores", "what labs exist"
- LLM correctly routes to appropriate handler
- Fallback to error message when LLM can't determine intent

## Task 4: Docker Deployment

**Goal**: Containerize the bot and deploy with docker-compose.

**Implementation**:
1. Create `bot/Dockerfile` - Multi-stage build with uv
2. Update `docker-compose.yml` to include bot service
3. Configure Docker networking (containers use service names, not localhost)
4. Set up health checks and restart policies

**Key Concept**: Docker containers communicate via service names. Bot connects to backend at `http://backend:8000`, not `localhost:8000`.

**Acceptance Criteria**:
- `docker compose up --build` starts all services
- Bot can reach backend via Docker network
- Bot reconnects automatically after failures

## File Structure

```
se-toolkit-lab-7/
├── bot/
│   ├── bot.py              # Entry point with --test mode
│   ├── config.py           # Settings loader
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── commands.py     # Command handlers
│   ├── services/
│   │   ├── __init__.py
│   │   ├── lms_api.py      # Backend API client (Task 2)
│   │   └── llm_client.py   # LLM client (Task 3)
│   ├── pyproject.toml      # Dependencies
│   └── PLAN.md             # This document
├── .env.bot.example        # Template (committed)
├── .env.bot.secret         # Real secrets (gitignored, VM only)
└── backend/
└── frontend/
└── docker-compose.yml
```

## Testing Strategy

1. **Test Mode**: `--test` flag for manual testing without Telegram
2. **Unit Tests**: Test handlers in isolation (future)
3. **Integration Tests**: Test full bot flow with mock Telegram (future)

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| LLM picks wrong tool | Improve tool descriptions, not regex fallbacks |
| Backend unavailable | Return graceful error messages, retry logic |
| Secrets in code | Use environment variables, gitignore `.env.bot.secret` |
| Docker networking issues | Use service names, not localhost |
