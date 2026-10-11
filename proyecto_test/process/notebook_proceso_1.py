# Databricks notebook source
# MAGIC %md
# MAGIC # Proceso de ejemplo
# MAGIC
# MAGIC Este notebook demuestra la ubicación de un proceso versionado. La lógica real se
# MAGIC incorporará mediante Pull Requests y pruebas, sin datos productivos.

# COMMAND ----------

result = spark.sql("SELECT 1 AS example_value").first()
assert result.example_value == 1
