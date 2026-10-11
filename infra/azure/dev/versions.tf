terraform {
  required_version = ">= 1.8, < 2.0"

  backend "azurerm" {}

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 4.0, < 6.0"
    }
  }
}

