"""
Summarize API Endpoint
Handles interview summary generation and PDF creation
"""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict
import sys
import os

# Add src to path for imports  
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai.conversation import ConversationManager
from reports.pdf_generator import PDFGenerator

router = APIRouter()

# Initialize managers
conversation_manager = ConversationManager()
pdf_generator = PDFGenerator()

class SummarizeRequest(BaseModel):
    """Request model for summarize endpoint"""
    conversation_history: List[Dict[str, str]]

class SummarizeResponse(BaseModel):
    """Response model for summarize endpoint (markdown only)"""
    summary_text: str

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_endpoint(request: SummarizeRequest) -> SummarizeResponse:
    """
    Generate markdown summary of the interview
    
    - Receives complete conversation history
    - Returns markdown-formatted summary
    """
    try:
        # Generate the markdown summary
        summary_text = conversation_manager.generate_summary(request.conversation_history)
        
        return SummarizeResponse(summary_text=summary_text)
        
    except Exception as e:
        print(f"❌ Summarize endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )

@router.post("/summarize/pdf")
async def summarize_pdf_endpoint(request: SummarizeRequest) -> Response:
    """
    Generate PDF summary of the interview
    
    - Receives complete conversation history  
    - Returns PDF file directly
    """
    try:
        # Generate the markdown summary
        summary_text = conversation_manager.generate_summary(request.conversation_history)
        
        # Convert to PDF
        pdf_bytes = pdf_generator.generate_pdf(summary_text)
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=occupational_history_summary.pdf"}
        )
        
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )
