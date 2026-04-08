resource "azurerm_resource_group" "rg_be" {
  name     = "rg-portal-coddfy-backend"
  location = "East US"
}

# Banco de Dados PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "db" {
  name                   = "db-projeto-backend"
  resource_group_name    = azurerm_resource_group.rg_be.name
  location               = azurerm_resource_group.rg_be.location
  version                = "13"
  administrator_login    = "adminuser"
  administrator_password = "SenhaForte123!" # Use variáveis/secrets em prod
  sku_name               = "B_Standard_B1ms"
  storage_mb             = 32768
}

# Plano de Serviço e App Service para o FastAPI
resource "azurerm_service_plan" "asp" {
  name                = "plan-backend"
  resource_group_name = azurerm_resource_group.rg_be.name
  location            = azurerm_resource_group.rg_be.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_linux_web_app" "fastapi_app" {
  name                = "app-fastapi-prod"
  resource_group_name = azurerm_resource_group.rg_be.name
  location            = azurerm_service_plan.asp.location
  service_plan_id     = azurerm_service_plan.asp.id

  site_config {
    application_stack {
      python_version = "3.10"
    }
  }
}