locals {
  normalized_project = lower(replace(var.project_name, "_", "-"))
  resource_suffix    = "${local.normalized_project}-${var.environment}"
  common_tags = {
    project     = local.normalized_project
    environment = var.environment
    owner       = var.owner
    managed_by  = "terraform"
  }
}

resource "azurerm_resource_group" "this" {
  name     = "rg-${local.resource_suffix}"
  location = var.location
  tags     = local.common_tags
}

resource "azurerm_databricks_workspace" "this" {
  name                        = "dbw-${local.resource_suffix}"
  resource_group_name         = azurerm_resource_group.this.name
  location                    = azurerm_resource_group.this.location
  sku                         = lower(var.workspace_sku)
  managed_resource_group_name = "rg-${local.resource_suffix}-managed"
  tags                        = local.common_tags
}

