locals {
  project_path         = "/Workspace/data/proyecto_test"
  cicd_path            = "/Workspace/.cicd/proyecto_test/dev"
  schema_name          = "cicd"
  github_oidc_subject  = "repo:${var.github_owner}@${var.github_owner_id}/${var.github_repository}@${var.github_repository_id}:environment:dev"
  github_oidc_audience = "${trimsuffix(var.databricks_host, "/")}/oidc/v1/token"
}

resource "databricks_service_principal" "github_dev" {
  provider     = databricks.account
  display_name = "sp-dbx-cicd-dev"
}

resource "databricks_mws_permission_assignment" "github_dev" {
  provider     = databricks.account
  workspace_id = var.databricks_workspace_id
  principal_id = databricks_service_principal.github_dev.id
  permissions  = ["USER"]
}

# La asignación de cuenta incorpora la identidad al workspace. El data source
# resuelve después su ID SCIM local, requerido por la API de entitlements.
data "databricks_service_principal" "github_dev_workspace" {
  provider       = databricks.workspace
  application_id = databricks_service_principal.github_dev.application_id

  depends_on = [databricks_mws_permission_assignment.github_dev]
}

resource "databricks_entitlements" "github_dev" {
  provider             = databricks.workspace
  service_principal_id = data.databricks_service_principal.github_dev_workspace.sp_id

  # La CLI necesita workspace-access para usar las APIs del workspace. No se
  # conceden capacidades generales de creación de cómputo ni acceso a SQL.
  workspace_access           = true
  databricks_sql_access      = false
  allow_cluster_create       = false
  allow_instance_pool_create = false
}

data "databricks_user" "developer" {
  provider  = databricks.account
  user_name = var.developer_user_name
}

resource "databricks_group" "data_engineers" {
  provider     = databricks.account
  display_name = var.developer_group_name
}

resource "databricks_group_member" "developer" {
  provider  = databricks.account
  group_id  = databricks_group.data_engineers.id
  member_id = data.databricks_user.developer.id
}

resource "databricks_mws_permission_assignment" "data_engineers" {
  provider     = databricks.account
  workspace_id = var.databricks_workspace_id
  principal_id = databricks_group.data_engineers.id
  permissions  = ["USER"]
}

resource "databricks_service_principal_federation_policy" "github_dev" {
  provider             = databricks.account
  service_principal_id = databricks_service_principal.github_dev.id
  policy_id            = "github-environment-dev"
  description          = "GitHub Actions OIDC limitado al environment dev"

  oidc_policy = {
    issuer        = "https://token.actions.githubusercontent.com"
    audiences     = [local.github_oidc_audience]
    subject_claim = "sub"
    subject       = local.github_oidc_subject
  }
}

resource "databricks_directory" "project" {
  provider = databricks.workspace
  path     = local.project_path
}

resource "databricks_directory" "cicd" {
  provider = databricks.workspace
  path     = local.cicd_path
}

resource "databricks_permissions" "project_directory" {
  provider       = databricks.workspace
  directory_path = databricks_directory.project.path

  depends_on = [databricks_mws_permission_assignment.data_engineers]

  access_control {
    service_principal_name = databricks_service_principal.github_dev.application_id
    permission_level       = "CAN_MANAGE"
  }

  # Dev es un entorno de depuración. Los cambios manuales son temporales y el
  # siguiente despliegue restaura el contenido del SHA promovido.
  access_control {
    group_name       = databricks_group.data_engineers.display_name
    permission_level = "CAN_EDIT"
  }
}

resource "databricks_permissions" "cicd_directory" {
  provider       = databricks.workspace
  directory_path = databricks_directory.cicd.path

  access_control {
    service_principal_name = databricks_service_principal.github_dev.application_id
    permission_level       = "CAN_MANAGE"
  }
}

data "databricks_catalog" "workspace" {
  provider = databricks.workspace
  name     = var.workspace_catalog_name
}

resource "databricks_schema" "cicd" {
  provider      = databricks.workspace
  catalog_name  = data.databricks_catalog.workspace.name
  name          = local.schema_name
  comment       = "Esquema de pruebas del pipeline CI/CD."
  force_destroy = false
}

resource "databricks_grant" "github_dev_catalog" {
  provider   = databricks.workspace
  catalog    = data.databricks_catalog.workspace.name
  principal  = databricks_service_principal.github_dev.application_id
  privileges = ["USE_CATALOG"]
}

resource "databricks_grant" "github_dev_schema" {
  provider   = databricks.workspace
  schema     = "${data.databricks_catalog.workspace.name}.${databricks_schema.cicd.name}"
  principal  = databricks_service_principal.github_dev.application_id
  privileges = ["USE_SCHEMA", "CREATE_TABLE", "MODIFY", "SELECT"]
}
