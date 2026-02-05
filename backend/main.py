from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
import json
from dotenv import load_dotenv
import os
from dotenv import load_dotenv

from services.pdf_service import extract_text_from_pdf
from services.model_service import generate_dcf_model
from services.error_check_service import check_model_errors
from services.chat_service import chat_with_model
from services.embedding_service import process_pdf_for_search
from services.session_service import create_session, get_session
from services.summary_service import generate_pdf_summary
from services.action_validator import validate_actions

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
    modelData: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, str]]] = []
    sessionIds: Optional[List[str]] = []
    agentMode: Optional[bool] = False  # True = can write, False = read-only


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
    Upload PDF and store in session for chat context
    """
    try:
        if not pdf.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        print(f"📄 Processing PDF: {pdf.filename}")

        # Read PDF content
        content = await pdf.read()

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(content)

        print(f"📝 Extracted {len(extracted_text)} characters from PDF")

        # Generate embeddings for semantic search
        print("🔮 Generating embeddings for PDF...")
        embeddings_data = process_pdf_for_search(extracted_text)

        # Generate brief summary
        print("📊 Generating summary...")
        summary = await generate_pdf_summary(extracted_text, pdf.filename)
        print(f"📝 Summary: {summary[:80]}...")

        # Create session to store PDF and embeddings
        session_id = create_session(
            pdf_text=extracted_text,
            pdf_data={"summary": summary},  # Include summary in pdf_data
            embeddings_data=embeddings_data
        )

        print(f"✅ PDF uploaded successfully")
        print(f"📊 Created {embeddings_data['chunk_count']} chunks")
        print(f"🔑 Session ID: {session_id[:8]}...")

        return {
            "sessionId": session_id,
            "filename": pdf.filename,
            "chunks": embeddings_data['chunk_count'],
            "characters": len(extracted_text),
            "summary": summary
        }

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
        if not request.message:
            raise HTTPException(status_code=400, detail="Message required")

        print(f"💬 Chat message: {request.message[:50]}...")
        print(f"📊 Model data received: {bool(request.modelData)} (sheets: {list(request.modelData.keys()) if request.modelData else 'none'})")
        print(f"📚 Session IDs: {len(request.sessionIds) if request.sessionIds else 0}")

        # Get PDF context from all sessions if sessionIds provided
        pdf_context = None
        if request.sessionIds and len(request.sessionIds) > 0:
            all_chunks = []
            all_embeddings = []

            for session_id in request.sessionIds:
                session = get_session(session_id)
                if session:
                    all_chunks.extend(session["chunks"])
                    all_embeddings.extend(session["embeddings"])
                    print(f"📄 Added {len(session['chunks'])} chunks from session {session_id[:8]}...")
                else:
                    print(f"⚠️  Session {session_id[:8]}... not found or expired")

            if all_chunks:
                pdf_context = {
                    "chunks": all_chunks,
                    "embeddings": all_embeddings
                }
                print(f"📚 Total PDF context: {len(all_chunks)} chunks from {len(request.sessionIds)} PDF(s)")

        # Generate response using LangChain with optional model context
        response_content = await chat_with_model(
            request.message,
            request.modelData or {},
            request.history,
            pdf_context,
            agent_mode=request.agentMode
        )

        # Parse JSON response from LangChain
        print(f"📝 Raw AI response (first 200 chars): {response_content[:200]}")

        # Strip markdown code blocks if present
        cleaned_response = response_content.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]  # Remove ```
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]  # Remove ```
        cleaned_response = cleaned_response.strip()

        try:
            response_data = json.loads(cleaned_response)

            # Validate actions before sending to frontend
            if response_data.get('actions'):
                print(f"🔍 Validating {len(response_data['actions'])} actions...")
                validated_actions, validation_errors = validate_actions(response_data['actions'])

                if validation_errors:
                    print(f"⚠️  Found {len(validation_errors)} validation errors:")
                    for error in validation_errors:
                        print(f"  - {error}")

                    # Add errors to response
                    error_msg = "\\n".join(validation_errors)
                    response_data['response'] += f"\\n\\n⚠️ Advarsel: Nogle actions blev fjernet pga. dimension fejl:\\n{error_msg}"

                response_data['actions'] = validated_actions
                print(f"✅ Validated: {len(validated_actions)} actions passed, {len(validation_errors)} failed")

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error: {e}")
            print(f"📄 Full response: {response_content}")
            # Fallback if AI doesn't return valid JSON
            response_data = {
                "response": response_content,
                "actions": []
            }

        print(f"🔄 Returning to frontend: response length={len(str(response_data.get('response', '')))}, actions={len(response_data.get('actions', []))}")
        return response_data

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
