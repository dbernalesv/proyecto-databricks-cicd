variable "subscription_id" {
  description = "UUID de la suscripción Azure. No es un secreto."
  type        = string

  validation {
    condition     = can(regex("^[0-9a-fA-F-]{36}$", var.subscription_id))
    error_message = "subscription_id debe tener formato UUID."
  }
}

variable "location" {
  description = "Región seleccionada después de comprobar disponibilidad y costo."
  type        = string
  default     = "eastus"
}

variable "owner" {
  description = "Alias del responsable para etiquetado de costos."
  type        = string
}

variable "budget_amount" {
  description = "Tope de alerta en la moneda de facturación de la suscripción, no en PEN necesariamente."
  type        = number
  default     = 50

  validation {
    condition     = var.budget_amount > 0
    error_message = "budget_amount debe ser mayor que cero."
  }
}

variable "manage_budget" {
  description = "Si es true, Terraform crea y administra un presupuesto. Se deja false porque el laboratorio ya tiene un presupuesto creado en Azure."
  type        = bool
  default     = false
}

variable "budget_contact_email" {
  description = "Correo que recibirá alertas de costo."
  type        = string
  sensitive   = true

  validation {
    condition     = can(regex("^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$", var.budget_contact_email))
    error_message = "budget_contact_email debe ser un correo válido."
  }
}

variable "budget_start_date" {
  description = "Primer día del mes actual en RFC3339; ajustar antes del primer apply."
  type        = string
  default     = "2026-10-01T00:00:00Z"
}

