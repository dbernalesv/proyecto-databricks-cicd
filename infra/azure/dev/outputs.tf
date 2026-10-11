output "databricks_host" {
  description = "Valor para la variable DATABRICKS_HOST del environment dev."
  value       = "https://${module.workspace.workspace_url}"
}

output "azure_workspace_resource_id" {
  description = "ID ARM del workspace."
  value       = module.workspace.workspace_id
}

output "databricks_workspace_id" {
  description = "ID numérico del workspace para la capa de configuración Databricks."
  value       = module.workspace.workspace_numeric_id
}

output "resource_group_name" {
  value = module.workspace.resource_group_name
}

