"""
Main entry point for Profit Quality & Accrual Analysis Tool

This module demonstrates how to use the profit quality analysis agent
"""

from tools.profit_quality import profit_quality_analysis
from schemas import FinancialData

def main():
    """
    Main function demonstrating agent usage
    """
    
    # Example: Analyze using custom financial data
    print("=" * 60)
    print("PROFIT QUALITY & ACCRUAL ANALYSIS")
    print("=" * 60)
    
    # Create sample financial data (10 years of data)
    financial_data = FinancialData(
        pat=[100, 110, 120, 115, 125, 130, 140, 135, 145, 150],  
        cfo=[95, 105, 118, 112, 122, 128, 138, 133, 143, 148],    
        ebitda=[150, 160, 170, 165, 175, 180, 190, 185, 195, 200],  
        depreciation=[20, 20, 21, 21, 22, 22, 23, 23, 24, 24],    
        sales=[1000, 1050, 1100, 1080, 1150, 1200, 1250, 1220, 1300, 1350],
        capex=[30, 32, 35, 33, 38, 40, 42, 41, 45, 48],  # Capital expenditure
        cash_balance=500,  
        risk_free_rate=4.5  
    )
    
    result = profit_quality_analysis(financial_data=financial_data)
    print(result)

if __name__ == "__main__":
    main()
