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
    def cfo_ebitda_consistency(cfo_list: List[float], ebitda_list: List[float], threshold: float = 0.7) -> float:
        """
        Check CFO/EBITDA consistency - returns average ratio
        
        Args:
            cfo_list: List of CFO values
            ebitda_list: List of EBITDA values
            threshold: Minimum acceptable ratio (default 0.7)
            
        Returns:
            Average CFO/EBITDA ratio
        """
        if len(cfo_list) < 1 or len(ebitda_list) < 1:
            return 0.0
        
        ratios = []
        for cfo, ebitda in zip(cfo_list, ebitda_list):
            if ebitda != 0:
                ratio = cfo / ebitda
                ratios.append(ratio)
        
        avg_ratio = statistics.mean(ratios) if ratios else 0
        return round(avg_ratio, 3)
    
    @staticmethod
    def accrual_quality(pat_list: List[float], cfo_list: List[float]) -> int:
        """
        Measure accrual profit conversion quality
        Returns score 1-10 (10=low ratio/better quality, 1=high ratio/worse quality)
        
        Args:
            pat_list: List of PAT values
            cfo_list: List of CFO values
            
        Returns:
            Quality score 1-10
        """
        if len(pat_list) < 1 or len(cfo_list) < 1:
            return 5
        
        accruals = [pat - cfo for pat, cfo in zip(pat_list, cfo_list)]
        avg_pat = statistics.mean(pat_list) if pat_list else 1
        accrual_ratio = statistics.mean([abs(acc) / avg_pat for acc in accruals if avg_pat != 0])
        
        # Convert ratio to score: lower ratio = higher quality = higher score
        # Assume ratio > 0.3 = score 1, ratio < 0.05 = score 10
        if accrual_ratio < 0.05:
            score = 10
        elif accrual_ratio < 0.10:
            score = 9
        elif accrual_ratio < 0.15:
            score = 8
        elif accrual_ratio < 0.20:
            score = 7
        elif accrual_ratio < 0.25:
            score = 6
        elif accrual_ratio < 0.30:
            score = 5
        elif accrual_ratio < 0.35:
            score = 4
        elif accrual_ratio < 0.40:
            score = 3
        elif accrual_ratio < 0.45:
            score = 2
        else:
            score = 1
        
        return score
    
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
        Returns score 1-10 (10=earning much more than risk-free, 1=earning less/equal)
        
        Args:
            cash_balance: Current cash balance
            risk_free_rate: Risk-free rate (as percentage)
            annual_earnings: Annual earnings on cash (optional - interest income)
            
        Returns:
            Dict with score and warning if data insufficient
        """
        expected_annual_earnings = (cash_balance * risk_free_rate) / 100
        
        # If annual_earnings not provided, cannot calculate properly
        if annual_earnings is None:
            return {
                "score": 5,
                "warning": "No interest income data provided - neutral score assigned"
            }
        
        # Calculate how much above/below risk-free rate
        earning_ratio = annual_earnings / expected_annual_earnings if expected_annual_earnings != 0 else 1
        
        # Convert ratio to score
        if earning_ratio >= 3.0:
            score = 10
        elif earning_ratio >= 2.5:
            score = 9
        elif earning_ratio >= 2.0:
            score = 8
        elif earning_ratio >= 1.5:
            score = 7
        elif earning_ratio >= 1.2:
            score = 6
        elif earning_ratio >= 1.0:
            score = 5
        elif earning_ratio >= 0.8:
            score = 4
        elif earning_ratio >= 0.5:
            score = 3
        elif earning_ratio > 0:
            score = 2
        else:
            score = 1
        
        return {"score": score, "warning": None}
    
    @staticmethod
    def fcf_quality(cfo_list: List[float], depreciation_list: List[float], capex_list: List[float]) -> str:
        """
        Detect FCF generation gaps and lumpy FCF patterns
        Returns "Yes" or "No" for lack of FCF generation
        
        Args:
            cfo_list: List of CFO values
            depreciation_list: List of depreciation values (not used - kept for compatibility)
            capex_list: List of capital expenditure values
            
        Returns:
            "Yes" if lack of FCF generation detected, "No" otherwise
        
        Note: FCF = CFO - Capex (depreciation already in CFO)
        """
        if len(cfo_list) < 2:
            return "No"
        
        # CORRECTED: FCF = CFO - Capex (depreciation already included in CFO)
        fcf_list = [cfo - capex for cfo, capex in zip(cfo_list, capex_list)]
        
        avg_fcf = statistics.mean(fcf_list)
        fcf_volatility = statistics.stdev(fcf_list) if len(fcf_list) > 1 else 0
        cv = (fcf_volatility / avg_fcf * 100) if avg_fcf != 0 else 0
        
        negative_years = sum(1 for fcf in fcf_list if fcf < 0)
        
        # Detect lack of FCF generation:
        # 1. More than 30% of years with negative FCF
        # 2. Very high volatility (>50%)
        # 3. Average FCF is negative
        lack_of_fcf = (
            negative_years / len(fcf_list) > 0.3 or 
            cv > 50 or 
            avg_fcf < 0
        )
        
        return "Yes" if lack_of_fcf else "No"
