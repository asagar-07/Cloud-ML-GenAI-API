from fastapi import FastAPI
from api.routes.health_routes import router as health_router

app = FastAPI(
    title="Cloud ML & GenAI Deploy API",
    description="API foundation for ML and GenAI deployment project",
    version="0.1.0"
)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Cloud ML & GenAI Deploy API"
    }