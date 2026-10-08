import pandas as pd
from sqlalchemy import create_engine

from src import config as cfg


def get_engine():
    return create_engine(cfg.DB_URL)


def init_db_grammys(csv_path=None):
    """Carga inicial del CSV de Grammys a la BD SQL (esta será la 'base de datos fuente')."""
    cfg.ensure_dirs()
    df = pd.read_csv(csv_path or cfg.GRAMMYS_RAW)
    df.to_sql(cfg.GRAMMYS_TABLE, con=get_engine(), if_exists="replace", index=False)
    print(f"Tabla '{cfg.GRAMMYS_TABLE}' cargada en la BD SQL: {df.shape[0]} filas, {df.shape[1]} columnas.")
