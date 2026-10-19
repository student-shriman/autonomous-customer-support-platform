"""
Autonomous Customer Support Platform - FastAPI Application Entrypoint.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.services.seed_data import seed_initial_data

from backend.app.api.health import router as health_router
from backend.app.api.auth import router as auth_router
from backend.app.api.tickets import router as tickets_router
from backend.app.api.chat import router as chat_router
from backend.app.api.hitl import router as hitl_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database & Seed
    print(f"🚀 Starting {settings.PROJECT_NAME}...")
    try:
        await init_db()
        async with AsyncSessionLocal() as session:
            await seed_initial_data(session)
    except Exception as e:
        print(f"⚠️ Startup database initialization note: {e}")
    yield
    print("🛑 Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Enterprise-grade autonomous multi-agent customer support and resolution platform.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(health_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(hitl_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Autonomous Customer Support Platform API Online",
        "docs_url": "/docs",
        "health_url": "/health",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
