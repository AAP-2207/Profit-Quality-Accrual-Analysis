import os
import requests
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class DataFetcher:
    """Handles API calls to fetch financial data"""
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.api_base_url = os.getenv("API_BASE_URL")
        
        if not self.api_key or not self.api_base_url:
            raise ValueError("API_KEY and API_BASE_URL must be set in .env file")
    
    def fetch_financial_data(self, ticker: str, years: int = 10) -> Dict[str, Any]:
        """
        Fetch financial data from API
        
        Args:
            ticker: Stock ticker symbol
            years: Number of historical years to fetch
            
        Returns:
            Dictionary containing financial metrics
        """
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            params = {
                "ticker": ticker,
                "years": years,
                "metrics": ["PAT", "CFO", "EBITDA", "Depreciation", "Sales", "Cash"]
            }
            
            response = requests.get(
                f"{self.api_base_url}/financial-data",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching data from API: {str(e)}")
    
    def fetch_risk_free_rate(self) -> float:
        """Fetch current risk-free rate"""
        try:
            response = requests.get(
                f"{self.api_base_url}/risk-free-rate",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data.get("rate", 4.5)  # Default fallback
        
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not fetch risk-free rate: {str(e)}")
            return 4.5  # Default risk-free rate
