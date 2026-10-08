"""Calidad de datos con Pandera para el dataset de Spotify."""
import pandas as pd

try:
    import pandera.pandas as pa
except ImportError:          # versiones antiguas de pandera
    import pandera as pa

from src import config as cfg


class DataQualityError(Exception):
    """La validación de calidad de datos falló."""


spotify_schema = pa.DataFrameSchema(
    {
        "track_id": pa.Column(str, nullable=False),
        "artists": pa.Column(str, nullable=False),
        "track_name": pa.Column(str, nullable=False),
        "album_name": pa.Column(str, nullable=True),
        "popularity": pa.Column(int, pa.Check.in_range(0, 100)),
        "duration_ms": pa.Column(int, pa.Check.gt(0)),
        "explicit": pa.Column(bool),
        "danceability": pa.Column(float, pa.Check.in_range(0, 1)),
        "energy": pa.Column(float, pa.Check.in_range(0, 1)),
        "loudness": pa.Column(float, pa.Check.in_range(-60, 5)),
        "speechiness": pa.Column(float, pa.Check.in_range(0, 1)),
        "acousticness": pa.Column(float, pa.Check.in_range(0, 1)),
        "valence": pa.Column(float, pa.Check.in_range(0, 1)),
        "tempo": pa.Column(float, pa.Check.ge(0)),
        "track_genre": pa.Column(str, nullable=False),
    },
    coerce=True,
    strict=False,
)


def _summarize(failure_cases: pd.DataFrame):
    g = (failure_cases.groupby(["column", "check"], dropna=False)
         .size().reset_index(name="filas_afectadas")
         .sort_values("filas_afectadas", ascending=False))
    return g.astype(str).to_dict("records")


def validate_spotify_data(df: pd.DataFrame):
    """Devuelve (df_limpio, df_rechazado, reporte).
    Estados: PASSED | PASSED_WITH_WARNINGS | FAILED."""
    report = {"dataset": "spotify", "rows_total": int(len(df))}
    try:
        clean = spotify_schema.validate(df, lazy=True)
        report.update(status="PASSED", rows_invalid=0, invalid_pct=0.0, errors=[])
        return clean, df.iloc[0:0], report
    except pa.errors.SchemaErrors as exc:
        fc = exc.failure_cases
        report["errors"] = _summarize(fc)
        # Sin índice de fila => error estructural (columna faltante / tipo imposible de convertir)
        if fc["index"].isna().any():
            report.update(status="FAILED", rows_invalid=None, invalid_pct=None,
                          reason="Error estructural: columnas faltantes o tipos inválidos")
            return None, None, report
        bad = fc["index"].dropna().unique()
        rejected = df.loc[df.index.isin(bad)]
        pct = round(len(rejected) / len(df) * 100, 4)
        report.update(rows_invalid=int(len(rejected)), invalid_pct=pct)
        if pct > cfg.MAX_INVALID_PCT:
            report.update(status="FAILED",
                          reason=f"{pct}% de filas inválidas supera el umbral de {cfg.MAX_INVALID_PCT}%")
            return None, rejected, report
        clean = spotify_schema.validate(df.drop(index=rejected.index))
        report.update(status="PASSED_WITH_WARNINGS",
                      reason="Filas inválidas separadas en data/reports/rejected_rows.csv")
        return clean, rejected, report
