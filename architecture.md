# Diploma Architecture Baseline

## Repository Strategy
- Single monorepo with independent service modules.
- Java services are built as separate Spring Boot apps.
- AI service is a separate Python/FastAPI app.

## Modules
- `api-gateway` (port `8080`): single entrypoint for clients.
- `auth-service` (port `8081`): registration/auth/JWT.
- `product-service` (port `8082`): catalog and filtering.
- `order-service` (port `8083`): cart/order/status workflows.
- `ai-service` (port `8000`): intelligent PC configuration.

## Infrastructure
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Kafka (KRaft): `localhost:9092`

## Communication Model (Initial)
- REST for synchronous flows through `api-gateway`.
- Kafka events for order lifecycle (planned topics):
  - `order.created.v1`
  - `order.status.changed.v1`

## Next Implementation Steps
1. Add DB migrations and per-service schemas.
2. Add JWT issuance/validation in `auth-service` + `api-gateway`.
3. Add product and order domain models with persistence.
4. Add Kafka producer/consumer integration for order events.
5. Integrate `ai-service` from `api-gateway`.
