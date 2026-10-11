output "databricks_client_id" {
  description = "Application ID no sensible para DATABRICKS_CLIENT_ID en GitHub dev."
  value       = databricks_service_principal.github_dev.application_id
}

output "databricks_workspace_project_path" {
  description = "Carpeta normal administrada por el Bundle y reconciliada por CI/CD."
  value       = databricks_directory.project.path
}

output "databricks_bundle_state_path" {
  description = "Ruta protegida para estado y artefactos internos del Bundle Dev."
  value       = databricks_directory.cicd.path
}

output "databricks_catalog" {
  description = "Catálogo administrado del workspace respaldado por Default Storage."
  value       = data.databricks_catalog.workspace.name
}

output "databricks_schema" {
  value = databricks_schema.cicd.name
}

output "databricks_developer_group" {
  description = "Grupo de cuenta asignado al workspace Dev con permisos temporales de edición."
  value       = databricks_group.data_engineers.display_name
}
