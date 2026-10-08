"""Lógica de cada tarea del DAG (Python/pandas puro, sin dependencia de Airflow)."""
import json

import pandas as pd

from src import config as cfg
from src.database import get_engine
from src.load import export_to_csv, save_to_db
from src.quality import DataQualityError, validate_spotify_data
from src.transform import merge_datasets, transform_grammys, transform_spotify


def read_csv():
    cfg.ensure_dirs()
    df = pd.read_csv(cfg.SPOTIFY_RAW)
    df.to_csv(cfg.STAGING / "spotify_raw.csv", index=False)
    print(f"[read_csv] Spotify leído desde CSV: {df.shape}")


def read_db():
    cfg.ensure_dirs()
    df = pd.read_sql(f"SELECT * FROM {cfg.GRAMMYS_TABLE}", get_engine())
    if df.empty:
        raise DataQualityError("La tabla de Grammys está vacía")
    df.to_csv(cfg.STAGING / "grammys_raw.csv", index=False)
    print(f"[read_db] Grammys leído desde la BD SQL: {df.shape}")


def validate_csv():
    df = pd.read_csv(cfg.STAGING / "spotify_raw.csv")
    clean, rejected, report = validate_spotify_data(df)
    (cfg.REPORTS / "validation_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"[validate_csv] Estado: {report['status']} | filas inválidas: {report['rows_invalid']} "
          f"({report['invalid_pct']}%)")
    if rejected is not None and len(rejected):
        rejected.to_csv(cfg.REPORTS / "rejected_rows.csv", index=False)
    if report["status"] == "FAILED":
        raise DataQualityError(report.get("reason", "Validación fallida"))
    clean.to_csv(cfg.STAGING / "spotify_clean.csv", index=False)


def transform_csv():
    df = transform_spotify(pd.read_csv(cfg.STAGING / "spotify_clean.csv"))
    df.to_csv(cfg.STAGING / "spotify_transformed.csv", index=False)
    print(f"[transform_csv] Spotify transformado: {df.shape}")


def transform_db():
    df = transform_grammys(pd.read_csv(cfg.STAGING / "grammys_raw.csv"))
    df.to_csv(cfg.STAGING / "grammys_transformed.csv", index=False)
    print(f"[transform_db] Grammys agregado por artista: {df.shape}")


def merge():
    sp = pd.read_csv(cfg.STAGING / "spotify_transformed.csv")
    gr = pd.read_csv(cfg.STAGING / "grammys_transformed.csv")
    out = merge_datasets(sp, gr)
    out.to_csv(cfg.STAGING / "merged.csv", index=False)
    print(f"[merge] Dataset final: {out.shape} | canciones con nominación: {int(out['has_grammy_nomination'].sum())}")


def load():
    save_to_db(pd.read_csv(cfg.STAGING / "merged.csv"))


def store():
    df = pd.read_sql(f"SELECT * FROM {cfg.FINAL_TABLE}", get_engine())   # se exporta lo que quedó en la BD
    export_to_csv(df)
