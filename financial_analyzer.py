from typing import List, Dict, Tuple
import statistics

class FinancialAnalyzer:
    """Analyzes financial metrics and quality of earnings"""
    
    @staticmethod
    def cumulative_pat_vs_cfo(pat_list: List[float], cfo_list: List[float], rolling_window: int = 3) -> Dict[str, any]:
        """
        Compare cumulative PAT vs CFO - returns ratio for available period
        
        Args:
            pat_list: List of PAT values (oldest to newest)
            cfo_list: List of CFO values (oldest to newest)
            rolling_window: Window size for rolling average (default 3 years)
            
        Returns:
            Dict with ratio value and actual years of data used
        """
        if len(pat_list) < 1 or len(cfo_list) < 1:
            return {"value": 0.0, "years": 0, "warning": "Insufficient data"}
        
        years_available = min(len(pat_list), len(cfo_list))
        cumulative_pat = sum(pat_list)
        cumulative_cfo = sum(cfo_list)
        ratio = cumulative_cfo / cumulative_pat if cumulative_pat != 0 else 0
        
        return {
            "value": round(ratio, 3),
            "years": years_available,
            "warning": "Only 3 years available" if years_available < 10 else None
        }
    
    @staticmethod
    def cfo_ebitda_consistency(cfo_list: List[float], ebitda_list: List[float], threshold: float = 0.7) -> Dict[str, any]:
        """
        Check CFO/EBITDA consistency - returns detailed breakdown
        
        Args:
            cfo_list: List of CFO values
            ebitda_list: List of EBITDA values
            threshold: Minimum acceptable ratio (default 0.7)
            
        Returns:
            Dict with average CFO, average EBITDA, and ratio
        """
        if len(cfo_list) < 1 or len(ebitda_list) < 1:
            return {
                "avg_cfo": 0.0,
                "avg_ebitda": 0.0,
                "ratio": 0.0
            }
        
        avg_cfo = statistics.mean(cfo_list)
        avg_ebitda = statistics.mean(ebitda_list)
        ratio = avg_cfo / avg_ebitda if avg_ebitda != 0 else 0
        
        return {
            "avg_cfo": round(avg_cfo, 2),
            "avg_ebitda": round(avg_ebitda, 2),
            "ratio": round(ratio, 3)
        }
    
    @staticmethod
    def accrual_quality(pat_list: List[float], cfo_list: List[float]) -> Dict[str, any]:
        """
        Measure accrual profit conversion quality
        Returns detailed accrual analysis
        
        Args:
            pat_list: List of PAT values
            cfo_list: List of CFO values
            
        Returns:
            Dict with average PAT, CFO, accruals, and accrual ratio
        """
        if len(pat_list) < 1 or len(cfo_list) < 1:
            return {
                "avg_pat": 0.0,
                "avg_cfo": 0.0,
                "avg_accruals": 0.0,
                "accrual_ratio": 0.0
            }
        
        avg_pat = statistics.mean(pat_list)
        avg_cfo = statistics.mean(cfo_list)
        accruals = [pat - cfo for pat, cfo in zip(pat_list, cfo_list)]
        avg_accruals = statistics.mean(accruals)
        accrual_ratio = statistics.mean([abs(acc) / avg_pat for acc in accruals if avg_pat != 0])
        
        return {
            "avg_pat": round(avg_pat, 2),
            "avg_cfo": round(avg_cfo, 2),
            "avg_accruals": round(avg_accruals, 2),
            "accrual_ratio": round(accrual_ratio, 4)
        }
    
    @staticmethod
    def depreciation_volatility(depreciation_list: List[float], sales_list: List[float]) -> float:
        """
        Analyze volatility in depreciation as percentage of sales
        Returns percentage volatility
        
        Args:
            depreciation_list: List of depreciation values
            sales_list: List of sales values
            
        Returns:
            Volatility as percentage
        """
        if len(depreciation_list) < 2 or len(sales_list) < 2:
            return 0.0
        
        depreciation_ratios = [
            (dep / sales * 100) if sales != 0 else 0 
            for dep, sales in zip(depreciation_list, sales_list)
        ]
        
        avg_ratio = statistics.mean(depreciation_ratios)
        volatility = statistics.stdev(depreciation_ratios) if len(depreciation_ratios) > 1 else 0
        cv = (volatility / avg_ratio * 100) if avg_ratio != 0 else 0  # Coefficient of variation
        
        return round(cv, 2)
    
    @staticmethod
    def cash_earning_rate(cash_balance: float, risk_free_rate: float, annual_earnings: float = None) -> Dict[str, any]:
        """
        Check if company is earning above risk-free rate on cash
        Returns detailed cash earnings information
        
        Args:
            cash_balance: Current cash balance
            risk_free_rate: Risk-free rate (as percentage)
            annual_earnings: Annual earnings on cash (optional - interest income)
            
        Returns:
            Dict with cash balance, risk-free rate, expected earnings, actual earnings, and earning rate
        """
        expected_annual_earnings = (cash_balance * risk_free_rate) / 100
        
        # If annual_earnings not provided, cannot calculate properly
        if annual_earnings is None:
            return {
                "cash_balance": round(cash_balance, 2),
                "risk_free_rate": risk_free_rate,
                "expected_earnings": round(expected_annual_earnings, 2),
                "actual_earnings": None,
                "earning_rate": None,
                "warning": "No interest income data provided"
            }
        
        # Calculate actual earning rate
        actual_earning_rate = (annual_earnings / cash_balance * 100) if cash_balance != 0 else 0
        
        return {
            "cash_balance": round(cash_balance, 2),
            "risk_free_rate": risk_free_rate,
            "expected_earnings": round(expected_annual_earnings, 2),
            "actual_earnings": round(annual_earnings, 2),
            "earning_rate": round(actual_earning_rate, 3),
            "warning": None
        }
    
    @staticmethod
    def fcf_quality(cfo_list: List[float], depreciation_list: List[float], capex_list: List[float]) -> Dict[str, any]:
        """
        Detect FCF generation gaps and lumpy FCF patterns
        Returns detailed FCF analysis
        
        Args:
            cfo_list: List of CFO values
            depreciation_list: List of depreciation values (not used - kept for compatibility)
            capex_list: List of capital expenditure values
            
        Returns:
            Dict with average FCF, volatility, negative years, and analysis
        
        Note: FCF = CFO - Capex (depreciation already in CFO)
        """
        if len(cfo_list) < 2:
            return {
                "avg_fcf": 0.0,
                "volatility_cv": 0.0,
                "negative_years": 0,
                "total_years": 0,
                "avg_cfo": 0.0,
                "avg_capex": 0.0
            }
        
        # CORRECTED: FCF = CFO - Capex (depreciation already included in CFO)
        fcf_list = [cfo - capex for cfo, capex in zip(cfo_list, capex_list)]
        
        avg_fcf = statistics.mean(fcf_list)
        avg_cfo = statistics.mean(cfo_list)
        avg_capex = statistics.mean(capex_list)
        fcf_volatility = statistics.stdev(fcf_list) if len(fcf_list) > 1 else 0
        cv = (fcf_volatility / avg_fcf * 100) if avg_fcf != 0 else 0
        
        negative_years = sum(1 for fcf in fcf_list if fcf < 0)
        
        return {
            "avg_fcf": round(avg_fcf, 2),
            "volatility_cv": round(cv, 2),
            "negative_years": negative_years,
            "total_years": len(fcf_list),
            "avg_cfo": round(avg_cfo, 2),
            "avg_capex": round(avg_capex, 2)
        }
