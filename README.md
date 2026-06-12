# Diploma Microservices Monorepo

Distributed hardware ordering platform with a hybrid AI PC configurator.

## Current Structure
- `api-gateway` (Spring Boot)
- `auth-service` (Spring Boot)
- `product-service` (Spring Boot)
- `order-service` (Spring Boot)
- `ai-service` (FastAPI)
- `frontend` (React + Vite + TypeScript)
- `docker-compose.yml` (PostgreSQL, Redis, Kafka, frontend nginx)

## Prerequisites
- Java 21
- Maven wrapper (`./mvnw`)
- Docker + Docker Compose
- Python 3.13 (for local `ai-service` run)
- Node.js 18+ (for local `frontend` run)

## Infrastructure Start
```powershell
docker compose up -d
```

Docker Compose starts one PostgreSQL instance with three logical service databases:
- `diploma_auth` for `auth-service`
- `diploma_product` for `product-service`
- `diploma_order` for `order-service`

Redis is used for product catalog caching and server-side user carts. Kafka is used for order lifecycle events and asynchronous order status audit records.

The AI configurator is implemented as a hybrid intelligent module:
- expert rules validate hard compatibility constraints;
- a `GradientBoostingRegressor` model ranks compatible configuration candidates;
- an optional local LLM assistant understands natural-language user requests and answers chat questions;
- each recommendation response includes `ml_score`;
- model metadata is available at `/api/configurator/model`.

The LLM layer does not replace compatibility checks. It extracts user intent and parameters from a free-form phrase, then the existing configurator selects real products from the catalog.

## Local LLM Assistant
The project can run a local open LLM through Ollama. The demo default model is `qwen2.5:3b-instruct-q4_0`, because it is lighter for a local laptop and is enough to demonstrate natural-language chat and request extraction.

Install or start Ollama on the host machine, then pull the model:
```powershell
ollama pull qwen2.5:3b-instruct-q4_0
```

Run the whole project:
```powershell
docker compose up -d --build
```

By default, `ai-service` inside Docker connects to host Ollama through:
```text
http://host.docker.internal:11434
```

If you want to use a stronger model, pull it and override `OLLAMA_MODEL`:
```powershell
ollama pull qwen2.5:7b-instruct
$env:OLLAMA_MODEL="qwen2.5:7b-instruct"
docker compose up -d --build ai-service
```

Optional Docker-only Ollama mode:
```powershell
docker compose --profile llm up -d ollama
$env:OLLAMA_BASE_URL="http://ollama:11434"
docker compose exec ollama ollama pull qwen2.5:3b-instruct-q4_0
docker compose --profile llm up -d --build ai-service
```

The chat endpoint is available through the gateway at:
```text
POST /api/configurator/assistant
```

Example request:
```json
{
  "message": "Собери игровой ПК до 120000 рублей для 1440p, минимум 32 ГБ RAM, желательно NVIDIA"
}
```

Optional explicit ML training command, after `product-service` is available:
```powershell
cd ai-service
python train_model.py
```

## Build and Test Java Modules
```powershell
./mvnw test
```

## End-to-End Tests
E2E tests run through `api-gateway` and cover registration, login, product browse, order creation, and AI configurator.

1. Start Docker Desktop and run all services:
```powershell
docker compose up -d --build
```
2. Install E2E dependencies:
```powershell
python -m pip install -r e2e-tests/requirements.txt
```
3. Run E2E suite:
```powershell
python -m pytest e2e-tests -m e2e -q
```

Optional environment variables:
- `E2E_BASE_URL` (default: `http://localhost:8080`)
- `E2E_TIMEOUT_SECONDS` (default: `5`)

## Run Services Locally
Example for one Java service:
```powershell
./mvnw -pl auth-service spring-boot:run
```

Run AI service:
```powershell
cd ai-service
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Run frontend:
```powershell
cd frontend
npm install
npm run dev
```

Frontend is available at `http://localhost:5173` in Docker. Its nginx container proxies `/api/*` requests to `api-gateway`.

For local development, `npm run dev` still starts Vite at `http://localhost:5173` and proxies `/api/*` requests to `http://localhost:8080`.

## Health Endpoints
- API Gateway: `http://localhost:8080/actuator/health`
- Auth Service: `http://localhost:8081/actuator/health`
- Product Service: `http://localhost:8082/actuator/health`
- Order Service: `http://localhost:8083/actuator/health`
- AI Service: `http://localhost:8000/health`
