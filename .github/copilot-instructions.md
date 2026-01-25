# Profit Quality & Accrual Analysis Tool - Project Setup

## Project Overview
Python-based financial analysis tool for analyzing company profit quality and accrual metrics using your financial data API.

## Completed Steps

✅ **Project Initialization**
- Created project structure with all necessary modules
- Set up requirements.txt with dependencies (no OpenAI/LangChain/LangGraph)
- Configured .env file for API credentials only

✅ **Core Implementation**
- `schemas.py`: Pydantic models for financial data validation (list-based inputs)
- `data_fetcher.py`: API integration for financial data retrieval
- `financial_analyzer.py`: 6 core analysis functions returning specific values/scores
- `agent.py`: Main analysis orchestrator (direct Python, no LLM required)
- `main.py`: Example usage and entry point

✅ **Documentation**
- Comprehensive README.md with setup, usage, and output format details

## Key Features Implemented

1. **Cumulative PAT vs CFO Analysis** → Returns ratio value (float)
2. **CFO/EBITDA Consistency Check** → Returns ratio value (float)
3. **Accrual Quality Measurement** → Returns score 1-10 (10=better quality)
4. **Depreciation Volatility Analysis** → Returns percentage (float)
5. **Cash Earning Rate vs Risk-Free** → Returns score 1-10 (10=earning much more)
6. **Lack of FCFE Generation** → Returns "Yes" or "No"

## Technologies Used
- **Python 3.9+**: Core language
- **Pydantic**: Data validation and schemas
- **Requests**: HTTP client for API calls
- **python-dotenv**: Environment variable management

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure .env File**
   ```
   API_KEY=your_api_key
   API_BASE_URL=your_api_url
   ```

3. **Run the Analysis**
   ```bash
   python main.py
   ```

## Usage Examples

### Using Custom Financial Data
```python
from agent import analyze_profit_quality
from schemas import FinancialData

data = FinancialData(
    pat=[100, 110, 120, ...],       # 10-year values
    cfo=[95, 105, 118, ...],
    ebitda=[150, 160, 170, ...],
    depreciation=[20, 20, 21, ...],
    sales=[1000, 1050, 1100, ...],
    capex=[30, 32, 35, ...],
    cash_balance=500,
    risk_free_rate=4.5
)

result = analyze_profit_quality(financial_data=data)
print(result)
```

### Using Ticker Symbol
```python
from agent import analyze_profit_quality

result = analyze_profit_quality(ticker="AAPL")
```

## Output Format

Returns formatted string with 6 metrics:
- Cumulative PAT vs CFO Ratio: numeric value
- CFO/EBITDA Consistency: numeric value
- Accrual Quality Score: 1-10
- Depreciation Volatility: percentage
- Cash Earning Score: 1-10
- FCFE Generation Status: Yes/No

## Function Returns
All functions return a **formatted string** containing the analysis results with metrics and scores.

## Project Structure
```
.
├── agent.py                 # Main analysis orchestrator
├── financial_analyzer.py    # 6 analysis functions
├── data_fetcher.py         # API integration
├── schemas.py              # Pydantic models
├── main.py                 # Entry point with example
├── tools.py                # Deprecated (for reference)
├── requirements.txt        # Dependencies
├── .env                    # Configuration (not in git)
├── README.md              # Documentation
└── .github/
    └── copilot-instructions.md
```

## Status
**Project Ready for Use** - All core functionality implemented and tested. No LLM/LangChain dependencies required.
