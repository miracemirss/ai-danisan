# app/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models
from app.routers import auth
from app.routers import appointment
from app.routers import clients
from app.routers import practitioners
from app.routers import sessions
from app.routers import reports
from app.routers import session_notes
from app.routers import subscription_plans
from app.routers import subscriptions
from app.routers import ai_jobs
from app.routers import ai_summaries
from app.routers import tenants
from app.routers import client_consents
API_PREFIX = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama yaşam döngüsü:
    - Startup: DB tablolarını oluştur
    - Shutdown: Şimdilik özel bir şey yapmıyoruz
    """
    # --- STARTUP ---
    Base.metadata.create_all(bind=engine)
    yield
    # --- SHUTDOWN ---
    # İleride background task cleanup vs. eklenebilir.


app = FastAPI(
    title="AI Danışan Takip Asistanı API",
    version="0.1.0",
    lifespan=lifespan,
)


# --- CORS Ayarları (Frontend için) ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    # Geliştirme sürecinde hepsine izin istersen aşağıyı da açabilirsin:
    # "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Healthcheck / Root ---
@app.get("/", tags=["system"])
def read_root():
    return {
        "status": "ok",
        "message": "AI Danışan API is running",
        "version": "0.1.0",
    }


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "healthy"}


# --- Routers ---

# Auth endpoints:
# POST   /api/v1/auth/register
# POST   /api/v1/auth/login
# GET    /api/v1/auth/me
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(appointment.router, prefix=API_PREFIX)
app.include_router(clients.router, prefix=API_PREFIX)
app.include_router(practitioners.router, prefix=API_PREFIX)
app.include_router(sessions.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(session_notes.router, prefix=API_PREFIX)
app.include_router(subscription_plans.router, prefix=API_PREFIX)
app.include_router(subscriptions.router, prefix=API_PREFIX)
app.include_router(ai_jobs.router, prefix=API_PREFIX)
app.include_router(ai_summaries.router, prefix=API_PREFIX)
app.include_router(tenants.router, prefix=API_PREFIX)
app.include_router(client_consents.router, prefix=API_PREFIX)