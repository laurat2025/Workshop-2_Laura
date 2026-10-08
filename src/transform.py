import re
import unicodedata

import pandas as pd

_SPLIT = re.compile(r"\s+(?:featuring|feat\.?|with|and|&)\s+|,|;|/", flags=re.I)

# Nombres genéricos que NO identifican a un artista (evitan cruces falsos entre datasets)
GENERIC_KEYS = {"various artists", "various", "conductor", "soloist", "soloists", "orchestra", "chorus",
                "original broadway cast", "original cast", "cast", "soundtrack", "original soundtrack",
                "composer", "producer", "unknown", "anonymous"}


def normalize_name(value) -> str:
    """'Beyoncé ' -> 'beyonce'. Llave común para cruzar Spotify con Grammys."""
    if not isinstance(value, str):
        return ""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-z0-9 ]", " ", value.lower())
    return re.sub(r"\s+", " ", value).strip()


def grammy_artist_keys(artist, workers) -> set:
    """Llaves de artista de una fila de Grammys.
    - Si `artist` viene vacío, se recupera de `workers` (texto entre paréntesis: '..., songwriters (Lady Gaga)').
    - 'A Featuring B' / 'A & B' genera la llave completa y una llave por cada artista."""
    if isinstance(artist, str) and artist.strip():
        sources = [artist]
    elif isinstance(workers, str):
        sources = re.findall(r"\(([^()]+)\)", workers)
    else:
        sources = []
    keys = set()
    for src in sources:
        keys.add(normalize_name(src))
        keys.update(normalize_name(p) for p in _SPLIT.split(src))
    return {k for k in keys if len(k) >= 2 and k not in GENERIC_KEYS and not k.isdigit()}


def transform_spotify(df: pd.DataFrame) -> pd.DataFrame:
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")].copy()      # quita índice sobrante
    df = df.drop_duplicates(subset="track_id")                         # un track puede repetirse por género
    df["duration_min"] = (df["duration_ms"] / 60000).round(2)
    df["primary_artist"] = df["artists"].astype(str).str.split(";").str[0].str.strip()
    return df


def transform_grammys(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega los Grammys por artista: nominaciones y rango de años.
    NOTA: en este dataset la columna `winner` es True en todas las filas, por lo que NO se usa
    (cada fila es una nominación/entrada de categoría)."""
    df = df.copy()
    df["artist_clean"] = [grammy_artist_keys(a, w) for a, w in zip(df.get("artist"), df.get("workers"))]
    df = df[df["artist_clean"].map(len) > 0].explode("artist_clean")
    return (df.groupby("artist_clean", as_index=False)
              .agg(grammy_nominations=("category", "size"),
                   grammy_first_year=("year", "min"),
                   grammy_last_year=("year", "max")))


def merge_datasets(df_spotify: pd.DataFrame, df_grammys: pd.DataFrame) -> pd.DataFrame:
    """LEFT JOIN: se conservan TODAS las canciones, 1 fila por track.
    Cada artista de la canción ('A;B') se cruza por separado; la canción hereda los datos del
    artista MÁS nominado entre sus artistas (columna `grammy_artist`)."""
    ex = df_spotify[["track_id", "artists"]].copy()
    ex["artist_raw"] = ex["artists"].astype(str).str.split(";")
    ex = ex.explode("artist_raw")
    ex["artist_clean"] = ex["artist_raw"].map(normalize_name)

    joined = ex.merge(df_grammys, on="artist_clean", how="left")
    n_matched = (joined.groupby("track_id")["grammy_nominations"].apply(lambda s: int(s.notna().sum()))
                 .rename("grammy_artists").reset_index())
    best = (joined.sort_values("grammy_nominations", ascending=False, na_position="last")
                  .drop_duplicates("track_id")
                  [["track_id", "artist_raw", "grammy_nominations", "grammy_first_year", "grammy_last_year"]]
                  .rename(columns={"artist_raw": "grammy_artist"}))
    best.loc[best["grammy_nominations"].isna(), "grammy_artist"] = None

    out = df_spotify.merge(best, on="track_id", how="left").merge(n_matched, on="track_id", how="left")
    out["grammy_nominations"] = out["grammy_nominations"].fillna(0).astype(int)
    out["has_grammy_nomination"] = out["grammy_nominations"] > 0
    return out
