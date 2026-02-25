# Financial Document Analyzer — *Refactored & Future-Proofed* 🚀

This repository contains my revised version of the Financial Document Analyzer built using **CrewAI** and **FastAPI**. I have transformed a broken, synchronous codebase into a stable, asynchronous system with database persistence.

### ✅ Bonus Points Implemented
1.  **Queue Worker Model:** Integrated FastAPI `BackgroundTasks` to handle concurrent requests without blocking. The API now returns a `task_id` immediately.
2.  **Database Integration:** Added an **SQLite** database using **SQLAlchemy** to store persistent records of every analysis, task status, and result.

---

## 🏗️ Re-Engineered System Flow

1.  **Client** uploads a PDF via `POST /analyze`.
2.  **API** saves the file, creates a `pending` record in **SQLite**, and returns a `task_id`.
3.  **Background Worker** takes the task, runs the **CrewAI** workflow (4 specialist agents).
4.  **Database** is updated from `pending` to `completed` (or `failed`) with the final AI response.
5.  **Client** polls `GET /status/{task_id}` to retrieve results.

---

## 🛑 Critical Bug Fixes (The "Crash" Bugs)

| # | Bug | Root Cause | Resolution |
|---|---|---|---|
| **1** | **LLM Crash** | `llm = llm` caused `NameError` | Initialized `ChatOpenAI(model="gpt-4o-mini")` |
| **2** | **Tool Scope** | Agent used `tool=` (singular) | Corrected to `tools=` (plural) for tool recognition |
| **3** | **Execution Limits**| `max_iter=1`, `max_rpm=1` | Bumped to `max_iter=5`, `max_rpm=10` for deep analysis |
| **4** | **Import Error** | `from crewai_tools import tools` | Fixed to `from crewai.tools import tool` |
| **5** | **Ghost `Pdf` Class**| Referenced `Pdf` which was never imported | Replaced with `PyPDFLoader` |
| **6** | **Async Conflict** | Tool was `async def` (unsupported) | Converted to sync + added `@tool` decorator |
| **7** | **Naming Collision**| API route was named same as Task object | Renamed route to `analyze_document` |
| **8** | **Static Loading** | `file_path` ignored in `kickoff` | Correctly passed dynamic path to the AI agents |

---

## 🧠 Brain Overhaul (Prompt Engineering)

The original agents were programmed to "make up facts" and "YOLO." I rewrote all 4 specialist identities:
- **Financial Analyst:** Extracts 100% factual GAAP metrics (Revenue, EPS, Ratios).
- **Compliance Officer:** Validates document structure and reporting ethics.
- **Investment Advisor:** Provides evidence-based stances (Buy/Hold/Sell).
- **Risk Specialist:** Assesses Market/Credit/Liquidity risk via VaR benchmarks.

Every task now enforces a **Strict JSON Output** to ensure machine-readable, reliable results.

---

## 🚀 Setup Instructions

1.  **Environment**
    ```bash
    python -m venv venv
    venv\Scripts\activate       # Windows
    source venv/bin/activate    # Mac/Linux
    pip install -r requirements.txt
    ```

2.  **API Keys**
    Create a `.env` file:
    ```env
    OPENAI_API_KEY=your_key_here
    ```

3.  **Run Server**
    ```bash
    uvicorn main:app --reload
    ```

---

## 🔌 API Documentation

### 1. `POST /analyze`
Upload a PDF for analysis.
- **Payload:** `file` (multipart/pdf)
- **Returns:** `task_id` (used to track analysis)

### 2. `GET /status/{task_id}`
Checks if the AI has finished.
- **Status Types:** `pending`, `completed`, `failed`.
- **Returns:** The full JSON analysis result once completed.

### 3. `GET /`
Standard health check.

---

## 📊 Summary of Improvements
- ✅ **Fixed:** All 9 runtime/crash bugs.
- ✅ **Improved:** Agent reasoning and prompt factual grounding.
- ✅ **Optimized:** Switched to an async background worker model.
- ✅ **Stored:** Integrated SQLite for persistent record keeping.