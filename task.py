## Importing libraries and files
from crewai import Task

from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import read_data_tool

# PROMPT IMPROVEMENT: Rewrote all task descriptions and expected_outputs from
# intentionally vague/broken prompts to structured, JSON-output, professional definitions.
# Also fixed Bug (TK4): `verification` task was incorrectly assigned to `financial_analyst`
# instead of the `verifier` agent.

## Task 1: Document Verification
verification = Task(
    description=(
        "## Document Verification Task\n\n"
        "**File to verify:** {file_path}\n\n"
        "### Instructions:\n"
        "1. Read the financial document at the provided file path using the available tool.\n"
        "2. Confirm that the document is a legitimate financial report (e.g., 10-K, 10-Q, "
        "annual report, earnings release, or audited financial statement).\n"
        "3. Check for the presence of standard financial sections:\n"
        "   - Income Statement (Revenue, COGS, Net Income)\n"
        "   - Balance Sheet (Assets, Liabilities, Equity)\n"
        "   - Cash Flow Statement (Operating, Investing, Financing)\n"
        "   - Management Discussion & Analysis (MD&A) if present\n"
        "4. Flag any missing sections, inconsistencies, or unusual formatting.\n"
        "5. Confirm the reporting period (quarterly/annual) and the reporting entity.\n\n"
        "### Important:\n"
        "Base your verification strictly on the document content. Do not assume or fabricate."
    ),
    expected_output=(
        "A structured JSON object with the following fields:\n"
        "{\n"
        '  "is_financial_document": true/false,\n'
        '  "document_type": "10-K / 10-Q / Annual Report / Earnings Release / Other",\n'
        '  "reporting_entity": "Company name",\n'
        '  "reporting_period": "Q2 2025 / FY 2024 / etc.",\n'
        '  "sections_found": ["Income Statement", "Balance Sheet", "Cash Flow", "MD&A"],\n'
        '  "sections_missing": [],\n'
        '  "anomalies_detected": [],\n'
        '  "verification_status": "PASSED / FAILED / PARTIAL"\n'
        "}"
    ),
    agent=verifier,  # FIX (TK4): Was incorrectly assigned to `financial_analyst` instead of `verifier`
    tools=[read_data_tool],
    async_execution=False,
)


## Task 2: Core Financial Analysis
analyze_financial_document = Task(
    description=(
        "## Financial Document Analysis Task\n\n"
        "**Document path:** {file_path}\n"
        "**User query:** {query}\n\n"
        "### Instructions:\n"
        "1. Read the full financial document at {file_path} using the available tool.\n"
        "2. Extract and analyze the following key financial metrics:\n"
        "   - Revenue and revenue growth (YoY %)\n"
        "   - Gross profit margin and net profit margin\n"
        "   - Earnings Per Share (EPS) — basic and diluted\n"
        "   - EBITDA and operating cash flow\n"
        "   - Total debt, debt-to-equity ratio\n"
        "   - Current ratio and quick ratio (liquidity)\n"
        "   - Return on Equity (ROE) and Return on Assets (ROA)\n"
        "3. Identify key trends, year-over-year changes, and material financial events.\n"
        "4. Address the specific user query: {query}\n"
        "5. Note any significant risks, opportunities, or anomalies found in the data.\n\n"
        "### Important:\n"
        "All figures must be sourced directly from the document. "
        "Do not fabricate numbers or cite external sources not in the document."
    ),
    expected_output=(
        "A structured JSON object with the following fields:\n"
        "{\n"
        '  "company": "Company name",\n'
        '  "reporting_period": "Period covered",\n'
        '  "summary": "2-3 sentence executive summary",\n'
        '  "key_metrics": {\n'
        '    "revenue": "value and YoY change",\n'
        '    "net_income": "value and YoY change",\n'
        '    "eps_diluted": "value",\n'
        '    "gross_margin_pct": "value",\n'
        '    "net_margin_pct": "value",\n'
        '    "debt_to_equity": "value",\n'
        '    "current_ratio": "value",\n'
        '    "roe": "value",\n'
        '    "operating_cash_flow": "value"\n'
        '  },\n'
        '  "key_trends": ["trend 1", "trend 2"],\n'
        '  "query_response": "Direct answer to the user query",\n'
        '  "risks": ["risk 1", "risk 2"],\n'
        '  "opportunities": ["opportunity 1", "opportunity 2"]\n'
        "}"
    ),
    agent=financial_analyst,
    tools=[read_data_tool],
    async_execution=False,
)


## Task 3: Investment Analysis
investment_analysis = Task(
    description=(
        "## Investment Analysis Task\n\n"
        "**Document path:** {file_path}\n"
        "**User query:** {query}\n\n"
        "### Instructions:\n"
        "1. Using the financial analysis already performed, assess the investment profile "
        "of the company.\n"
        "2. Calculate or estimate standard valuation metrics where data is available:\n"
        "   - Price-to-Earnings (P/E) ratio\n"
        "   - Price-to-Book (P/B) ratio\n"
        "   - Enterprise Value / EBITDA (EV/EBITDA)\n"
        "   - Free Cash Flow Yield\n"
        "3. Compare the company's financial performance against industry benchmarks "
        "where explicitly mentioned in the document.\n"
        "4. Provide a clear investment stance: Bullish / Neutral / Bearish — with justification.\n"
        "5. Distinguish between short-term (0–12 months) and long-term (1–3 years) considerations.\n\n"
        "### Important:\n"
        "All recommendations must be grounded in documented financial data. "
        "Clearly label any assumption made. No speculative assets unless specifically "
        "mentioned and justified by the document."
    ),
    expected_output=(
        "A structured JSON object with the following fields:\n"
        "{\n"
        '  "investment_stance": "Bullish / Neutral / Bearish",\n'
        '  "stance_justification": "Evidence-based reasoning",\n'
        '  "valuation_metrics": {\n'
        '    "pe_ratio": "value or N/A",\n'
        '    "pb_ratio": "value or N/A",\n'
        '    "ev_ebitda": "value or N/A",\n'
        '    "fcf_yield": "value or N/A"\n'
        '  },\n'
        '  "short_term_outlook": "0-12 month assessment",\n'
        '  "long_term_outlook": "1-3 year assessment",\n'
        '  "key_catalysts": ["catalyst 1", "catalyst 2"],\n'
        '  "key_concerns": ["concern 1", "concern 2"],\n'
        '  "recommendation": "Hold / Buy / Sell with specific reasoning"\n'
        "}"
    ),
    agent=investment_advisor,
    tools=[read_data_tool],
    async_execution=False,
)


## Task 4: Risk Assessment
risk_assessment = Task(
    description=(
        "## Risk Assessment Task\n\n"
        "**Document path:** {file_path}\n"
        "**User query:** {query}\n\n"
        "### Instructions:\n"
        "1. Read and analyze the financial document at {file_path} for risk indicators.\n"
        "2. Assess the following risk categories based on documented evidence:\n"
        "   - **Market Risk**: Exposure to macroeconomic factors, FX, interest rate sensitivity\n"
        "   - **Credit Risk**: Debt levels, credit ratings (if mentioned), interest coverage ratio\n"
        "   - **Liquidity Risk**: Current ratio, quick ratio, cash runway\n"
        "   - **Operational Risk**: Supply chain issues, regulatory challenges, cost pressures\n"
        "   - **Regulatory/Compliance Risk**: Legal proceedings, SEC notices, pending litigation\n"
        "3. Assign a risk rating (Low / Medium / High) to each category with justification.\n"
        "4. Provide risk mitigation strategies appropriate to the company's financial profile.\n\n"
        "### Important:\n"
        "Base all risk assessments strictly on data found in the document. "
        "Provide balanced, proportionate assessments — neither overstating nor understating risk."
    ),
    expected_output=(
        "A structured JSON object with the following fields:\n"
        "{\n"
        '  "overall_risk_rating": "Low / Medium / High",\n'
        '  "risk_summary": "2-3 sentence overview",\n'
        '  "risk_categories": {\n'
        '    "market_risk": {"rating": "Low/Medium/High", "factors": [], "evidence": ""},\n'
        '    "credit_risk": {"rating": "Low/Medium/High", "factors": [], "evidence": ""},\n'
        '    "liquidity_risk": {"rating": "Low/Medium/High", "factors": [], "evidence": ""},\n'
        '    "operational_risk": {"rating": "Low/Medium/High", "factors": [], "evidence": ""},\n'
        '    "regulatory_risk": {"rating": "Low/Medium/High", "factors": [], "evidence": ""}\n'
        '  },\n'
        '  "key_risk_indicators": ["KRI 1", "KRI 2"],\n'
        '  "mitigation_strategies": ["strategy 1", "strategy 2"]\n'
        "}"
    ),
    agent=risk_assessor,
    tools=[read_data_tool],
    async_execution=False,
)