from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os

# 🚀 Crear la app FastAPI
app = FastAPI(title="cPRA 3.0 - CSV version")

# ✅ Habilitar CORS (para conexión con frontend o pruebas locales)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción conviene restringirlo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧾 Ruta del archivo CSV (ajustar si está en otra carpeta)
CSV_PATH = os.path.join("data", "donors.csv")

# 📥 Modelo de datos que recibe el endpoint
class InputData(BaseModel):
    antigenos: list[str]
    abo: str | None = None

# 📡 Endpoint principal para calcular el cPRA
@app.post("/calc_cpra")
def calc_cpra(data: InputData):
    antigenos = [a.upper() for a in data.antigenos]
    abo = data.abo

    # 📊 Leer tabla de donantes
    try:
        df = pd.read_csv(CSV_PATH, sep=";", dtype=str)
    except FileNotFoundError:
        return {"error": f"No se encontró el archivo: {CSV_PATH}"}

    total_donantes = len(df)
    if total_donantes == 0:
        return {"cPRA": 0.0}

    # 🚫 Incompatibilidades por ABO
    if abo:
        if abo == "A":
            df_incomp_abo = df[~df["abo"].isin(["A", "O"])]
        elif abo == "B":
            df_incomp_abo = df[~df["abo"].isin(["B", "O"])]
        elif abo == "AB":
            df_incomp_abo = pd.DataFrame()  # AB acepta todos
        elif abo == "O":
            df_incomp_abo = df[df["abo"] != "O"]
        else:
            df_incomp_abo = pd.DataFrame()
    else:
        df_incomp_abo = pd.DataFrame()

    # 🚫 Incompatibilidades por HLA
    df_incomp_hla = df[df.apply(lambda row: any(
        ant in row.values for ant in antigenos), axis=1)]

    # 🔀 Combinar incompatibilidades (ABO o HLA)
    df_incompatibles = pd.concat(
        [df_incomp_abo, df_incomp_hla]).drop_duplicates()

    # 📈 Calcular porcentaje sobre el total de donantes
    cpra = (len(df_incompatibles) / total_donantes) * 100

    return {"cPRA": round(cpra, 1)}

# 🧭 Servir el frontend (index.html)
from fastapi.responses import FileResponse

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")
