from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from datetime import datetime
import pandas as pd
import sqlite3
import os

# Base por defecto: demo
DB_NAME = os.getenv("CPRA_DB", "cpra_demo.db")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

# =========================
# 🔄 Función reutilizable de carga
# =========================

def load_data_from_db(app: FastAPI):
    """Cargar datos desde SQLite y actualizar app.state"""

    conn = sqlite3.connect(DB_PATH)
    df_local = pd.read_sql_query("SELECT * FROM donors", conn)
    conn.close()

    # Normalizar strings
    for col in df_local.columns:
        df_local[col] = df_local[col].astype(str).str.strip().str.upper()

    # Normalizar ABO
    df_local["abo"] = df_local["abo"].replace({"0": "O"})

    # Calcular frecuencias ABO
    frecuencias_local = df_local["abo"].value_counts(normalize=True).to_dict()

    # Columnas HLA
    columnas_hla = [
        col for col in df_local.columns if col not in ["donor_id", "abo"]
    ]

    antigens_validos = set(df_local[columnas_hla].values.flatten())
    antigens_validos = {a for a in antigens_validos if pd.notna(a)}

    # Guardar en memoria
    app.state.df = df_local
    app.state.frecuencias_abo = frecuencias_local
    app.state.valid_antigens = antigens_validos

    # Guardar metadata
    app.state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.state.total_donors = len(df_local)

    print("🔄 Base recargada. Donantes:", len(df_local))


# =========================
# 🔁 Lifespan moderno
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_data_from_db(app)
    yield


# =========================
# 🚀 Crear app
# =========================

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# 📥 Modelo de entrada
# =========================


class InputData(BaseModel):
    antigenos: list[str]
    abo: str | None = None
    mode: str = "freq"


# =========================
# 🧮 Endpoint cálculo cPRA
# =========================

@app.post("/calc_cpra")
def calc_cpra(data: InputData):

    df_local: pd.DataFrame = getattr(app.state, "df", pd.DataFrame())
    frecuencias_local = getattr(app.state, "frecuencias_abo", {})
    valid_antigens = getattr(app.state, "valid_antigens", set())

    if df_local.empty:
        return {"cPRA": 0.0}

    antigenos = [a.upper() for a in data.antigenos]
    abo = data.abo.upper() if data.abo else None

    invalid = [a for a in antigenos if a not in valid_antigens]

    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Antígenos inválidos: {invalid}"
        )

    columnas_hla = [
        col for col in df_local.columns if col not in ["donor_id", "abo"]
    ]

    mask_hla = df_local[columnas_hla].isin(antigenos).any(axis=1)
    df_incomp_hla = df_local[mask_hla]

    cpra_hla = len(df_incomp_hla) / len(df_local)

    abo_incompatibles = []

    if abo == "A":
        abo_incompatibles = ["B", "AB"]
    elif abo == "B":
        abo_incompatibles = ["A", "AB"]
    elif abo == "O":
        abo_incompatibles = ["A", "B", "AB"]
    elif abo == "AB":
        abo_incompatibles = []

    freq_abo_incomp = sum(
        frecuencias_local.get(g, 0) for g in abo_incompatibles
    )

    
    mode = data.mode.lower()

    if mode == "filter":
        mask_abo = df_local["abo"].isin(abo_incompatibles)
        mask_total = mask_hla | mask_abo
        cpra_final = mask_total.sum() / len(df_local)

    else:
        cpra_final = cpra_hla + ((1 - cpra_hla) * freq_abo_incomp)

    return {
    "cPRA": round(cpra_final * 100, 1),
    "N_donors": len(df_local),
    "mode_used": mode.upper(),
    "last_update": app.state.last_update
    }



# =========================
# 🔄 Endpoint recarga en caliente
# =========================

@app.post("/reload_db")
def reload_db():
    load_data_from_db(app)
    return {"status": "Base recargada correctamente"}


# =========================
# 📊 Endpoint metadata
# =========================

@app.get("/dataset_info")
def dataset_info():
    return {
        "total_donors": getattr(app.state, "total_donors", 0),
        "last_update": getattr(app.state, "last_update", "N/A")
    }


# =========================
# 🌐 Servir frontend
# =========================

@app.get("/", response_class=HTMLResponse)
def root_page():
    try:
        with open("frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h2>⚠️ Frontend no encontrado</h2>",
            status_code=404,
        )
