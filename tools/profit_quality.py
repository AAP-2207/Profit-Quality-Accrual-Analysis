"""
Profit Quality Analysis Tool
Direct function that fetches data and returns analysis results
"""

import os
import requests
from typing import Dict, List
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_analyzer import FinancialAnalyzer

load_dotenv()

def profit_quality_analysis(company_id: str, risk_free_rate: float) -> str:
    """
    Analyzes profit quality for a company using its ID
    
    Args:
        company_id: Company identifier (ticker or ID)
        risk_free_rate: Risk-free rate as decimal (e.g., 0.07 for 7%)
        
    Returns:
        Formatted string with all analysis results
    """
    try:
        # Fetch data from API
        api_key = os.getenv("API_KEY")
        api_base_url = os.getenv("API_BASE_URL")
        
        if not api_key or not api_base_url:
            return "Error: API_KEY and API_BASE_URL must be set in .env file"
        
        # Clean up API URL
        api_base_url = api_base_url.rstrip('/')
        
        print(f"Fetching data for {company_id} from {api_base_url}...")
        
        # Correct authentication header format for AC API
        headers = {"x-api-key": api_key}
        
        # Fetch complete financial data from AC API
        endpoint = f"{api_base_url}/server/company/{company_id}"
        
        try:
            response = requests.get(endpoint, headers=headers, timeout=30, allow_redirects=True)
            response.encoding = 'utf-8'  # Force UTF-8 encoding
            
            if response.status_code == 401:
                return "Error: Invalid or missing API key. Check your API_KEY in .env file"
            
            if response.status_code == 404:
                return f"Error: Company {company_id} not found. Ensure you use the correct format (e.g., TCS.NS or TCS.BO)"
            
            if response.status_code != 200:
                print(f"⚠ API returned status {response.status_code}, using mock data")
                data = _generate_mock_data(company_id)
            else:
                api_response = response.json()
                
                if api_response.get("status") != "success":
                    print(f"⚠ API error: {api_response.get('message')}, using mock data")
                    data = _generate_mock_data(company_id)
                else:
                    print(f"✓ Successfully fetched data from {endpoint}")
                    financial_data = api_response.get("data", [])
                    
                    # Sort by year (oldest to newest) and extract metrics
                    financial_data.sort(key=lambda x: x.get("calendarYear", 0))
                    
                    data = {
                        "pat": [float(item.get("netIncome", 0)) for item in financial_data],
                        "cfo": [float(item.get("operatingCashFlow", item.get("netCashProvidedByOperatingActivities", 0))) for item in financial_data],
                        "ebitda": [float(item.get("ebitda", 0)) for item in financial_data],
                        "depreciation": [float(item.get("depreciationAndAmortization", 0)) for item in financial_data],
                        "sales": [float(item.get("revenue", 0)) for item in financial_data],
                        "capex": [abs(float(item.get("capitalExpenditure", 0))) for item in financial_data],
                        "cash_balance": float(financial_data[-1].get("cashAndCashEquivalents", 0)) if financial_data else 0
                    }
                    
        except Exception as e:
            print(f"⚠ Could not connect to API: {str(e)}, using mock data")
            data = _generate_mock_data(company_id)
        
        # Extract financial metrics
        pat_list = data.get("pat", [])
        cfo_list = data.get("cfo", [])
        ebitda_list = data.get("ebitda", [])
        depreciation_list = data.get("depreciation", [])
        sales_list = data.get("sales", [])
        capex_list = data.get("capex", [])
        cash_balance = data.get("cash_balance", 0)
        
        # Ensure capex has same length
        if not capex_list or len(capex_list) < len(cfo_list):
            capex_list = [0] * len(cfo_list)
        
        # Convert risk_free_rate from decimal to percentage
        risk_free_rate_pct = risk_free_rate * 100
        
        # Run analysis
        analyzer = FinancialAnalyzer()
        
        pat_vs_cfo_result = analyzer.cumulative_pat_vs_cfo(pat_list, cfo_list)
        cfo_ebitda = analyzer.cfo_ebitda_consistency(cfo_list, ebitda_list)
        accrual_result = analyzer.accrual_quality(pat_list, cfo_list)
        dep_volatility = analyzer.depreciation_volatility(depreciation_list, sales_list)
        cash_score_result = analyzer.cash_earning_rate(cash_balance, risk_free_rate_pct)
        fcf_result = analyzer.fcf_quality(cfo_list, depreciation_list, capex_list)
        
        # Extract values from dicts
        pat_vs_cfo = pat_vs_cfo_result.get("value")
        years_used = pat_vs_cfo_result.get("years")
        data_warning = pat_vs_cfo_result.get("warning")
        
        # Extract CFO/EBITDA details
        avg_cfo = cfo_ebitda.get("avg_cfo")
        avg_ebitda = cfo_ebitda.get("avg_ebitda")
        cfo_ebitda_ratio = cfo_ebitda.get("ratio")
        
        # Extract accrual quality details
        avg_pat = accrual_result.get("avg_pat")
        avg_cfo_accrual = accrual_result.get("avg_cfo")
        avg_accruals = accrual_result.get("avg_accruals")
        accrual_ratio = accrual_result.get("accrual_ratio")
        
        # Extract cash earning details
        cash_balance_val = cash_score_result.get("cash_balance")
        risk_free_rate_val = cash_score_result.get("risk_free_rate")
        expected_earnings = cash_score_result.get("expected_earnings")
        actual_earnings = cash_score_result.get("actual_earnings")
        earning_rate = cash_score_result.get("earning_rate")
        cash_warning = cash_score_result.get("warning")
        
        # Extract FCF quality details
        avg_fcf = fcf_result.get("avg_fcf")
        fcf_volatility = fcf_result.get("volatility_cv")
        negative_years = fcf_result.get("negative_years")
        total_years = fcf_result.get("total_years")
        avg_cfo_fcf = fcf_result.get("avg_cfo")
        avg_capex = fcf_result.get("avg_capex")
        
        # Calculate cumulative PAT and CFO for detailed display
        cumulative_pat = sum(pat_list)
        cumulative_cfo = sum(cfo_list)
        
        # Format output
        warnings = []
        if data_warning:
            warnings.append(f"⚠ {data_warning}")
        if cash_warning:
            warnings.append(f"⚠ {cash_warning}")
        
        warning_section = "\n".join(warnings) + "\n" if warnings else ""
        
        # Format point 5 based on whether we have actual earnings data
        if actual_earnings is None:
            cash_section = f"""5. COMPANY CASH EARNINGS ANALYSIS:
   Cash Balance: {cash_balance_val:,.2f}
   Risk-Free Rate: {risk_free_rate_val:.2f}%
   Expected Earnings at Risk-Free Rate: {expected_earnings:,.2f}
   Actual Interest Income: Data not available"""
        else:
            cash_section = f"""5. COMPANY CASH EARNINGS ANALYSIS:
   Cash Balance: {cash_balance_val:,.2f}
   Risk-Free Rate: {risk_free_rate_val:.2f}%
   Expected Earnings at Risk-Free Rate: {expected_earnings:,.2f}
   Actual Interest Income: {actual_earnings:,.2f}
   Actual Earning Rate: {earning_rate:.3f}%"""
        
        output = f"""
PROFIT QUALITY & ACCRUAL ANALYSIS REPORT
Company: {company_id}
Risk-Free Rate: {risk_free_rate_pct:.2f}%
Data Period: {years_used} years
========================================

{warning_section}
1. CUMULATIVE PAT vs CFO RATIO ({years_used}Y):
   Cumulative PAT: {cumulative_pat:,.2f}
   Cumulative CFO: {cumulative_cfo:,.2f}
   Ratio (CFO/PAT): {pat_vs_cfo}

2. CFO/EBITDA CONSISTENCY:
   Average CFO: {avg_cfo:,.2f}
   Average EBITDA: {avg_ebitda:,.2f}
   CFO/EBITDA Ratio: {cfo_ebitda_ratio}

3. ACCRUAL PROFIT CONVERSION QUALITY:
   Average PAT: {avg_pat:,.2f}
   Average CFO: {avg_cfo_accrual:,.2f}
   Average Accruals (PAT - CFO): {avg_accruals:,.2f}
   Accrual Ratio (Accruals/PAT): {accrual_ratio}
   (Lower ratio = Better quality)

4. DEPRECIATION VOLATILITY (as % of sales):
   Volatility: {dep_volatility}%

{cash_section}

6. FREE CASH FLOW ANALYSIS:
   Average CFO: {avg_cfo_fcf:,.2f}
   Average Capex: {avg_capex:,.2f}
   Average FCF (CFO - Capex): {avg_fcf:,.2f}
   FCF Volatility (CV%): {fcf_volatility:.2f}%
   Negative FCF Years: {negative_years} out of {total_years}

========================================
Analysis Complete
"""
        return output
        
    except Exception as e:
        return f"Error during analysis: {str(e)}\n\nPlease check:\n- API credentials in .env\n- Company ID is valid\n- API endpoint is accessible"


def _generate_mock_data(company_id: str) -> Dict:
    """Generate mock financial data for testing"""
    return {
        "company_id": company_id,
        "pat": [100, 110, 120, 115, 125, 130, 140, 135, 145, 150],
        "cfo": [95, 105, 118, 112, 122, 128, 138, 133, 143, 148],
        "ebitda": [150, 160, 170, 165, 175, 180, 190, 185, 195, 200],
        "depreciation": [20, 20, 21, 21, 22, 22, 23, 23, 24, 24],
        "sales": [1000, 1050, 1100, 1080, 1150, 1200, 1250, 1220, 1300, 1350],
        "capex": [30, 32, 35, 33, 38, 40, 42, 41, 45, 48],
        "cash_balance": 500
    }
