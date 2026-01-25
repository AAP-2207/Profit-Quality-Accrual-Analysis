from pydantic import BaseModel
from typing import Optional, List

class FinancialData(BaseModel):
    """Input schema for financial data"""
    pat: List[float]  # Profit After Tax (list of values)
    cfo: List[float]  # Cash Flow from Operations (list of values)
    ebitda: List[float]  # EBITDA (list of values)
    depreciation: List[float]  # Depreciation (list of values)
    sales: List[float]  # Sales/Revenue (list of values)
    capex: List[float] = []  # Capital Expenditure (optional, defaults to empty)
    cash_balance: float  # Current cash balance
    risk_free_rate: float  # Risk-free rate (as percentage)
    
class AnalysisConfig(BaseModel):
    """Configuration for analysis parameters"""
    cfo_ebitda_threshold: float = 0.7
    rolling_window: int = 3
    volatility_threshold: Optional[float] = None
