# Databricks notebook source
# MAGIC %md
# MAGIC # DDL de ejemplo
# MAGIC
# MAGIC La creación real de tablas se añadirá cuando exista un catálogo Dev aprovisionado.

# COMMAND ----------

# No ejecuta DDL destructivo durante el laboratorio inicial.
ddl_preview = "CREATE TABLE IF NOT EXISTS <catalog>.<schema>.tabla1 (id BIGINT)"
assert "IF NOT EXISTS" in ddl_preview
