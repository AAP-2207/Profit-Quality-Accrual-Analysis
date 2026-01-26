"""
Test profit quality analysis with two Indian stocks
"""

from tools.profit_quality import profit_quality_analysis

print("=" * 70)
print("TEST 1: TCS (Tata Consultancy Services)")
print("=" * 70)

result1 = profit_quality_analysis(company_id="TCS.NS", risk_free_rate=0.045)
print(result1)

print("\n\n")

print("=" * 70)
print("TEST 2: RELIANCE (Reliance Industries)")
print("=" * 70)

result2 = profit_quality_analysis(company_id="RELIANCE.NS", risk_free_rate=0.045)
print(result2)
