import pytest

from databricks_cicd.config import DeploymentConfig, EnvironmentConfig


def test_builds_valid_environment_config() -> None:
    config = EnvironmentConfig.from_mapping(
        {
            "APP_ENV": "Dev",
            "DATABRICKS_CATALOG": "proyecto_dev",
            "DATABRICKS_SCHEMA": "cicd",
        }
    )

    assert config == EnvironmentConfig("dev", "proyecto_dev", "cicd")


def test_rejects_missing_configuration() -> None:
    with pytest.raises(ValueError, match="DATABRICKS_SCHEMA"):
        EnvironmentConfig.from_mapping(
            {
                "APP_ENV": "dev",
                "DATABRICKS_CATALOG": "proyecto_dev",
            }
        )


def test_rejects_unknown_environment() -> None:
    with pytest.raises(ValueError, match="dev, qa o prod"):
        EnvironmentConfig.from_mapping(
            {
                "APP_ENV": "sandbox",
                "DATABRICKS_CATALOG": "proyecto_dev",
                "DATABRICKS_SCHEMA": "cicd",
            }
        )


def test_builds_safe_deployment_config() -> None:
    config = DeploymentConfig.from_mapping(
        {
            "APP_ENV": "dev",
            "DATABRICKS_CATALOG": "proyecto_dev",
            "DATABRICKS_SCHEMA": "cicd",
            "DATABRICKS_HOST": "https://adb-example.azuredatabricks.net",
            "DATABRICKS_CLIENT_ID": "example-client-id",
            "DATABRICKS_WORKSPACE_ROOT": "/Workspace/data/proyecto_test",
        }
    )

    assert config.workspace_root == "/Workspace/data/proyecto_test"


def test_rejects_broad_deployment_root() -> None:
    with pytest.raises(ValueError, match="ruta debe ser exactamente"):
        DeploymentConfig.from_mapping(
            {
                "APP_ENV": "dev",
                "DATABRICKS_CATALOG": "proyecto_dev",
                "DATABRICKS_SCHEMA": "cicd",
                "DATABRICKS_HOST": "https://adb-example.azuredatabricks.net",
                "DATABRICKS_CLIENT_ID": "example-client-id",
                "DATABRICKS_WORKSPACE_ROOT": "/Workspace/data",
            }
        )
