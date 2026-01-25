import os
from typing import Any, Dict, Union
from dotenv import load_dotenv
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
from tools.profit_quality import profit_quality_analysis
from data_fetcher import DataFetcher
from financial_analyzer import FinancialAnalyzer
from schemas import FinancialData

load_dotenv()

class ProfitQualityAgent:
    """
    Profit Quality & Accrual Analysis Agent using LangChain React pattern
    
    This agent analyzes:
    - Cumulative PAT vs CFO (10Y)
    - CFO/EBITDA consistency (>0.7 threshold)
    - Accrual profit conversion quality (Score 1-10)
    - Depreciation volatility (percentage)
    - Cash earning rates (Score 1-10)
    - FCFE generation (Yes/No)
    """
    
    def __init__(self):
        """Initialize the agent with LLM and tools"""
        # Check if using local LLM or OpenAI
        use_local = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
        
        if use_local:
            # Use Ollama for local LLM (free, no API key needed)
            model_name = os.getenv("LOCAL_LLM_MODEL", "llama2")
            self.llm = Ollama(model=model_name, temperature=0)
            print(f"Using local LLM: {model_name}")
        else:
            # Fallback to OpenAI if key provided
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0,
                api_key=os.getenv("OPENAI_API_KEY")
            )
            print("Using OpenAI")
        
        # Create ReAct prompt template
        template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
    
    def analyze_company(self, ticker: str) -> str:
        """
        Analyze a company's profit quality and accruals using the ticker symbol
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            Analysis result as a formatted string
        """
        try:
            # Fetch and analyze
            result = profit_quality_analysis(ticker=ticker, risk_free_rate=0.07)
            return result
        
        except Exception as e:
            return f"Error during analysis: {str(e)}"
    
    def analyze_custom_data(self, financial_data: FinancialData) -> str:
        """
        Analyze using custom financial data
        
        Args:
            financial_data: FinancialData object with required metrics
            
        Returns:
            Analysis result as a formatted string
        """
        try:
            return profit_quality_analysis(financial_data=financial_data)
        
        except Exception as e:
            return f"Error during analysis: {str(e)}"

def create_profit_quality_agent() -> ProfitQualityAgent:
    """
    Factory function to create and return a Profit Quality Agent
    
    Returns:
        Initialized ProfitQualityAgent instance
    """
    return ProfitQualityAgent()

def analyze_profit_quality(ticker: str = None, financial_data: FinancialData = None) -> str:
    """
    Main exported function for profit quality analysis
    Returns analysis result as a formatted string
    
    Args:
        ticker: Optional stock ticker symbol
        financial_data: Optional FinancialData object with custom metrics
        
    Returns:
        Analysis result as a formatted string with metrics and scores
    """
    agent = create_profit_quality_agent()
    
    if ticker:
        return agent.analyze_company(ticker)
    elif financial_data:
        return agent.analyze_custom_data(financial_data)
    else:
        return "Error: Please provide either a ticker symbol or financial data"

if __name__ == "__main__":
    # Example usage with custom data
    financial_data = FinancialData(
        pat=[100, 110, 120, 115, 125, 130, 140, 135, 145, 150],
        cfo=[95, 105, 118, 112, 122, 128, 138, 133, 143, 148],
        ebitda=[150, 160, 170, 165, 175, 180, 190, 185, 195, 200],
        depreciation=[20, 20, 21, 21, 22, 22, 23, 23, 24, 24],
        sales=[1000, 1050, 1100, 1080, 1150, 1200, 1250, 1220, 1300, 1350],
        capex=[30, 32, 35, 33, 38, 40, 42, 41, 45, 48],
        cash_balance=500,
        risk_free_rate=4.5
    )
    
    result = analyze_profit_quality(financial_data=financial_data)
    print(result)
