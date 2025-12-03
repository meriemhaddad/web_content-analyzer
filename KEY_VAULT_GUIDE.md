# Azure Key Vault Integration Guide

This project is designed to use Azure Key Vault for secure management of secrets (API keys, connection strings, etc.).

## Steps to Integrate Azure Key Vault

1. **Create a Key Vault**
   ```bash
   az keyvault create --name <your-keyvault-name> --resource-group <your-resource-group>
   ```

2. **Add Secrets to Key Vault**
   ```bash
   az keyvault secret set --vault-name <your-keyvault-name> --name "AZURE_OPENAI_API_KEY" --value "<your-api-key>"
   ```

3. **Assign Identity to Container App**
   - Enable managed identity for your Azure Container App.
   - Grant the identity access to Key Vault secrets:
     ```bash
     az keyvault set-policy --name <your-keyvault-name> --object-id <container-app-identity-object-id> --secret-permissions get list
     ```

4. **Configure Environment Variables**
   - Set environment variables in your Container App to reference Key Vault secrets using Azure App Service/Container Apps syntax (if supported), or fetch secrets at runtime using DefaultAzureCredential in your code.

5. **Modify Code to Use Managed Identity**
   - The app already supports Azure DefaultAzureCredential. If `USE_MANAGED_IDENTITY=true` is set, the app will use managed identity to access Key Vault and Azure OpenAI.

## References
- [Azure Key Vault Documentation](https://learn.microsoft.com/en-us/azure/key-vault/)
- [Azure Container Apps: Use Key Vault secrets](https://learn.microsoft.com/en-us/azure/container-apps/key-vault-secrets)
