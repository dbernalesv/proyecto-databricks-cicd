terraform {
  required_version = ">= 1.8, < 2.0"

  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = ">= 1.114, < 2.0"
    }
  }
}

