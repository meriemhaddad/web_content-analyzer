# Azure Container Apps Bicep Template

// This Bicep file provisions an Azure Container App for the web content analysis agent.
// It assumes you have pushed your Docker image to Azure Container Registry (ACR).

param location string = resourceGroup().location
param containerAppName string
param environmentName string
param containerRegistryServer string
param containerRegistryUsername string
param containerRegistryPassword string
param containerImage string
param azureOpenAiEndpoint string
param azureOpenAiApiKey string
param azureOpenAiDeploymentName string = 'gpt-4o'
param env string = 'production'

resource containerAppEnv 'Microsoft.App/managedEnvironments@2022-03-01' existing = {
  name: environmentName
}

resource containerApp 'Microsoft.App/containerApps@2022-03-01' = {
  name: containerAppName
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
      registries: [
        {
          server: containerRegistryServer
          username: containerRegistryUsername
          password: containerRegistryPassword
        }
      ]
      secrets: [
        { name: 'azure-openai-api-key', value: azureOpenAiApiKey }
      ]
      environmentVariables: [
        { name: 'AZURE_OPENAI_ENDPOINT', value: azureOpenAiEndpoint },
        { name: 'AZURE_OPENAI_DEPLOYMENT_NAME', value: azureOpenAiDeploymentName },
        { name: 'ENV', value: env },
        { name: 'AZURE_OPENAI_API_KEY', secretRef: 'azure-openai-api-key' }
      ]
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: containerImage
          resources: {
            cpu: 1.0
            memory: '2.0Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}
