data "azurerm_subscription" "current" {
  subscription_id = var.subscription_id
}

module "workspace" {
  source = "../../modules/azure-databricks-workspace"

  project_name  = "databricks-cicd"
  environment   = "dev"
  location      = var.location
  owner         = var.owner
  workspace_sku = "premium"
}

resource "azurerm_consumption_budget_subscription" "learning" {
  count           = var.manage_budget ? 1 : 0
  name            = "budget-databricks-cicd-learning"
  subscription_id = data.azurerm_subscription.current.id
  amount          = var.budget_amount
  time_grain      = "Monthly"

  time_period {
    start_date = var.budget_start_date
  }

  dynamic "notification" {
    for_each = toset([50, 75, 90, 100])
    content {
      enabled        = true
      threshold      = notification.value
      operator       = "GreaterThanOrEqualTo"
      threshold_type = "Actual"
      contact_emails = [var.budget_contact_email]
    }
  }
}
