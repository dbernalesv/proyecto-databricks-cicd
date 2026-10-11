"""Contrato mínimo de configuración compartido por todos los entornos."""

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class EnvironmentConfig:
    """Configuración no sensible requerida por una ejecución de datos."""

    environment: str
    catalog: str
    schema: str

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> "EnvironmentConfig":
        """Construye y valida la configuración a partir de variables externas."""
        required = ("APP_ENV", "DATABRICKS_CATALOG", "DATABRICKS_SCHEMA")
        missing = [name for name in required if not values.get(name, "").strip()]
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Faltan variables requeridas: {names}")

        environment = values["APP_ENV"].strip().lower()
        if environment not in {"dev", "qa", "prod"}:
            raise ValueError("APP_ENV debe ser dev, qa o prod")

        return cls(
            environment=environment,
            catalog=values["DATABRICKS_CATALOG"].strip(),
            schema=values["DATABRICKS_SCHEMA"].strip(),
        )


@dataclass(frozen=True)
class DeploymentConfig:
    """Configuración requerida antes de solicitar una credencial OIDC."""

    environment: EnvironmentConfig
    host: str
    client_id: str
    workspace_root: str

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> "DeploymentConfig":
        """Valida entradas cloud sin imprimirlas ni aceptar rutas amplias."""
        from databricks_cicd.workspace_manifest import assert_safe_workspace_root

        required = ("DATABRICKS_HOST", "DATABRICKS_CLIENT_ID", "DATABRICKS_WORKSPACE_ROOT")
        missing = [name for name in required if not values.get(name, "").strip()]
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"Faltan variables requeridas: {names}")

        host = values["DATABRICKS_HOST"].strip()
        if not host.startswith("https://"):
            raise ValueError("DATABRICKS_HOST debe usar HTTPS")

        return cls(
            environment=EnvironmentConfig.from_mapping(values),
            host=host,
            client_id=values["DATABRICKS_CLIENT_ID"].strip(),
            workspace_root=assert_safe_workspace_root(values["DATABRICKS_WORKSPACE_ROOT"].strip()),
        )
