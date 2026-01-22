from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
from dotenv import load_dotenv

from services.pdf_service import extract_text_from_pdf
from services.model_service import generate_dcf_model
from services.error_check_service import check_model_errors
from services.chat_service import chat_with_model

load_dotenv()

app = FastAPI(
    title="Excel DCF Assistant API",
    description="Backend API for DCF model generation and analysis",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models
class ErrorCheckRequest(BaseModel):
    modelData: Dict[str, Any]


class ChatRequest(BaseModel):
    message: str
    modelData: Dict[str, Any]
    history: Optional[List[Dict[str, str]]] = []


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/upload-pdf")
async def upload_pdf(pdf: UploadFile = File(...)):
    """
    Upload PDF and generate DCF model data
    """
    try:
        if not pdf.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        print(f"📄 Processing PDF: {pdf.filename}")

        # Read PDF content
        content = await pdf.read()

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(content)

        # Generate DCF model data using LangChain + OpenAI
        model_data = await generate_dcf_model(extracted_text)

        return model_data

    except Exception as e:
        print(f"PDF upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@app.post("/api/check-errors")
async def check_errors(request: ErrorCheckRequest):
    """
    Validate DCF model for errors across sheets
    """
    try:
        if not request.modelData:
            raise HTTPException(status_code=400, detail="No model data provided")

        print("🔍 Checking model for errors...")

        # Run error checks using LangChain
        errors = await check_model_errors(request.modelData)

        return {"errors": errors}

    except Exception as e:
        print(f"Error check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check errors: {str(e)}")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat with the model using LangChain
    """
    try:
        if not request.message or not request.modelData:
            raise HTTPException(status_code=400, detail="Message and model data required")

        print(f"💬 Chat message: {request.message[:50]}...")

        # Generate response using LangChain with model context
        response = await chat_with_model(
            request.message,
            request.modelData,
            request.history
        )

        return {"response": response}

    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat: {str(e)}")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3001))
    print(f"🚀 Backend server starting on http://localhost:{port}")
    print(f"📊 Ready to process DCF models")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
