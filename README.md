# Financial Document Analyzer — Debugged & Refactored Version

This repository contains my revised version of the Financial Document Analyzer built using CrewAI and FastAPI.

The original codebase contained multiple deterministic bugs that prevented execution, along with loosely designed prompts that resulted in unreliable financial analysis.

In this submission, I have:

- Resolved all runtime errors
- Corrected misconfigured CrewAI components
- Refactored agent and task definitions
- Redesigned prompts for structured, professional financial reasoning
- Enforced deterministic JSON outputs
- Implemented output persistence

The system now executes reliably and produces consistent, structured analysis results.

---

## Project Overview

The application analyzes financial PDF documents using a multi-agent CrewAI workflow.

Each agent performs a specific responsibility within the analysis pipeline:

- Financial Analyst — extracts financial metrics and summarizes performance
- Compliance Reviewer — validates document credibility and reporting standards
- Investment Advisor — provides evidence-based investment stance
- Risk Specialist — categorizes and evaluates financial risk exposure

The FastAPI backend accepts a PDF upload, processes it through the CrewAI system, returns structured JSON, and saves the result locally.

---

## Deterministic Bugs Identified & Fixed

Below is a summary of the critical issues that were preventing stable execution.

| # | Issue | Root Cause | Resolution |
|---|-------|------------|------------|
| 1 | LLM Initialization Failure | `llm` referenced before assignment | Properly initialized ChatOpenAI instance |
| 2 | Incorrect Tool Parameter | Used `tool=` instead of `tools=` | Corrected to `tools=[...]` |
| 3 | Agent Execution Limits | `max_iter=1`, `max_rpm=1` | Adjusted for realistic reasoning flow |
| 4 | Broken Import | Invalid CrewAI tools import | Corrected module import |
| 5 | Undefined PDF Class | Used non-existent `Pdf` class | Replaced with PyPDFLoader |
| 6 | Async Tool Misconfiguration | Tool defined as async without decorator | Converted to sync and registered with @tool |
| 7 | Namespace Collision | API route name matched Task name | Renamed route handler |
| 8 | Static File Usage | Uploaded file path ignored | Passed dynamic input into Crew kickoff |
| 9 | Missing Output Persistence | Results not saved | Implemented timestamped JSON storage |

All runtime-breaking issues have been resolved. The application now runs without crashes.

---

## Prompt Refactoring & Agent Improvements

The original prompts were vague and allowed unreliable reasoning.
Each agent was redesigned to reflect realistic financial roles and enforce structured decision-making.

Improvements introduced:

- Clearly defined professional identities
- Domain-aligned reasoning expectations
- Explicit output schemas
- Reduced ambiguity and hallucination risk
- Controlled temperature for consistent outputs

---

## Structured JSON Output

All analysis tasks enforce deterministic JSON responses.

Example response structure:

{
  "financial_summary": "...",
  "key_metrics": {
    "revenue": "...",
    "net_income": "...",
    "eps": "..."
  },
  "investment_stance": "Bullish | Neutral | Bearish",
  "risk_assessment": {
    "market_risk": "...",
    "credit_risk": "...",
    "liquidity_risk": "..."
  }
}

This ensures:

- Machine-readable responses
- API reliability
- Easier downstream integration
- Reduced formatting inconsistencies

---

## System Flow

Client
→ FastAPI Endpoint (POST /analyze)
→ CrewAI (Agents + Tasks)
→ PDF Loader (PyPDFLoader)
→ Structured JSON Response
→ Saved to outputs/analysis_{timestamp}.json

---

## Setup Instructions

1. Create Virtual Environment

python -m venv venv

Activate:

Windows:
venv\Scripts\activate

Mac/Linux:
source venv/bin/activate

2. Install Dependencies

pip install -r requirements.txt

3. Configure Environment Variables

Create a .env file:

OPENAI_API_KEY=your_api_key_here

4. Run the Application

uvicorn main:app --reload

---

## API Specification

Endpoint:
POST /analyze

Request:
- Content-Type: multipart/form-data
- Field: file (PDF document)

Response:
- Structured JSON analysis
- Automatically persisted to the outputs/ directory

---

## Key Improvements Beyond Bug Fixes

- Stable LLM initialization
- Proper tool registration
- Dynamic file handling
- Controlled agent iteration limits
- Deterministic structured outputs
- Output persistence for auditability
- Cleaner separation of responsibilities

---

## Final Status

- All deterministic runtime errors resolved
- Agent prompts refactored for structured financial reasoning
- Stable CrewAI workflow
- Deterministic JSON API responses
- Persistent output storage implemented

The system is now reliable, structured, and ready for further extension.