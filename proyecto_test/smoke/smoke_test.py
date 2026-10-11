# Databricks notebook source
# MAGIC %md
# MAGIC # Smoke test de CI/CD
# MAGIC
# MAGIC Confirma que OIDC, Bundle, archivos del workspace y cómputo serverless funcionan juntos.

# COMMAND ----------

dbutils.widgets.text("environment", "dev")
dbutils.widgets.text("catalog", "")
dbutils.widgets.text("schema", "")
dbutils.widgets.text("expected_git_sha", "")

environment = dbutils.widgets.get("environment")
catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
expected_git_sha = dbutils.widgets.get("expected_git_sha")

assert environment in {"dev", "qa", "prod"}
assert catalog
assert schema
assert expected_git_sha

result = spark.sql("SELECT 1 AS pipeline_is_healthy").first()
assert result.pipeline_is_healthy == 1
