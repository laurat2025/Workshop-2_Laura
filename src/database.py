import sqlite3
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = 'data/etl_workshop.db'

def get_engine():
    return create_engine(f'sqlite:///{DB_PATH}')

def init_db_grammys():
    """Carga inicial del CSV de Grammys a la BD SQLite para simular la fuente SQL"""
    conn = sqlite3.connect(DB_PATH)
    try:
        df_grammys = pd.read_csv('data/grammys_raw.csv')
        df_grammys.to_sql('grammys_raw', conn, if_exists='replace', index=False)
    except Exception as e:
        print(f"Error inicializando BD de Grammys: {e}")
    finally:
        conn.close()

def read_grammys_from_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM grammys_raw", conn)
    conn.close()
    return df
