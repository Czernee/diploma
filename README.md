# Diploma Microservices Monorepo

Initial scaffold for a diploma project: distributed hardware ordering platform with an AI PC configurator.

## Current Structure
- `api-gateway` (Spring Boot)
- `auth-service` (Spring Boot)
- `product-service` (Spring Boot)
- `order-service` (Spring Boot)
- `ai-service` (FastAPI)
- `frontend` (React + Vite + TypeScript)
- `docker-compose.yml` (PostgreSQL, Redis, Kafka)

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

Frontend is available at `http://localhost:5173` and proxies `/api/*` requests to `http://localhost:8080`.

## Health Endpoints
- API Gateway: `http://localhost:8080/actuator/health`
- Auth Service: `http://localhost:8081/actuator/health`
- Product Service: `http://localhost:8082/actuator/health`
- Order Service: `http://localhost:8083/actuator/health`
- AI Service: `http://localhost:8000/health`
