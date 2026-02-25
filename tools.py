## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai.tools import tool  # FIX (Bug #4): `from crewai_tools import tools` caused ImportError
from langchain_community.document_loaders import PyPDFLoader  # FIX (Bug #5): `Pdf` was used but never imported

## Creating search tool (optional — requires SERPER_API_KEY)
try:
    from crewai_tools.tools.serper_dev_tool import SerperDevTool
    search_tool = SerperDevTool() if os.getenv("SERPER_API_KEY") else None
except ImportError:
    search_tool = None  # serper not installed, skip gracefully

## FIX (Bug #5 + Bug #6):
# Bug #5: `Pdf` was never imported — caused NameError when reading any PDF.
#         Fixed by importing and using `PyPDFLoader` from langchain_community.
# Bug #6: Tool was `async` (CrewAI cannot await it, returns coroutine not data)
#         and had no `@tool` decorator (agent couldn't recognize or call it).
#         Fixed by making it a sync function with proper `@tool` decorator + docstring.

@tool("Financial Document Reader")
def read_data_tool(path: str = 'data/sample.pdf') -> str:
    """Reads and extracts the full text content from a financial PDF document.

    Args:
        path (str): Path to the PDF file to read. Defaults to 'data/sample.pdf'.

    Returns:
        str: Full text content extracted from the financial document.
    """
    loader = PyPDFLoader(file_path=path)
    docs = loader.load()

    full_report = ""
    for data in docs:
        # Clean and format the financial document data
        content = data.page_content

        # Remove extra whitespaces and format properly
        while "\n\n" in content:
            content = content.replace("\n\n", "\n")

        full_report += content + "\n"

    return full_report


## Creating a wrapper class to maintain backward compatibility with agents.py import
class FinancialDocumentTool:
    read_data_tool = read_data_tool


## Creating Investment Analysis Tool
class InvestmentTool:
    def analyze_investment_tool(self, financial_document_data):
        # Process and analyze the financial document data
        processed_data = financial_document_data

        # Clean up the data format
        i = 0
        while i < len(processed_data):
            if processed_data[i:i+2] == "  ":  # Remove double spaces
                processed_data = processed_data[:i] + processed_data[i+1:]
            else:
                i += 1

        # TODO: Implement investment analysis logic here
        return "Investment analysis functionality to be implemented"


## Creating Risk Assessment Tool
class RiskTool:
    def create_risk_assessment_tool(self, financial_document_data):
        # TODO: Implement risk assessment logic here
        return "Risk assessment functionality to be implemented"