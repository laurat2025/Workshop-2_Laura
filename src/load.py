from src import config as cfg
from src.database import get_engine


def save_to_db(df, table_name=None):
    table_name = table_name or cfg.FINAL_TABLE
    df.to_sql(table_name, con=get_engine(), if_exists="replace", index=False, chunksize=5000)
    print(f"{len(df)} filas cargadas en la BD (tabla: {table_name}).")


def export_to_csv(df, output_path=None):
    output_path = output_path or cfg.FINAL_CSV
    df.to_csv(output_path, index=False)
    print(f"CSV exportado en: {output_path}")
