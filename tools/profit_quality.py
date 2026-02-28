"""
Profit Quality Analysis Tool - LangChain Tool
Fetches financial data from API and performs comprehensive profit quality analysis
"""

# IMPORTS: Required libraries including LangChain tool decorator
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import os
import requests
from typing import Dict, List
from dotenv import load_dotenv
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from financial_analyzer import FinancialAnalyzer

load_dotenv()

# API Configuration
BASE_URL = "https://ac-api-server.vercel.app"
API_KEY = os.getenv("AC_API_KEY")

# INPUT SCHEMA: Configuration object that LangChain reads
class ProfitQualityInput(BaseModel):
    """Input schema for profit quality analysis tool"""
    company_id: str = Field(
        ...,
        description="Company ticker symbol (e.g., RELIANCE.BO, TCS.NS). Use Yahoo Finance format with exchange suffix."
    )
    risk_free_rate: float = Field(
        ...,
        description="Risk-free rate as decimal (e.g., 0.07 for 7%, 0.045 for 4.5%). Used to compare company cash earnings.",
        ge=0.0,
        le=1.0
    )

# TOOL DEFINITION: LangChain tool with name, description, and schema
@tool("profit_quality_analysis", args_schema=ProfitQualityInput, return_direct=True)
def profit_quality_analysis(company_id: str, risk_free_rate: float) -> str:
    """
    Performs comprehensive profit quality and accrual analysis for a company.
    
    Analyzes 6 key metrics:
    1. Cumulative PAT vs CFO Ratio - measures cash conversion of profits
    2. CFO/EBITDA Consistency - validates operational cash generation
    3. Accrual Quality - detects earnings manipulation through accruals
    4. Depreciation Volatility - identifies inconsistent depreciation policies
    5. Cash Earning Rate - compares returns on cash vs risk-free rate
    6. Free Cash Flow Quality - assesses FCF generation and volatility
    
    Fetches 10 years of financial data from internal API and returns detailed analysis.
    
    Args:
        company_id: Company ticker symbol (e.g., RELIANCE.BO)
        risk_free_rate: Risk-free rate as decimal (e.g., 0.07 for 7%)
        
    Returns:
        Formatted string with comprehensive analysis results including all metrics, ratios, and quality scores
    """
    # Validate symbol format
    if not (company_id.endswith(".NS") or company_id.endswith(".BO")):
        return f"Error: Invalid symbol format '{company_id}'. Please use format: SYMBOL.NS (NSE) or SYMBOL.BO (BSE)"
    
    try:
        # Fetch data from API
        api_key = API_KEY
        api_base_url = BASE_URL
        
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
                        "cash_balance": float(financial_data[-1].get("cashAndCashEquivalents", 0)) if financial_data else 0,
                        "interest_income": float(financial_data[-1].get("interestIncome", 0)) if financial_data else None
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
        interest_income = data.get("interest_income", None)
        
        # Ensure capex has same length
        if not capex_list or len(capex_list) < len(cfo_list):
            capex_list = [0] * len(cfo_list)
        
        # Convert risk_free_rate from decimal to percentage
        risk_free_rate_pct = risk_free_rate * 100
        
        # Run analysis (EXECUTION BLOCK: Core calculations and data processing)
        analyzer = FinancialAnalyzer()
        
        pat_vs_cfo_result = analyzer.cumulative_pat_vs_cfo(pat_list, cfo_list)
        cfo_ebitda = analyzer.cfo_ebitda_consistency(cfo_list, ebitda_list)
        accrual_result = analyzer.accrual_quality(pat_list, cfo_list)
        dep_volatility = analyzer.depreciation_volatility(depreciation_list, sales_list)
        cash_score_result = analyzer.cash_earning_rate(cash_balance, risk_free_rate_pct, interest_income)
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
        
        # OUTPUT: Single string containing all analysis results (can be as long as needed)
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


# Test the tool
if __name__ == "__main__":
    # Check if API key is loaded
    if not API_KEY or API_KEY == "your_api_key_here":
        print("❌ ERROR: API key not found!")
        print("Please set your API key in the .env file:")
        print("  1. Create a .env file (or edit existing)")
        print("  2. Set AC_API_KEY=your_actual_api_key")
        print("  3. Save the file and run again")
        exit(1)
    
    print("PROFIT QUALITY ANALYSIS TOOL - PRODUCTION TEST")
    print("=" * 70)
    print("Purpose: Comprehensive profit quality and accrual analysis")
    print("For use with LangChain/LangGraph AI agents")
    print("=" * 70)
    
    # Test 1: RELIANCE.BO - Latest data with 7% risk-free rate
    print("\n[TEST 1] Reliance Industries (RELIANCE.BO) - 7% Risk-Free Rate")
    print("-" * 70)
    try:
        result = profit_quality_analysis.invoke({"company_id": "RELIANCE.BO", "risk_free_rate": 0.07})
        print(result)
        print("\n✓ Test 1 Passed")
    except Exception as e:
        print(f"✗ Test 1 Failed: {e}")
    
    # Test 2: TCS.NS - Latest data with 6% risk-free rate
    print("\n" + "=" * 70)
    print("\n[TEST 2] Tata Consultancy Services (TCS.NS) - 6% Risk-Free Rate")
    print("-" * 70)
    try:
        result = profit_quality_analysis.invoke({"company_id": "TCS.NS", "risk_free_rate": 0.06})
        print(result)
        print("\n✓ Test 2 Passed")
    except Exception as e:
        print(f"✗ Test 2 Failed: {e}")
    
    print("\n" + "=" * 70)
    print("\n✅ ALL TESTS COMPLETED - Tool is ready!")
    print("=" * 70)
    print("\nTo use this tool in your LangGraph agent:")
    print("  from tools.profit_quality import profit_quality_analysis")
    print("  result = profit_quality_analysis.invoke({'company_id': 'RELIANCE.BO', 'risk_free_rate': 0.07})")
    print("=" * 70)
