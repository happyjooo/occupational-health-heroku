"""
FastAPI Web Application for Occupational History Assistant
Serves the HTML frontend and provides API endpoints for chat functionality
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
import os
import sys
import uuid
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai.conversation import ConversationManager
from reports.pdf_generator import PDFGenerator

app = FastAPI(title="Occupational History Assistant", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
conversation_manager = ConversationManager()
pdf_generator = PDFGenerator()

# Store active sessions with file persistence for Heroku
import json
import tempfile
from pathlib import Path

# Create sessions directory in temp
SESSIONS_DIR = Path(tempfile.gettempdir()) / "heroku_sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

def load_session(session_id: str) -> dict:
    """Load session from file"""
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    if session_file.exists():
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
                # Convert created_at string back to datetime
                if 'created_at' in data:
                    data['created_at'] = datetime.fromisoformat(data['created_at'])
                return data
        except Exception as e:
            print(f"⚠️ Error loading session {session_id}: {e}")
    return None

def save_session(session_id: str, session_data: dict):
    """Save session to file"""
    session_file = SESSIONS_DIR / f"session_{session_id}.json"
    try:
        # Convert datetime to string for JSON serialization
        data_to_save = session_data.copy()
        if 'created_at' in data_to_save:
            data_to_save['created_at'] = data_to_save['created_at'].isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(data_to_save, f, indent=2)
    except Exception as e:
        print(f"⚠️ Error saving session {session_id}: {e}")

# In-memory cache for faster access
sessions = {}

# Email configuration
SMTP_SERVER = "smtp.gmail.com"  # Gmail SMTP server
SMTP_PORT = 587
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "team@monashmed.tech")  # Configure your Gmail
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD", "")  # Set this as environment variable

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    is_complete: bool = False

class SummaryRequest(BaseModel):
    session_id: str
    doctor_name: str
    doctor_clinic: str
    doctor_email: str
    additional_notes: str = ""  # Optional additional notes from patient

# Mount static files
app.mount("/static", StaticFiles(directory="html_version"), name="static")

# Serve static HTML files
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the landing page"""
    return FileResponse('html_version/index.html')

@app.get("/index.html", response_class=HTMLResponse)
async def index_html():
    """Serve the landing page with .html extension"""
    return FileResponse('html_version/index.html')

@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    """Serve the chat interface"""
    return FileResponse('html_version/chat.html')

@app.get("/chat.html", response_class=HTMLResponse)
async def chat_html():
    """Serve the chat interface with .html extension"""
    return FileResponse('html_version/chat.html')

@app.get("/review", response_class=HTMLResponse)
async def review_page():
    """Serve the review page"""
    return FileResponse('html_version/review.html')

@app.get("/review.html", response_class=HTMLResponse)
async def review_html():
    """Serve the review page with .html extension"""
    return FileResponse('html_version/review.html')

@app.get("/success", response_class=HTMLResponse)
async def success_page():
    """Serve the success page"""
    return FileResponse('html_version/success.html')

@app.get("/success.html", response_class=HTMLResponse)
async def success_html():
    """Serve the success page with .html extension"""
    return FileResponse('html_version/success.html')

@app.get("/debug", response_class=HTMLResponse)
async def debug_page():
    """Serve the debug/testing interface"""
    return FileResponse('html_version/debug.html')

@app.get("/debug.html", response_class=HTMLResponse)
async def debug_html():
    """Serve the debug page with .html extension"""
    return FileResponse('html_version/debug.html')

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Handle chat messages and return AI responses
    """
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        # Try to load session from memory first, then from file
        if session_id not in sessions:
            loaded_session = load_session(session_id)
            if loaded_session:
                sessions[session_id] = loaded_session
                print(f"🔄 Restored session {session_id} from file")
        
        if session_id not in sessions:
            # Check if browser sent conversation history as backup
            if request.conversation_history and len(request.conversation_history) > 0:
                print(f"🔄 Session {session_id} lost on server, restoring from browser storage")
                # Restore session from browser history
                sessions[session_id] = {
                    'conversation_history': request.conversation_history,
                    'created_at': datetime.now(),
                    'summary': None
                }
                save_session(session_id, sessions[session_id])
            else:
                # This should only happen for genuinely new sessions
                print(f"⚠️ WARNING: Session {session_id} not found and no browser history provided")
                
                # Return an error instead of silently creating new session
                raise HTTPException(
                    status_code=410, 
                    detail="Session expired or lost. Please refresh the page to start a new conversation."
                )
        
        # Add user message to conversation
        user_message = {"role": "user", "content": request.message}
        sessions[session_id]['conversation_history'].append(user_message)
        
        # Get AI response
        ai_response = conversation_manager.continue_interview(
            sessions[session_id]['conversation_history']
        )
        
        # Check if interview is complete
        is_complete = conversation_manager.is_interview_complete(ai_response['content'])
        
        if not is_complete:
            # Add AI response to conversation if not complete
            sessions[session_id]['conversation_history'].append(ai_response)
        
        # Save session after each interaction
        save_session(session_id, sessions[session_id])
        
        return ChatResponse(
            response=ai_response['content'],
            session_id=session_id,
            is_complete=is_complete
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/summary/{session_id}")
async def get_summary(session_id: str):
    """
    Generate and return summary for a session
    """
    try:
        # Try to load session from memory first, then from file
        if session_id not in sessions:
            loaded_session = load_session(session_id)
            if loaded_session:
                sessions[session_id] = loaded_session
                print(f"🔄 Restored session {session_id} from file for summary")
            else:
                raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate summary if not already done
        if not sessions[session_id].get('summary'):
            conversation_history = sessions[session_id]['conversation_history']
            summary_text = conversation_manager.generate_summary(conversation_history)
            
            # Parse and structure the summary (simplified version)
            sessions[session_id]['summary'] = {
                'raw_text': summary_text,
                'jobs': extract_jobs_from_summary(summary_text),
                'generated_at': datetime.now().isoformat()
            }
        
        return {
            'session_id': session_id,
            'summary': sessions[session_id]['summary'],
            'conversation_length': len(sessions[session_id]['conversation_history'])
        }
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send-summary")
async def send_summary(request: SummaryRequest):
    """
    Send detailed doctor summary to doctor (generate PDF and email)
    """
    try:
        if request.session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = sessions[request.session_id]
        
        if not session_data.get('summary'):
            raise HTTPException(status_code=400, detail="Summary not generated yet")
        
        # Generate doctor-specific summary using the advanced prompt (ALWAYS the same regardless of notes)
        conversation_history = session_data['conversation_history']
        doctor_summary_text = conversation_manager.generate_doctor_summary(conversation_history)
        
        print("🔍 DEBUG: Raw AI output before adding disclaimers:")
        print(f"Length: {len(doctor_summary_text)} characters")
        print(f"Last 200 chars: ...{doctor_summary_text[-200:]}")
        
        # Append additional notes if provided (simple string append - no AI involvement)
        if request.additional_notes and request.additional_notes.strip():
            print("📝 APPENDING ADDITIONAL NOTES TO DOCTOR SUMMARY")
            # Add AI disclaimer before additional notes
            doctor_summary_text += f"\n\n*Note: This summary was generated by an AI assistant. Please review all information for accuracy and completeness.*"
            doctor_summary_text += f"\n\n---\n\n### Additional Notes from Patient\n\nAfter reviewing their summary, the patient provided the following additional information:\n\n{request.additional_notes.strip()}"
            print("✅ Added disclaimer before additional notes")
        else:
            # Add AI disclaimer at the end if no additional notes
            doctor_summary_text += f"\n\n*Note: This summary was generated by an AI assistant. Please review all information for accuracy and completeness.*"
            print("✅ Added disclaimer at end (no additional notes)")
        
        # 🔍 DEBUG: Print final markdown before PDF generation
        print("="*80)
        print("📄 FINAL MARKDOWN SENT TO PDF GENERATOR - START")
        print("="*80)
        print(doctor_summary_text)
        print("="*80)
        print("📄 FINAL MARKDOWN SENT TO PDF GENERATOR - END")
        print(f"📏 Final markdown length: {len(doctor_summary_text)} characters")
        print("="*80)
        
        # Generate PDF with doctor summary (now includes appended notes if any)
        pdf_filename = f"occupational_health_analysis_{request.session_id}_{int(datetime.now().timestamp())}.pdf"
        
        # Create temp directory for PDFs if it doesn't exist
        temp_dir = "temp_pdfs"
        os.makedirs(temp_dir, exist_ok=True)
        pdf_path = os.path.join(temp_dir, pdf_filename)
        
        # Generate PDF
        pdf_bytes = pdf_generator.generate_pdf(doctor_summary_text)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Send email with PDF attachment (if password is set)
        if SMTP_PASSWORD:
            email_sent = send_email_with_pdf(
                recipient_email=request.doctor_email,
                doctor_name=request.doctor_name,
                doctor_clinic=request.doctor_clinic,
                pdf_path=pdf_path
            )
            
            if not email_sent:
                print("⚠️ Email sending failed, but PDF was generated")
            else:
                # Clean up PDF file after successful email send
                try:
                    os.remove(pdf_path)
                    print("🗑️ Temporary PDF file cleaned up")
                except Exception as e:
                    print(f"⚠️ Could not delete temp PDF: {e}")
        else:
            print("⚠️ No email password set - PDF generated but not sent")
            print(f"📄 PDF saved to: {pdf_path}")
            print(f"📧 To enable email: export EMAIL_PASSWORD='your_app_password'")
            print(f"📧 Then restart the server")
            print("⚠️ PDF will remain in temp_pdfs/ until email is configured")
        
        # Store send information
        session_data['sent_to'] = {
            'doctor_name': request.doctor_name,
            'doctor_clinic': request.doctor_clinic,
            'doctor_email': request.doctor_email,
            'pdf_path': pdf_path,
            'sent_at': datetime.now().isoformat()
        }
        
        # After successful email send, clean up session data for privacy
        cleanup_success = False
        try:
            if session_id in sessions:
                del sessions[session_id]
            # Also remove session file
            session_file = SESSIONS_DIR / f"session_{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            print(f"🗑️ Cleaned up session {session_id} after successful email send")
            cleanup_success = True
        except Exception as cleanup_error:
            print(f"⚠️ Error cleaning up session: {cleanup_error}")
        
        return {
            'success': True,
            'message': 'Detailed analysis sent successfully to doctor',
            'doctor_name': request.doctor_name,
            'doctor_clinic': request.doctor_clinic,
            'doctor_email': request.doctor_email,
            'pdf_path': pdf_path,
            'cleanup_completed': cleanup_success
        }
        
    except Exception as e:
        print(f"Error sending summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """
    Get session information
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    return {
        'session_id': session_id,
        'created_at': session_data['created_at'].isoformat(),
        'conversation_length': len(session_data['conversation_history']),
        'has_summary': 'summary' in session_data,
        'sent_to': session_data.get('sent_to')
    }

# DEBUG/TESTING ENDPOINTS - Remove in production
@app.get("/api/debug/session/{session_id}")
async def debug_session(session_id: str):
    """
    Debug endpoint to see what's actually in a session
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    return {
        'session_id': session_id,
        'conversation_length': len(session_data.get('conversation_history', [])),
        'first_user_message': session_data.get('conversation_history', [{}])[1].get('content', 'No messages') if len(session_data.get('conversation_history', [])) > 1 else 'No messages',
        'has_summary': bool(session_data.get('summary')),
        'created_at': session_data.get('created_at'),
        'full_conversation': session_data.get('conversation_history', [])
    }

@app.post("/api/debug/create-test-session")
async def create_test_session():
    """
    Create a test session with sample conversation data for testing summary/PDF generation
    """
    session_id = str(uuid.uuid4())
    
    # Sample conversation data - Eleanor's case (librarian with sarcoidosis)
    test_conversation = [
        {"role": "assistant", "content": "Hello! I'm Dr. O, an AI assistant here to help gather a detailed occupational history. This information is very important for your doctor to understand any work-related factors that might be relevant to your respiratory health. I'll be asking about your jobs, starting with your most recent, and then working backward. We'll discuss what you did, any materials you worked with, and what protective measures were in place. Please take your time, and don't worry if you can't remember every detail. To begin, could you please tell me about your most recent job? What was your job title, what industry was it in, and what years did you work there?"},
        {"role": "user", "content": "I've been working as a librarian at the city library since 1995. I'm still working there now."},
        {"role": "assistant", "content": "What are your main daily tasks as a librarian at the city library?"},
        {"role": "user", "content": "I help patrons find books, check out materials, organize the collections, and I spend quite a bit of time in the basement archive room cataloging older materials."},
        {"role": "assistant", "content": "Tell me about the basement archive room. What are the conditions like down there?"},
        {"role": "user", "content": "Well, it's always had this musty smell that's been there for years. The basement gets damp sometimes, especially after heavy rains. I've worked down there regularly since I started."},
        {"role": "assistant", "content": "That musty smell suggests possible mold growth - a significant concern for respiratory health. Have you noticed any visible signs of dampness, water damage, or discoloration on walls or materials in the basement?"},
        {"role": "user", "content": "Yes, there are some dark spots on the walls in corners, and some of the older books have that musty smell too. The library management knows about it but says it's an old building issue."},
        {"role": "assistant", "content": "That's important information. What job did you have before working at the library? Please include the job title, industry, and dates."},
        {"role": "user", "content": "From 1985 to 1995, I worked at a plant nursery and garden center."},
        {"role": "assistant", "content": "What were your main responsibilities at the plant nursery?"},
        {"role": "user", "content": "I worked with plants and soils, helped customers, and I had to use some sprays to keep the bugs off the flowers. I don't remember the names of the sprays, only that they were strong-smelling."},
        {"role": "assistant", "content": "Those sprays were likely insecticides or pesticides. How often did you use these sprays, and what protective equipment was provided?"},
        {"role": "user", "content": "I used them maybe a few times a week, especially during the growing season. I don't think we had any special protection - maybe just regular gardening gloves sometimes."},
        {"role": "assistant", "content": "What job did you have before the nursery work?"},
        {"role": "user", "content": "From 1980 to 1985, I worked in a small workshop that made metal trinkets and jewelry. I didn't do the metalwork myself - I worked in the office."},
        {"role": "assistant", "content": "Even though you worked in the office, did you ever walk through the workshop area? What was it like there?"},
        {"role": "user", "content": "Yes, I had to walk through the workshop several times a day. There were men grinding and polishing metals. It was a bit dusty, and you could hear the grinding machines running most of the day."},
        {"role": "assistant", "content": "Metal grinding and polishing can produce harmful dust particles. Do you recall what types of metals they were working with, and was there any ventilation or dust control in the workshop?"},
        {"role": "user", "content": "I'm not sure about the specific metals - some were shiny, some looked more dull. The workshop had a few windows but no special ventilation that I remember."},
        {"role": "assistant", "content": "That's very thorough information. Before we finish, is there any other job, part-time work, military service, or hobby involving potential exposures that we haven't covered?"},
        {"role": "user", "content": "No military service. I've always enjoyed reading and gardening at home, but nothing involving chemicals or dust that I can think of."},
        {"role": "assistant", "content": "---INTERVIEW_COMPLETE---"}
    ]
    
    sessions[session_id] = {
        'conversation_history': test_conversation,
        'created_at': datetime.now(),
        'summary': None
    }
    
    return {
        'message': 'Test session created successfully',
        'session_id': session_id,
        'conversation_length': len(test_conversation),
        'next_steps': {
            'test_summary': f'/api/summary/{session_id}',
            'test_review_page': f'/review.html?session={session_id}'
        }
    }

@app.get("/api/debug/doctor-summary-preview/{session_id}")
async def debug_doctor_summary_preview(session_id: str):
    """
    Debug endpoint to preview what conversation data would be sent to AI for doctor summary
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    conversation_history = session_data['conversation_history']
    
    # Convert conversation to text exactly like generate_doctor_summary does
    conversation_text = ""
    for message in conversation_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            conversation_text += f"Patient: {content}\n"
        elif role == "assistant" and content != "---INTERVIEW_COMPLETE---":
            conversation_text += f"Dr. O: {content}\n"
    
    return {
        'session_id': session_id,
        'conversation_text_for_ai': conversation_text,
        'raw_conversation_history': conversation_history
    }

@app.post("/api/debug/load-conversation")
async def load_conversation(conversation_data: dict):
    """
    Load custom conversation data for testing
    Expects: {"conversation": [{"role": "user/assistant", "content": "..."}]}
    """
    session_id = str(uuid.uuid4())
    
    conversation_history = conversation_data.get('conversation', [])
    
    if not conversation_history:
        raise HTTPException(status_code=400, detail="No conversation data provided")
    
    sessions[session_id] = {
        'conversation_history': conversation_history,
        'created_at': datetime.now(),
        'summary': None
    }
    
    return {
        'message': 'Custom conversation loaded successfully',
        'session_id': session_id,
        'conversation_length': len(conversation_history),
        'next_steps': {
            'test_summary': f'/api/summary/{session_id}',
            'test_review_page': f'/review.html?session={session_id}'
        }
    }

def send_email_with_pdf(recipient_email: str, doctor_name: str, doctor_clinic: str, pdf_path: str):
    """
    Send email with PDF attachment to doctor
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = recipient_email
        msg['Subject'] = f"Occupational Health Summary - {doctor_name}"
        
        # Email body
        body = f"""
Dear {doctor_name},

Please find attached the detailed occupational health analysis for your patient.

This report contains:
- Broad Occupational Risk Discovery analysis
- Job-Exposure Matrix assessment
- Detailed respiratory disease risk analysis
- Patient-specific exposure assessments

The analysis was generated using advanced AI occupational medicine protocols.

Best regards,
Occupational Health Assistant System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {os.path.basename(pdf_path)}'
        )
        msg.attach(part)
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, recipient_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def extract_jobs_from_summary(summary_text: str) -> List[Dict]:
    """
    Extract job information from summary text
    This is a simplified parser - you could make this more sophisticated
    """
    # For now, return mock data based on the UI design
    # In production, you'd parse the actual summary text
    jobs = [
        {
            'title': 'Construction Worker',
            'dates': '2015-2018',
            'industry': 'Residential Construction',
            'tasks': [
                'Framing wooden structures for houses',
                'Installing drywall and finishing surfaces', 
                'Basic electrical work and wiring',
                'Site preparation and cleanup'
            ],
            'exposures': ['Wood Dust', 'Crystalline Silica Dust', 'Loud Noise', 'Electrical Hazards']
        }
    ]
    
    # You could implement actual parsing logic here based on your summary format
    return jobs

if __name__ == "__main__":
    print("🏥 Starting Occupational History Assistant Server...")
    print("📱 Frontend will be available at: http://localhost:8000")
    print("🤖 API endpoints available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["./src", "./html_version"]
    )

