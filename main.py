import os
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document, investment_analysis, risk_assessment, verification
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import database as db_mod

# Load environment variables
load_dotenv()

app = FastAPI(title="Financial Document Analyzer API", version="2.0.0")

# Ensure directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

def run_crew_logic(task_id: str, query: str, file_path: str, filename: str):
    """Background task to run the CrewAI agents."""
    db = next(db_mod.get_db())
    try:
        # Initialize Crew
        financial_crew = Crew(
            agents=[verifier, financial_analyst, investment_advisor, risk_assessor],
            tasks=[verification, analyze_financial_document, investment_analysis, risk_assessment],
            process=Process.sequential,
        )

        # Kickoff with variable inputs
        # FIX (Bug #8): Pass file_path so it reaches the agents
        response = financial_crew.kickoff({
            'query': query,
            'file_path': file_path
        })

        # Save to local file system (Legacy Requirement)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/analysis_{timestamp}.json"
        output_data = {
            "task_id": task_id,
            "timestamp": timestamp,
            "query": query,
            "file_processed": filename,
            "analysis": str(response)
        }
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)

        # Update Database (Bonus Feature)
        db_mod.update_task_result(db, task_id, str(response), output_path, "completed")
        
    except Exception as e:
        print(f"Error in background task: {str(e)}")
        db_mod.update_task_result(db, task_id, f"Error: {str(e)}", "", "failed")

@app.get("/")
def health_check():
    return {"status": "success", "message": "Financial Document Analyzer API (v2.0) is running with Background Workers and Database Integration"}

@app.post("/analyze")
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(db_mod.get_db)
):
    """
    Accepts a PDF, creates a background task, and returns a Task ID.
    (Bonus: Queue Worker Model implementation)
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save uploaded file
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Create task in database
    task_id = db_mod.create_task(db, file.filename, query)

    # Add to background worker queue
    background_tasks.add_task(run_crew_logic, task_id, query, file_path, file.filename)

    return {
        "status": "pending",
        "message": "Analysis started in background",
        "task_id": task_id,
        "file_received": file.filename,
        "check_status_at": f"/status/{task_id}"
    }

@app.get("/status/{task_id}")
def check_status(task_id: str, db: Session = Depends(db_mod.get_db)):
    """
    Checks the status and gets the result of a specific analysis task.
    (Bonus: Database Integration)
    """
    task = db.query(db_mod.AnalysisResult).filter(db_mod.AnalysisResult.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "filename": task.filename,
        "query": task.query,
        "result": task.result if task.status == "completed" else None,
        "output_file": task.output_path,
        "created_at": task.created_at,
        "completed_at": task.completed_at
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)