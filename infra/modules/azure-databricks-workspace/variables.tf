variable "project_name" {
  description = "Nombre corto usado en recursos y etiquetas."
  type        = string
}

variable "environment" {
  description = "Entorno SDLC. En esta fase sólo se permite dev."
  type        = string

  validation {
    condition     = var.environment == "dev"
    error_message = "Esta fase del laboratorio sólo permite environment=dev."
  }
}

variable "location" {
  description = "Región Azure validada para la suscripción."
  type        = string
}

variable "owner" {
  description = "Alias del responsable, sin correo ni datos sensibles."
  type        = string
}

variable "workspace_sku" {
  description = "Premium habilita las capacidades de gobierno requeridas."
  type        = string
  default     = "premium"

  validation {
    condition     = contains(["standard", "premium"], lower(var.workspace_sku))
    error_message = "workspace_sku debe ser standard o premium."
  }
}

