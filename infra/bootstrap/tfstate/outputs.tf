output "resource_group_name" {
  description = "Resource Group compartido que contiene el backend."
  value       = azurerm_resource_group.tfstate.name
}

output "storage_account_name" {
  description = "Nombre de la cuenta usada por los archivos .tfbackend locales."
  value       = azurerm_storage_account.tfstate.name
}

output "container_name" {
  description = "Contenedor privado de estados Terraform."
  value       = azurerm_storage_container.tfstate.name
}

output "operator_object_id" {
  description = "Object ID de Entra autorizado para operar blobs de state."
  value       = data.azurerm_client_config.current.object_id
}
