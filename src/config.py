"""Rutas y parámetros globales del pipeline."""
import os
from pathlib import Path

PROJECT_DIR = Path(os.getenv("PROJECT_DIR", os.getcwd())).resolve()
DATA = PROJECT_DIR / "data"
STAGING = DATA / "staging"      # archivos intermedios entre tareas
REPORTS = DATA / "reports"      # reporte de calidad de datos

SPOTIFY_RAW = DATA / "spotify_tracks.csv"
GRAMMYS_RAW = DATA / "grammys_raw.csv"

DB_URL = f"sqlite:///{DATA / 'etl_workshop.db'}"
GRAMMYS_TABLE = "grammys_raw"                 # fuente (base de datos)
FINAL_TABLE = "spotify_grammys_merged"        # destino
FINAL_CSV = DATA / "transformed_dataset.csv"

MAX_INVALID_PCT = 5.0   # si más de 5 % de filas incumplen reglas => la validación FALLA


def ensure_dirs():
    for d in (DATA, STAGING, REPORTS):
        d.mkdir(parents=True, exist_ok=True)
