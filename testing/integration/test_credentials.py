"""
Direct test of Azure OpenAI credentials to debug the 401 error.
"""

import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

def test_azure_openai_credentials():
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    
    print(f"Testing Azure OpenAI Connection:")
    print(f"Endpoint: {endpoint}")
    print(f"API Key: {'SET' if api_key else 'NOT SET'}")
    
    if not endpoint or not api_key:
        print("[ERROR] Missing credentials!")
        return
    
    # Test endpoint
    url = f"{endpoint}/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-01"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    
    data = {
        "messages": [{"role": "user", "content": "Hello, test message"}],
        "max_tokens": 10
    }
    
    try:
        print("\n[CONNECTING] Testing connection...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("[SUCCESS] Connection successful!")
        else:
            print(f"[ERROR] Connection failed: {response.status_code}")
            
            # Check if it's an endpoint issue
            if "Invalid URL" in response.text or response.status_code == 404:
                print("[INFO] Possible endpoint issue - check your resource name")
            elif response.status_code == 401:
                print("[INFO] Authentication issue - check your API key")
            elif "DeploymentNotFound" in response.text:
                print("[INFO] Deployment issue - check your model deployment name")
                
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")

if __name__ == "__main__":
    test_azure_openai_credentials()