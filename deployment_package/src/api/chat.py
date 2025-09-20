"""
Chat API Endpoint
Handles the main interview conversation endpoint
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai.conversation import ConversationManager

router = APIRouter()

# Initialize conversation manager
conversation_manager = ConversationManager()

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    conversation_history: List[Dict[str, str]] = []

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    role: str
    content: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint for conducting the occupational history interview
    
    - Receives conversation history
    - Returns Dr. O's next response
    - Handles both new conversations and ongoing ones
    """
    try:
        # If no conversation history, start a new interview
        if not request.conversation_history:
            response = conversation_manager.start_interview()
        else:
            # Continue existing interview
            response = conversation_manager.continue_interview(request.conversation_history)
        
        return ChatResponse(**response)
        
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/chat/start")
async def start_interview_endpoint() -> ChatResponse:
    """
    Convenience endpoint to start a new interview
    Returns Dr. O's opening message
    """
    try:
        response = conversation_manager.start_interview()
        return ChatResponse(**response)
        
    except Exception as e:
        print(f"❌ Start interview error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting interview: {str(e)}"
        )
