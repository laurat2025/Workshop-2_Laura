import pandas as pd
from src.quality import extract_and_validate_spotify
from src.database import read_grammys_from_db

def transform_spotify_data():
    df = extract_and_validate_spotify()
    df['artist_clean'] = df['artists'].astype(str).str.lower().str.strip()
    df['track_clean'] = df['track_name'].astype(str).str.lower().str.strip()
    df.to_csv('data/tmp_spotify_transformed.csv', index=False)
    return df

def transform_grammys_data():
    df = read_grammys_from_db()
    df['artist_clean'] = df['artist'].astype(str).str.lower().str.strip()
    df['track_clean'] = df['nominee'].astype(str).str.lower().str.strip()
    df.to_csv('data/tmp_grammys_transformed.csv', index=False)
    return df

def merge_spotify_and_grammys():
    df_sp = pd.read_csv('data/tmp_spotify_transformed.csv')
    df_gr = pd.read_csv('data/tmp_grammys_transformed.csv')
    
    merged_df = pd.merge(df_sp, df_gr, on=['artist_clean'], how='inner')
    merged_df.to_csv('data/tmp_merged.csv', index=False)
    return merged_df
