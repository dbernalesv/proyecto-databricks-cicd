variable "subscription_id" {
  description = "UUID de la suscripción Azure donde se almacenará el state. No es un secreto."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-fA-F-]{36}$", var.subscription_id))
    error_message = "subscription_id debe tener formato UUID."
  }
}

variable "location" {
  description = "Región del Resource Group y de la cuenta de almacenamiento."
  type        = string
  default     = "eastus2"
}

variable "owner" {
  description = "Alias del responsable para etiquetado de costos."
  type        = string

  validation {
    condition     = length(trimspace(var.owner)) > 0
    error_message = "owner no puede estar vacío."
  }
}

variable "additional_state_operator_object_ids" {
  description = "Object IDs de Entra adicionales autorizados a operar el contenedor de state. No son secretos."
  type        = set(string)
  default     = []

  validation {
    condition = alltrue([
      for object_id in var.additional_state_operator_object_ids :
      can(regex("^[0-9a-fA-F-]{36}$", object_id))
    ])
    error_message = "Cada Object ID adicional debe tener formato UUID."
  }
}
