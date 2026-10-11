output "resource_group_name" {
  description = "Grupo de recursos administrado por este módulo."
  value       = azurerm_resource_group.this.name
}

output "workspace_id" {
  description = "ID Azure Resource Manager del workspace."
  value       = azurerm_databricks_workspace.this.id
}

output "workspace_numeric_id" {
  description = "ID numérico utilizado por APIs de cuenta Databricks."
  value       = azurerm_databricks_workspace.this.workspace_id
}

output "workspace_url" {
  description = "Host público del workspace, sin protocolo."
  value       = azurerm_databricks_workspace.this.workspace_url
}

