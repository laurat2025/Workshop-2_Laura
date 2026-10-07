import pandera as pa
import pandas as pd

spotify_schema = pa.DataFrameSchema({
    "track_id": pa.Column(pa.String, nullable=True),
    "artists": pa.Column(pa.String, nullable=True),
    "album_name": pa.Column(pa.String, nullable=True),
    "track_name": pa.Column(pa.String, nullable=True),
    "popularity": pa.Column(pa.Int, pa.Check.in_range(0, 100), nullable=True, coerce=True),
    "duration_ms": pa.Column(pa.Int, pa.Check.greater_than(0), nullable=True, coerce=True)
})

def validate_spotify_data(df):
    df_clean = df.dropna(subset=['artists', 'track_name']).copy()
    df_clean['popularity'] = pd.to_numeric(df_clean['popularity'], errors='coerce').fillna(0).astype(int)
    df_clean['duration_ms'] = pd.to_numeric(df_clean['duration_ms'], errors='coerce').fillna(0).astype(int)
    
    try:
        validated_df = spotify_schema.validate(df_clean)
        print(" Validaciones de calidad de Pandera superadas correctamente.")
        return validated_df
    except pa.errors.SchemaError as e:
        print(f" Error en la validación de calidad: {e}")
        raise e

def extract_and_validate_spotify():
    df = pd.read_csv('data/spotify_tracks.csv')
    return validate_spotify_data(df)
