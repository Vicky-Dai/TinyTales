#!/bin/bash
# Quick deployment script for Azure
# This script helps automate the Azure deployment process

set -e

echo "🚀 TinyTales Azure Deployment Script"
echo "===================================="
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo "🔐 Please login to Azure..."
    az login
fi

# Get user input
read -p "Enter resource group name (default: tiny-tales-rg): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-tiny-tales-rg}

read -p "Enter location (default: eastus): " LOCATION
LOCATION=${LOCATION:-eastus}

read -p "Enter backend app name (must be globally unique): " BACKEND_APP_NAME
if [ -z "$BACKEND_APP_NAME" ]; then
    BACKEND_APP_NAME="tinytales-backend-$(date +%s)"
    echo "Using generated name: $BACKEND_APP_NAME"
fi

read -p "Enter frontend app name (must be globally unique): " FRONTEND_APP_NAME
if [ -z "$FRONTEND_APP_NAME" ]; then
    FRONTEND_APP_NAME="tinytales-frontend-$(date +%s)"
    echo "Using generated name: $FRONTEND_APP_NAME"
fi

read -p "Enter App Service Plan SKU (F1=Free, B1=Basic ~$13/mo, default: B1): " SKU
SKU=${SKU:-B1}

read -p "Enter your OpenAI API Key: " OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OpenAI API Key is required!"
    exit 1
fi

echo ""
echo "📋 Configuration Summary:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"
echo "   Backend App: $BACKEND_APP_NAME"
echo "   Frontend App: $FRONTEND_APP_NAME"
echo "   App Service Plan: $SKU"
echo ""

read -p "Continue with deployment? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo "🔨 Creating resources..."

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service Plan
echo "Creating App Service Plan..."
az appservice plan create \
  --name tiny-tales-plan \
  --resource-group $RESOURCE_GROUP \
  --sku $SKU \
  --is-linux

# Create Backend App Service
echo "Creating backend App Service..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan tiny-tales-plan \
  --name $BACKEND_APP_NAME \
  --runtime "PYTHON:3.12"

# Create Frontend App Service
echo "Creating frontend App Service..."
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan tiny-tales-plan \
  --name $FRONTEND_APP_NAME \
  --runtime "PYTHON:3.12"

# Configure backend
echo "Configuring backend..."
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP_NAME \
  --settings OPENAI_API_KEY="$OPENAI_API_KEY"

az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $BACKEND_APP_NAME \
  --startup-file "uvicorn main:app --host 0.0.0.0 --port 8000"

# Configure frontend
echo "Configuring frontend..."
BACKEND_URL="https://$BACKEND_APP_NAME.azurewebsites.net"
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP_NAME \
  --settings BACKEND_API_URL="$BACKEND_URL/api/story/generate"

az webapp config set \
  --resource-group $RESOURCE_GROUP \
  --name $FRONTEND_APP_NAME \
  --startup-file "streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true"

# Enable Always On (if not free tier)
if [ "$SKU" != "F1" ]; then
    echo "Enabling Always On..."
    az webapp config set \
      --resource-group $RESOURCE_GROUP \
      --name $BACKEND_APP_NAME \
      --always-on true
    
    az webapp config set \
      --resource-group $RESOURCE_GROUP \
      --name $FRONTEND_APP_NAME \
      --always-on true
fi

echo ""
echo "✅ Resources created successfully!"
echo ""
echo "📝 Next Steps:"
echo "   1. Deploy your code using one of these methods:"
echo "      - Azure Portal: Go to Deployment Center"
echo "      - VS Code: Install Azure App Service extension"
echo "      - Azure CLI: See azure-deployment-guide.md"
echo ""
echo "   2. Backend URL: https://$BACKEND_APP_NAME.azurewebsites.net"
echo "   3. Frontend URL: https://$FRONTEND_APP_NAME.azurewebsites.net"
echo ""
echo "   4. Don't forget to update CORS in backend/main.py with frontend URL!"
echo ""

