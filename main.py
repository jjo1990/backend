from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db.database import create_db_and_tables
from routers import categorias, ingredientes, productos, auth, direcciones, pedidos, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Se ejecuta al arrancar el servidor.
    Crea las tablas en la DB si no existen.
    """
    create_db_and_tables()
    yield


app = FastAPI(
    title="API Parcial - Restaurante",
    description="Sistema de gestión de productos con categorías e ingredientes",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: permite que el frontend (en otro puerto) hable con el backend
# Sin esto, el navegador bloquea las peticiones por seguridad
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # store-app y admin-app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos los routers (cada uno trae sus endpoints)
app.include_router(categorias.router)
app.include_router(ingredientes.router)
app.include_router(productos.router)
app.include_router(auth.router)
app.include_router(direcciones.router)
app.include_router(pedidos.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"mensaje": "API funcionando", "docs": "/docs"}
