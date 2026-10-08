# Workshop 2 – Automatización de un Pipeline ETL con Apache Airflow
**Spotify Tracks (CSV) + Grammy Awards (Base de Datos SQL)**

---

## 📋 Entregables del Repositorio

Este repositorio cumple con todos los requisitos del proyecto:
* **Pipeline de Airflow Organizado:** Código fuente en `src/` y definición de DAG en `dags/` para orquestar la extracción, validación, transformación y carga de datos.
* **Documentación del Proyecto:** Explicación detallada del flujo ETL, reglas de calidad de datos y arquitectura en este archivo `README.md`.
* **Configuración de Reproducibilidad:** Entorno configurado para ejecutar el pipeline de forma autónoma en Google Colab o entorno local (SQLite, scripts modularizados y paquetes requeridos).

---

## 📌 Introducción
Este proyecto implementa un pipeline ETL orquestado mediante **Apache Airflow**. Integra dos fuentes de datos distintas:

1. **Spotify Tracks Dataset**: Datos sobre canciones, métricas de audio y popularidad (fuente CSV).
2. **Grammy Awards Dataset**: Histórico de nominaciones e historial de los premios Grammy desde 1958 (fuente SQL / SQLite).

El flujo procesa ambos conjuntos, valida la calidad de los datos de Spotify con la librería **Pandera**, realiza transformaciones avanzadas por artista, almacena los resultados en una base de datos SQLite y genera entregables finales junto con un reporte estadístico.

---

## 🔄 Flujo del Pipeline (DAG: `spotify_grammys_etl`)


### Descripción de Tareas

| Tarea | Descripción |
|---|---|
| `read_csv` | Lee el dataset de canciones de Spotify desde el archivo CSV raw y lo guarda en staging. |
| `validate_csv` | Evalúa la calidad de datos con Pandera. Genera `validation_report.json` y separa filas inválidas en `rejected_rows.csv`. Si el porcentaje de error supera el 5%, el DAG se detiene (`FAILED`). |
| `transform_csv` | Limpia índices sobrantes, elimina duplicados por `track_id`, calcula la duración en minutos (`duration_min`) y extrae el artista principal (`primary_artist`). |
| `read_db` | Lee la tabla `grammys_raw` cargada en la base de datos SQL (SQLite). |
| `transform_db` | Procesa y normaliza artistas de Grammys. Si la columna `artist` está vacía (~38% de los casos), extrae el artista desde el campo `workers`. Agrupa nominaciones y rango de años por artista. |
| `merge` | Realiza un `LEFT JOIN` conservando todas las canciones de Spotify. Asigna a cada canción la información del artista con mayor cantidad de nominaciones al Grammy. |
| `load` | Guarda el dataset resultante consolidado en la tabla `spotify_grammys_merged` de la base de datos. |
| `store` | Exporta la tabla final desde la base de datos al archivo `data/transformed_dataset.csv`. |

---

## 📂 Estructura del Repositorio

```text
.
├── dags/
│   └── spotify_grammys_dag.py           # Definición del DAG de Airflow
├── data/
│   ├── reports/
│   │   ├── rejected_rows.csv            # Filas que no cumplieron las reglas de calidad
│   │   └── validation_report.json       # Reporte detallado de validación (Pandera)
│   ├── etl_workshop.db                  # Base de datos SQLite
│   ├── grammys_raw.csv                  # Dataset raw de Grammys
│   ├── spotify_tracks.csv               # Dataset raw de Spotify
│   └── transformed_dataset.csv          # Entregable final exportado
├── src/
│   ├── __init__.py
│   ├── config.py                        # Configuración de rutas y parámetros globales
│   ├── database.py                      # Conexión a BD y carga inicial
│   ├── load.py                          # Funciones de carga a BD y exportación a CSV
│   ├── quality.py                       # Definición del schema y validación con Pandera
│   ├── tasks.py                         # Funciones ejecutadas por cada tarea del DAG
│   └── transform.py                     # Lógica de limpieza, normalización y merge
├── README.md                            # Documentación del proyecto
└── Workshop_2_Automatization_of_ETL_pipeline.ipynb  # Notebook principal de ejecución
