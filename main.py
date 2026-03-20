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
VALID_ABO_GROUPS = {"A", "B", "AB", "O"}
VALID_MODES = {"freq", "filter"}
NON_HLA_COLUMNS = {"donor_id", "sexo", "edad", "fecha_operativo", "abo", "rh"}
ABO_INCOMPATIBILITY = {
    "A": ["B", "AB"],
    "B": ["A", "AB"],
    "O": ["A", "B", "AB"],
    "AB": [],
}


def get_hla_columns(columns: list[str]) -> list[str]:
    """Identify HLA columns while excluding demographic and ABO metadata."""
    return [col for col in columns if col not in NON_HLA_COLUMNS]

# =========================
# 🔄 Función reutilizable de carga
# =========================

def load_data_from_db(app: FastAPI):
    """Cargar datos desde SQLite y actualizar app.state"""

    with sqlite3.connect(DB_PATH) as conn:
        df_local = pd.read_sql_query("SELECT * FROM donors", conn)

    # Normalizar strings
    for col in df_local.columns:
        df_local[col] = df_local[col].astype(str).str.strip().str.upper()

    # Normalizar ABO
    df_local["abo"] = df_local["abo"].replace({"0": "O"})

    # Calcular frecuencias ABO
    frecuencias_local = df_local["abo"].value_counts(normalize=True).to_dict()

    # Columnas HLA
    columnas_hla = get_hla_columns(df_local.columns.tolist())

    antigens_validos = {
        antigen
        for antigen in df_local[columnas_hla].stack().dropna().unique()
        if antigen
    }

    # Guardar en memoria
    app.state.df = df_local
    app.state.frecuencias_abo = frecuencias_local
    app.state.valid_antigens = antigens_validos
    app.state.hla_columns = columnas_hla

    # Guardar metadata
    app.state.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    app.state.total_donors = len(df_local)
    app.state.db_path = DB_PATH

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
    columnas_hla = getattr(app.state, "hla_columns", [])

    if df_local.empty:
        return {"cPRA": 0.0}

    antigenos = [a.strip().upper() for a in data.antigenos if a and a.strip()]
    abo = data.abo.upper() if data.abo else None
    mode = data.mode.lower().strip()

    if mode not in VALID_MODES:
        raise HTTPException(
            status_code=400,
            detail=f"Modo inválido: {data.mode}. Opciones: {sorted(VALID_MODES)}",
        )

    if abo and abo not in VALID_ABO_GROUPS:
        raise HTTPException(
            status_code=400,
            detail=f"Grupo ABO inválido: {data.abo}. Opciones: {sorted(VALID_ABO_GROUPS)}",
        )

    if not antigenos and not abo:
        raise HTTPException(
            status_code=400,
            detail="Debe enviar al menos un antígeno o un grupo ABO.",
        )

    invalid = [a for a in antigenos if a not in valid_antigens]

    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Antígenos inválidos: {invalid}"
        )

    mask_hla = df_local[columnas_hla].isin(antigenos).any(axis=1)
    df_incomp_hla = df_local[mask_hla]

    cpra_hla = len(df_incomp_hla) / len(df_local)

    abo_incompatibles = ABO_INCOMPATIBILITY.get(abo, [])

    freq_abo_incomp = sum(
        frecuencias_local.get(g, 0) for g in abo_incompatibles
    )

    
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
        "last_update": getattr(app.state, "last_update", "N/A"),
        "db_path": getattr(app.state, "db_path", DB_PATH),
        "hla_columns": getattr(app.state, "hla_columns", []),
        "valid_antigen_count": len(getattr(app.state, "valid_antigens", set())),
    }


@app.get("/reference_data")
def reference_data():
    return {
        "hla_columns": getattr(app.state, "hla_columns", []),
        "valid_antigens": sorted(getattr(app.state, "valid_antigens", set())),
        "abo_groups": sorted(VALID_ABO_GROUPS),
        "modes": sorted(VALID_MODES),
    }


# =========================
# 🌐 Servir frontend
# =========================

@app.get("/", response_class=HTMLResponse)
def root_page():
    try:
        frontend_path = os.path.join(BASE_DIR, "frontend", "index.html")
        with open(frontend_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h2>⚠️ Frontend no encontrado</h2>",
            status_code=404,
        )
