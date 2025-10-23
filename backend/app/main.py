import os
import urllib
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from app.routers import main_router
from app.models.base import Base

app = FastAPI(title="EDD Backend", version="0.1.0")

# === CORS (debe ir antes de incluir routers) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Carga variables .env ===
load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
driver = os.getenv("DB_DRIVER")
encrypt = os.getenv("DB_ENCRYPT")
trust = os.getenv("DB_TRUST")

# === Conexión principal a SQL Server ===
params = urllib.parse.quote_plus(
    f"DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt={encrypt};TrustServerCertificate={trust};"
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# === Crear tablas si no existen ===
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "✅ Backend EDD operativo y CORS habilitado"}

# === Incluye routers ===
app.include_router(main_router.router, prefix="/api", tags=["EDD"])
