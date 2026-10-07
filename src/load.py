import pandas as pd
import sqlite3

DB_PATH = 'data/etl_workshop.db'

def load_merged_data_to_db():
    df = pd.read_csv('data/tmp_merged.csv')
    conn = sqlite3.connect(DB_PATH)
    df.to_sql('spotify_grammys_merged', conn, if_exists='replace', index=False)
    conn.close()
    print("Datos cargados exitosamente en la BD (tabla: spotify_grammys_merged).")

def store_merged_data_to_csv():
    df = pd.read_csv('data/tmp_merged.csv')
    df.to_csv('data/transformed_dataset.csv', index=False)
    print("Archivo CSV exportado correctamente en: data/transformed_dataset.csv")
