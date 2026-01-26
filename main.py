"""
Main entry point for Profit Quality & Accrual Analysis Tool

This module demonstrates how to use the profit quality analysis agent
"""

from tools.profit_quality import profit_quality_analysis

def main():
    """
    Main function demonstrating agent usage
    """
    
    # Example: Analyze using company ID
    print("=" * 60)
    print("PROFIT QUALITY & ACCRUAL ANALYSIS")
    print("=" * 60)
    
    # Analyze an Indian stock (NSE/BSE listed)
    company_id = "TCS.NS"  # Tata Consultancy Services (NSE format)
    risk_free_rate = 0.045  # 4.5% as decimal
    
    result = profit_quality_analysis(company_id=company_id, risk_free_rate=risk_free_rate)
    print(result)

if __name__ == "__main__":
    main()
