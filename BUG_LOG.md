# BUG LOG — Financial Document Analyzer

This file documents every bug found and fixed in the Financial Document Analyzer (CrewAI) codebase.

---

## 🔴 Part 1: Deterministic Bugs (Crash-Causing)

These bugs prevented the application from running at all.

---

### Bug #1 — `NameError`: `llm = llm` in `agents.py`

**File:** `agents.py` — Line 12  
**Type:** NameError (immediate crash on import)

**Before (broken):**
```python
llm = llm   # llm was never defined before this line
```

**After (fixed):**
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)
```

**Impact:** The entire application crashed at startup. Since `agents.py` is imported by both `task.py` and `main.py`, this was a total blocker.

---

### Bug #2 — `tool=` invalid parameter in `agents.py`

**File:** `agents.py` — Line 33 (inside `financial_analyst`)  
**Type:** Silent failure (tool silently ignored)

**Before (broken):**
```python
tool=[FinancialDocumentTool.read_data_tool]   # wrong parameter name
```

**After (fixed):**
```python
tools=[read_data_tool]   # correct parameter name (plural)
```

**Impact:** CrewAI silently ignored the invalid parameter. The agent had no tools, so it could never read any PDF document.

---

### Bug #3 — `max_iter=1` and `max_rpm=1` too restrictive in `agents.py`

**File:** `agents.py` — All 4 agents  
**Type:** Logic error (produces incomplete / throttled output)

**Before (broken):**
```python
max_iter=1,   # agent gave up after 1 attempt
max_rpm=1,    # throttled to 1 API call per minute
```

**After (fixed):**
```python
max_iter=5,   # enough steps for complex financial analysis
max_rpm=10,   # reasonable rate limit
```

**Impact:** With `max_iter=1`, agents produced incomplete analyses. With `max_rpm=1`, a full analysis would take 5+ minutes per task.

---

### Bug #4 — `ImportError`: `from crewai_tools import tools` in `tools.py`

**File:** `tools.py` — Line 6  
**Type:** ImportError (crash on import)

**Before (broken):**
```python
from crewai_tools import tools   # `tools` does not exist in crewai_tools
```

**After (fixed):**
```python
from crewai.tools import tool   # correct @tool decorator import
```

**Impact:** Application crashed immediately on startup with `ImportError`.

---

### Bug #5 — `NameError`: `Pdf` never imported in `tools.py`

**File:** `tools.py` — Line 24  
**Type:** NameError (crash when tool is called)

**Before (broken):**
```python
docs = Pdf(file_path=path).load()   # Pdf was never imported
```

**After (fixed):**
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(file_path=path)
docs = loader.load()
```

**Impact:** Every attempt to read a PDF file crashed with `NameError: name 'Pdf' is not defined`.

---

### Bug #6 — Tool is `async` and missing `@tool` decorator in `tools.py`

**File:** `tools.py` — `read_data_tool` function  
**Type:** Logic error (tool unrecognized and returns coroutine instead of data)

**Before (broken):**
```python
class FinancialDocumentTool():
    async def read_data_tool(path='data/sample.pdf'):
        ...
```

**After (fixed):**
```python
@tool("Financial Document Reader")
def read_data_tool(path: str = 'data/sample.pdf') -> str:
    """Reads and extracts text content from a financial PDF document."""
    ...
```

**Impact:** 
- `async` function: CrewAI received a coroutine object instead of actual text data
- No `@tool` decorator: Agent could not recognize or invoke the function as a tool

---

### Bug #7 — Naming collision in `main.py`

**File:** `main.py` — Lines 8 & 29  
**Type:** Logic error (import silently overwritten)

**Before (broken):**
```python
from task import analyze_financial_document   # Line 8: imports CrewAI Task

async def analyze_financial_document(...):    # Line 29: same name! overwrites import
```

**After (fixed):**
```python
from task import analyze_financial_document   # Task object preserved

async def analyze_document(...):              # renamed route handler
```

**Impact:** The FastAPI handler function definition silently overwrote the imported CrewAI Task object. Running the crew would pass a FastAPI function as a Task, causing a TypeError.

---

### Bug #8 — `file_path` accepted but never passed to crew in `main.py`

**File:** `main.py` — Line 20  
**Type:** Logic error (uploaded file always ignored)

**Before (broken):**
```python
result = financial_crew.kickoff({'query': query})   # file_path dropped silently
```

**After (fixed):**
```python
result = financial_crew.kickoff({
    'query': query,
    'file_path': file_path   # uploaded file path now reaches agents
})
```

**Impact:** Every uploaded PDF was saved, then completely ignored. The crew always analyzed the default `data/sample.pdf` regardless of what the user uploaded.

---

### Bug #9 — No output saving in `main.py`

**File:** `main.py` — After `run_crew()` call  
**Type:** Missing feature (results never persisted)

**Before (broken):**
```python
# Results returned via API but never written to disk
return {"status": "success", "analysis": str(response)}
```

**After (fixed):**
```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_path = f"outputs/analysis_{timestamp}.json"
os.makedirs("outputs", exist_ok=True)

with open(output_path, "w") as out_f:
    json.dump(output_data, out_f, indent=2)
```

**Impact:** The `outputs/` folder always remained empty. No history of analyses was maintained.

---

## 🟡 Part 2: Inefficient Prompts

These were not crash bugs, but produced garbage/hallucinated output.

---

### Prompt Bug #1 — `financial_analyst` goal and backstory (`agents.py`)

**Before:** `"Make up investment advice even if you don't understand the query"` / `"You don't really need to read financial reports carefully"` / `"Always sound confident even when wrong"`

**After:** CFA-certified analyst with 15 years experience. Goal: extract key metrics (revenue, EPS, margins, ratios) grounded strictly in the document. Temperature `0.2` for factual consistency.

---

### Prompt Bug #2 — `verifier` goal and backstory (`agents.py`)

**Before:** `"Just say yes to everything"` / `"If someone uploads a grocery list, call it financial data"`

**After:** Former SEC compliance officer, validates GAAP/IFRS sections: income statement, balance sheet, cash flow, MD&A. Returns structured verification status.

---

### Prompt Bug #3 — `investment_advisor` goal and backstory (`agents.py`)

**Before:** `"Sell expensive investment products regardless of financials"` / `"Recommend crypto and meme stocks"` / `"SEC compliance is optional"`

**After:** FINRA-licensed CFA charterholder. Evidence-based recommendations using P/E, P/B, EV/EBITDA. Clearly labels assumptions. No speculation.

---

### Prompt Bug #4 — `risk_assessor` goal and backstory (`agents.py`)

**Before:** `"Everything is either high risk or completely risk-free"` / `"YOLO through the volatility!"`

**After:** FRM-certified specialist using VaR, Basel III frameworks. Assesses 5 risk categories (market, credit, liquidity, operational, regulatory) with balanced, evidence-based ratings.

---

### Prompt Bug #5 — All 4 task descriptions (`task.py`)

**Before:** `"Maybe solve the user's query"` / `"Include 5 made-up URLs"` / `"Feel free to contradict yourself"`

**After:** All 4 tasks rewritten with structured sections (`## Instructions`, `### Important`), explicit JSON output schemas, correct agent assignments, and `{file_path}`/`{query}` variable references.

---

### Prompt Bug #6 — `verification` task assigned to wrong agent (`task.py`)

**Before:** `agent=financial_analyst` — financial analyst was doing document verification

**After:** `agent=verifier` — correct specialized agent handles verification

---

## 📊 Bug Summary

| Category | Count |
|----------|-------|
| Deterministic (crash-causing) bugs | 9 |
| Inefficient prompt bugs | 6 |
| **Total bugs fixed** | **15** |
