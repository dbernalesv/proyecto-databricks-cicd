locals {
  project_name         = "databricks-cicd"
  resource_group_name  = "rg-${local.project_name}-tfstate"
  storage_account_name = "stdbcicdtf${substr(md5(var.subscription_id), 0, 10)}"
  container_name       = "tfstate"

  tags = {
    project     = local.project_name
    environment = "shared"
    owner       = var.owner
    managed_by  = "terraform"
  }
}

resource "azurerm_resource_group" "tfstate" {
  name     = local.resource_group_name
  location = var.location
  tags     = local.tags
}

resource "azurerm_storage_account" "tfstate" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.tfstate.name
  location                 = azurerm_resource_group.tfstate.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  min_tls_version                 = "TLS1_2"
  public_network_access           = "Enabled"
  shared_access_key_enabled       = false
  default_to_oauth_authentication = true
  allow_nested_items_to_be_public = false

  blob_properties {
    versioning_enabled = true

    delete_retention_policy {
      days = 14
    }

    container_delete_retention_policy {
      days = 14
    }
  }

  tags = local.tags
}

resource "azurerm_storage_container" "tfstate" {
  name                  = local.container_name
  storage_account_id    = azurerm_storage_account.tfstate.id
  container_access_type = "private"
}

resource "azurerm_role_assignment" "terraform_operator" {
  scope                = "${azurerm_storage_account.tfstate.id}/blobServices/default/containers/${azurerm_storage_container.tfstate.name}"
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
  principal_type       = "User"
}
