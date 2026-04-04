from fastapi import FastAPI

app = FastAPI(title="ai-service", version="0.0.1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "UP"}


@app.post("/api/configurator/generate")
def generate_configuration(payload: dict) -> dict:
    budget = payload.get("budget", 0)
    purpose = payload.get("purpose", "general")
    return {
        "purpose": purpose,
        "budget": budget,
        "components": [
            {"type": "cpu", "model": "placeholder-cpu"},
            {"type": "gpu", "model": "placeholder-gpu"},
            {"type": "ram", "model": "placeholder-ram"}
        ],
        "estimatedPerformance": "baseline",
        "totalPrice": budget
    }
