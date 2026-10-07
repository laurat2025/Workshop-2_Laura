# Workshop 2: Automatization of ETL Pipeline with Apache Airflow

Este repositorio contiene la solución para el taller de automatización de un pipeline ETL que extrae, valida, transforma, combina y carga información proveniente de **Spotify** (CSV) y **Grammy Awards** (SQL Database).

---

## 📌 Arquitectura del Pipeline ETL

El flujo de trabajo fue diseñado y orquestado con **Apache Airflow**, ejecutando 7 tareas:

```text
[read_csv -> transform_csv] \
                            --> merge -> load -> store
[read_db  -> transform_db ] /

