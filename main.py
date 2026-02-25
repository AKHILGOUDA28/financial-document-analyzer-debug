from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
import asyncio
import json
from datetime import datetime

from crewai import Crew, Process
from agents import financial_analyst
from task import analyze_financial_document

app = FastAPI(title="Financial Document Analyzer")

def run_crew(query: str, file_path: str="data/sample.pdf"):
    """To run the whole crew"""
    financial_crew = Crew(
        agents=[financial_analyst],
        tasks=[analyze_financial_document],
        process=Process.sequential,
    )
    
    # FIX (Bug #8): `file_path` was accepted but never passed into kickoff().
    # The crew always read the default sample.pdf, ignoring every uploaded file.
    result = financial_crew.kickoff({
        'query': query,
        'file_path': file_path  # now the uploaded file path properly reaches the agents
    })
    return result

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Financial Document Analyzer API is running"}

@app.post("/analyze")
async def analyze_document(  # FIX (Bug #7): Renamed from `analyze_financial_document` to avoid collision with the imported Task of the same name. The function definition was silently overwriting the import.
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    """Analyze financial document and provide comprehensive investment recommendations"""
    
    file_id = str(uuid.uuid4())
    file_path = f"data/financial_document_{file_id}.pdf"
    
    try:
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Validate query
        if query=="" or query is None:
            query = "Analyze this financial document for investment insights"
            
        # Process the financial document with all analysts
        response = run_crew(query=query.strip(), file_path=file_path)
        
        # FIX (Bug #9): Results were never saved to disk — outputs/ folder was always empty.
        # Now saving each analysis as a timestamped JSON file.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/analysis_{timestamp}.json"
        os.makedirs("outputs", exist_ok=True)

        output_data = {
            "timestamp": timestamp,
            "query": query,
            "file_processed": file.filename,
            "analysis": str(response)
        }
        with open(output_path, "w") as out_f:
            json.dump(output_data, out_f, indent=2)

        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename,
            "output_saved_to": output_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing financial document: {str(e)}")
    
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass  # Ignore cleanup errors

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)