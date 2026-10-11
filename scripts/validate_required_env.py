"""Falla de forma segura si el job carece de configuración no sensible."""

import os

from databricks_cicd.config import DeploymentConfig

if __name__ == "__main__":
    DeploymentConfig.from_mapping(os.environ)
    print("Configuración requerida validada; no se imprimieron valores.")
