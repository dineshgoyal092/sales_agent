# Azure OpenAI Setup Guide

This application now uses **Azure OpenAI** with **DefaultAzureCredential** for authentication instead of API keys.

## Prerequisites

1. **Azure OpenAI Service** deployed in your Azure subscription
2. **Azure CLI** installed on your machine
3. Proper **RBAC permissions** for Azure OpenAI

## Authentication Setup

### Option 1: Azure CLI (Recommended)

```bash
# Login to Azure
az login

# Set your subscription (if you have multiple)
az account set --subscription "your-subscription-id"

# Verify your login
az account show
```

### Option 2: Managed Identity

If running on Azure (VM, App Service, Functions), DefaultAzureCredential will automatically use the managed identity.

### Option 3: Environment Variables

Set these environment variables for service principal authentication:
- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_CLIENT_SECRET`

## Configuration

Update the `.env` file with your Azure OpenAI settings:

```env
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-12-01-preview
```

### Configuration Details

- **AZURE_OPENAI_ENDPOINT**: Your Azure OpenAI service endpoint
  - Format: `https://<your-resource-name>.openai.azure.com/`
  
- **AZURE_OPENAI_DEPLOYMENT**: The deployment name of your model
  - Example: `gpt-4`, `gpt-35-turbo`, `gpt-4-32k`
  
- **AZURE_OPENAI_API_VERSION**: The API version to use
  - Latest: `2024-12-01-preview`
  - Stable: `2024-02-15-preview`

## Required Azure Permissions

Your Azure account needs the following role on the Azure OpenAI resource:

- **Cognitive Services OpenAI User** (recommended)
- OR **Cognitive Services OpenAI Contributor**

To assign the role:

```bash
# Get your user principal ID
az ad signed-in-user show --query id -o tsv

# Assign the role
az role assignment create \
  --role "Cognitive Services OpenAI User" \
  --assignee <your-user-id> \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.CognitiveServices/accounts/<openai-resource-name>
```

## Testing the Setup

1. **Verify Azure CLI login:**
   ```bash
   az account show
   ```

2. **Check Azure OpenAI access:**
   ```bash
   az cognitiveservices account show \
     --name <your-openai-resource-name> \
     --resource-group <your-resource-group>
   ```

3. **Run the application:**
   ```bash
   cd src
   streamlit run app.py
   ```

## Troubleshooting

### Error: "DefaultAzureCredential failed to retrieve a token"

**Solutions:**
1. Run `az login` and authenticate
2. Verify your Azure subscription: `az account list`
3. Check RBAC permissions on the Azure OpenAI resource

### Error: "The requested model does not exist"

**Solution:**
- Verify the deployment name in `.env` matches your Azure OpenAI deployment
- List your deployments:
  ```bash
  az cognitiveservices account deployment list \
    --name <your-openai-resource-name> \
    --resource-group <your-resource-group>
  ```

### Error: "Access denied"

**Solution:**
- Ensure you have the "Cognitive Services OpenAI User" role
- Wait a few minutes after role assignment for permissions to propagate

## Authentication Fallback Order

DefaultAzureCredential attempts authentication in this order:

1. **Environment Variables** - Service principal credentials
2. **Managed Identity** - If running on Azure
3. **Azure CLI** - If `az login` was executed
4. **Azure PowerShell** - If logged in via PowerShell
5. **Interactive Browser** - Last resort, opens browser for login

## Security Best Practices

✅ **DO:**
- Use Azure CLI or Managed Identity for local development
- Use Managed Identity for production deployments
- Regularly rotate service principal secrets (if used)

❌ **DON'T:**
- Commit `.env` files with sensitive credentials
- Share service principal secrets in plain text
- Use API keys when Azure authentication is available

## Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [DefaultAzureCredential Overview](https://learn.microsoft.com/python/api/azure-identity/azure.identity.defaultazurecredential)
- [Azure RBAC Documentation](https://learn.microsoft.com/azure/role-based-access-control/)
