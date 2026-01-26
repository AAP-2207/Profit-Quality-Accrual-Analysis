"""
Quick test script for AC API
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
api_base_url = os.getenv("API_BASE_URL")

headers = {"x-api-key": api_key}
endpoint = f"{api_base_url}/server/company/TCS.NS"

print(f"Testing: {endpoint}")

try:
    response = requests.get(endpoint, headers=headers, timeout=30)
    response.encoding = 'utf-8'
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"API Status: {data.get('status')}")
        financial_data = data.get("data", [])
        print(f"Years available: {len(financial_data)}")
        
        for item in financial_data:
            print(f"Year {item.get('calendarYear')}: Revenue={item.get('revenue')}, NetIncome={item.get('netIncome')}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
