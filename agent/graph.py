"""
LangGraph-based Profit Quality Analysis Agent
Uses ReAct pattern with state management
"""

import os
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.profit_quality import profit_quality_analysis

load_dotenv()

# Define the state
class ProfitQualityState(TypedDict):
    company_id: str
    risk_free_rate: float
    result: str
    messages: list


def analyze_node(state: ProfitQualityState) -> ProfitQualityState:
    """
    Main analysis node - executes the profit quality analysis
    """
    company_id = state.get("company_id")
    risk_free_rate = state.get("risk_free_rate")
    
    # Call the profit quality analysis tool
    result = profit_quality_analysis(
        company_id=company_id,
        risk_free_rate=risk_free_rate
    )
    
    return {
        **state,
        "result": result
    }


# Create the graph
workflow = StateGraph(ProfitQualityState)

# Add nodes
workflow.add_node("analyze", analyze_node)

# Set entry point
workflow.set_entry_point("analyze")

# Add edges
workflow.add_edge("analyze", END)

# Compile the graph
profit_quality_graph = workflow.compile()


# Alternative: More complex agent with LLM reasoning
class AdvancedProfitQualityState(TypedDict):
    company_id: str
    risk_free_rate: float
    analysis_result: str
    llm_interpretation: str
    result: str
    messages: list


def fetch_and_analyze_node(state: AdvancedProfitQualityState) -> AdvancedProfitQualityState:
    """Fetch data and run analysis"""
    company_id = state.get("company_id")
    risk_free_rate = state.get("risk_free_rate")
    
    analysis_result = profit_quality_analysis(
        company_id=company_id,
        risk_free_rate=risk_free_rate
    )
    
    return {
        **state,
        "analysis_result": analysis_result
    }


def interpret_node(state: AdvancedProfitQualityState) -> AdvancedProfitQualityState:
    """Optional: Use LLM to interpret results"""
    analysis_result = state.get("analysis_result", "")
    
    # Use local LLM if available
    use_local = os.getenv("USE_LOCAL_LLM", "true").lower() == "true"
    
    if use_local:
        try:
            llm = Ollama(model=os.getenv("LOCAL_LLM_MODEL", "llama2"), temperature=0)
            prompt = f"""Analyze this financial report and provide a brief summary of the company's profit quality:

{analysis_result}

Provide a 2-3 sentence summary focusing on the key strengths or concerns."""
            
            interpretation = llm.invoke(prompt)
            
            final_result = f"{analysis_result}\n\nLLM INTERPRETATION:\n{interpretation}"
        except Exception as e:
            # If LLM fails, just return the analysis
            final_result = analysis_result
    else:
        final_result = analysis_result
    
    return {
        **state,
        "result": final_result
    }


# Create advanced graph
advanced_workflow = StateGraph(AdvancedProfitQualityState)
advanced_workflow.add_node("fetch_analyze", fetch_and_analyze_node)
advanced_workflow.add_node("interpret", interpret_node)
advanced_workflow.set_entry_point("fetch_analyze")
advanced_workflow.add_edge("fetch_analyze", "interpret")
advanced_workflow.add_edge("interpret", END)

profit_quality_graph_advanced = advanced_workflow.compile()
