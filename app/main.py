from fastapi import FastAPI
from app.api.controllers.health_controller import router as health_router
from app.api.controllers.auth_controller import router as auth_router
from app.api.controllers.doc_controller import router as doc_router
from app.api.controllers.dashboard_controller import router as dashboard_controller

app = FastAPI(
    title="Tender Data Analyzer API",
    description="API for analyzing tender data with dashboard endpoints",
    version="2.0.0",
    max_request_size=1073741824
)

@app.get("/")
def root():
    return {
        "message": "Tender Data Analyzer API v2.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(doc_router, prefix="/api/docs", tags=["documents"])
app.include_router(dashboard_controller, prefix="/api/dashboard", tags=["dashboard"])

