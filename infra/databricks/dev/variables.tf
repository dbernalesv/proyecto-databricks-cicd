variable "databricks_account_id" {
  description = "Account ID mostrado en la consola de cuenta Databricks."
  type        = string
}

variable "databricks_workspace_id" {
  description = "ID numérico exportado por infra/azure/dev."
  type        = number
}

variable "databricks_host" {
  description = "URL HTTPS exportada por infra/azure/dev."
  type        = string
}

variable "workspace_catalog_name" {
  description = "Catálogo administrado creado automáticamente para el workspace y respaldado por Default Storage."
  type        = string

  validation {
    condition     = length(trimspace(var.workspace_catalog_name)) > 0
    error_message = "workspace_catalog_name no puede estar vacío."
  }
}

variable "github_owner" {
  description = "Usuario u organización propietaria del repositorio público."
  type        = string
}

variable "github_owner_id" {
  description = "ID numérico inmutable del usuario u organización propietaria en GitHub."
  type        = string

  validation {
    condition     = can(regex("^[0-9]+$", var.github_owner_id))
    error_message = "github_owner_id debe contener únicamente dígitos."
  }
}

variable "github_repository" {
  description = "Nombre del repositorio GitHub."
  type        = string
}

variable "github_repository_id" {
  description = "ID numérico inmutable del repositorio en GitHub."
  type        = string

  validation {
    condition     = can(regex("^[0-9]+$", var.github_repository_id))
    error_message = "github_repository_id debe contener únicamente dígitos."
  }
}

variable "developer_group_name" {
  description = "Grupo de Databricks autorizado para editar temporalmente el proyecto en Dev."
  type        = string

  validation {
    condition     = length(trimspace(var.developer_group_name)) > 0
    error_message = "developer_group_name no puede estar vacío."
  }
}

variable "developer_user_name" {
  description = "Usuario de Databricks que se incorpora al grupo de desarrollo del laboratorio."
  type        = string

  validation {
    condition     = can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.developer_user_name))
    error_message = "developer_user_name debe tener formato de correo válido."
  }
}
