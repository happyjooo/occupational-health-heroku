"""
LLM Client for Gemini models
Handles interactions with both Google's Gemini API and Vertex AI
"""

from google import genai
import vertexai
from vertexai.generative_models import GenerativeModel
import os
import json
import tempfile
from typing import List, Dict, Optional, Literal
from dotenv import load_dotenv
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

class GeminiClient:
    """Client wrapper for Google Gemini 2.5 Flash API using new google-genai SDK"""
    
    def __init__(self):
        """Initialize the Gemini client"""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Use lazy loading - only create client when needed
        self._client = None
        self.model_name = "gemini-2.5-flash"
        
        print(f"🤖 Gemini client initialized with model: {self.model_name}")
    
    @property
    def client(self):
        """Lazy load the genai client only when needed"""
        if self._client is None:
            print("📡 Creating Gemini API connection...")
            print(f"🔑 DEBUG: API key exists: {bool(self.api_key)}")
            print(f"🔑 DEBUG: API key starts with: {self.api_key[:20] if self.api_key else 'NONE'}...")
            self._client = genai.Client(api_key=self.api_key)
        return self._client
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        role: str = "interviewer"
    ) -> str:
        """
        Generate a response using Gemini with proper conversation context
        
        Args:
            messages: List of conversation messages [{"role": "user|assistant", "content": "..."}]
            system_prompt: Optional system prompt to guide the conversation
            role: Role of the agent generating the response ("interviewer" or "patient")
            
        Returns:
            Generated response text
        """
        try:
            # Build the full conversation context for Gemini
            conversation_text = ""
            
            # Add system prompt if provided
            if system_prompt:
                conversation_text += f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            
            # Add conversation history with clear context
            if messages:
                conversation_text += "CONVERSATION HISTORY:\n"
                for message in messages:
                    role_msg = message["role"]
                    content = message["content"]
                    
                    if role_msg == "user":
                        conversation_text += f"Patient: {content}\n"
                    elif role_msg == "assistant":
                        conversation_text += f"Dr. O: {content}\n"
                
                # Add instruction for next response based on role
                if role == "interviewer":
                    conversation_text += "\nBased on the conversation history above, provide Dr. O's next response to continue the occupational history interview.\n\n"
                    conversation_text += "🧠 USE YOUR EXPERT BRAIN: When patient mentions a job/task, immediately cross-reference with JEM - what specific exposures should you probe for? Ask targeted follow-ups based on their answers, not generic checklist questions.\n"
                    conversation_text += "📋 FORMATTING: Use bullet points for multiple questions. Example: 'Two questions: • What type of dust? • Did you wear masks?'\n"
                    conversation_text += "🎯 RESPONSE LENGTH: Default to under 40 words. Use longer responses ONLY for high-risk exposures (asbestos, silica) or critical medical clarifications.\n"
                    conversation_text += "🔄 CRITICAL: ONE JOB AT A TIME - Complete the current job 100% before moving to the next. NEVER ask about current job AND next job in same response.\n"
                    conversation_text += "❌ NO AUTOMATIC 'THANK YOU': Avoid starting responses with 'Thank you for that information' - be direct and natural.\n"
                    conversation_text += "- Apply principles and JEM logic dynamically to what they just said\n"
                    conversation_text += "- Ask expert-driven questions, not generic 'tell me about your tasks'\n\n"
                    conversation_text += "Dr. O:"
                else:  # patient role
                    conversation_text += "\nBased on the conversation history above, provide the patient's response to Dr. O's question. Respond naturally as the patient character:\n\n"
                    conversation_text += "Patient:"
            else:
                # This is the opening message
                if role == "interviewer":
                    conversation_text += "\nProvide Dr. O's opening message to start the occupational history interview. Keep it CONCISE and welcoming:\n\nDr. O:"
                else:  # patient role
                    conversation_text += "\nProvide the patient's initial response to Dr. O's greeting. Respond naturally as the patient character:\n\nPatient:"
            
            # Debug: Log conversation context before sending to LLM
            print("="*50)
            print("🔍 DEBUG: CONVERSATION SENT TO LLM")
            print(f"📏 Length: {len(conversation_text)} characters")
            print(f"📝 Last 500 chars: ...{conversation_text[-500:]}")
            print("="*50)
            
            # Generate response with concise, structured output
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=conversation_text,
                config=genai.types.GenerateContentConfig(
                    temperature=0.6,  # Balanced for focused but flexible responses
                    max_output_tokens=800,  # Reasonable limit that allows flexibility when needed
                    top_p=0.8,  # Allow some creativity for medical contexts
                    thinking_config=genai.types.ThinkingConfig(thinking_budget=0)  # Disable thinking for speed
                )
            )
            
            # Debug: Log LLM response
            print("🤖 DEBUG: LLM RESPONSE")
            print(f"📤 Response: {response.text[:200]}...")
            print("="*50)
            
            # Post-processing: monitor response length but don't truncate
            response_text = response.text.strip()
            word_count = len(response_text.split())
            
            if word_count > 75:  # Higher threshold - warn but don't truncate
                print(f"⚠️ Long response detected ({word_count} words) - consider if brevity could be improved")
            
            return response_text
            
        except Exception as e:
            print(f"❌ Error generating response: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test if the Gemini API is working"""
        try:
            test_response = self.client.models.generate_content(
                model=self.model_name,
                contents="Say 'Hello, I am Dr. O' if you can hear me."
            )
            print(f"✅ Gemini connection test successful: {test_response.text}")
            return True
        except Exception as e:
            print(f"❌ Gemini connection test failed: {e}")
            return False


class VertexAIClient:
    """Client wrapper for Vertex AI Gemini models"""
    
    def __init__(self, project_id: str = None, location: str = "us-central1", model_name: str = "gemini-2.5-pro"):
        """Initialize the Vertex AI client"""
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.model_name = model_name
        
        # Set up credentials from environment variable
        credentials = self._setup_credentials()
        
        # Initialize Vertex AI with credentials
        vertexai.init(project=self.project_id, location=self.location, credentials=credentials)
        self._model = None
        
        print(f"🤖 Vertex AI client initialized with project: {self.project_id}, model: {self.model_name}")
    
    def _setup_credentials(self):
        """Set up Google Cloud credentials from environment variable"""
        credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        
        if credentials_json:
            print("🔑 Using service account credentials from environment variable")
            try:
                # Parse JSON credentials
                credentials_dict = json.loads(credentials_json)
                
                # Create credentials object
                credentials = service_account.Credentials.from_service_account_info(credentials_dict)
                return credentials
                
            except Exception as e:
                print(f"⚠️ Error parsing service account JSON: {e}")
                return None
        else:
            print("🔑 Using default application credentials")
            return None
    
    @property
    def model(self):
        """Lazy load the Vertex AI model"""
        if self._model is None:
            print("📡 Creating Vertex AI model connection...")
            self._model = GenerativeModel(self.model_name)
        return self._model
    
    def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        role: str = "summary",
        generation_config: Optional[Dict] = None
    ) -> str:
        """
        Generate a response using Vertex AI Gemini with conversation context
        
        Args:
            messages: List of conversation messages [{"role": "user|assistant", "content": "..."}]
            system_prompt: Optional system prompt to guide the conversation
            role: Role type - "summary" for summaries, anything else for interviews
            generation_config: Optional custom generation config (temperature, max_tokens, etc.)
            
        Returns:
            Generated response text
        """
        try:
            # Build the full conversation context for Vertex AI
            conversation_text = ""
            
            # Add system prompt if provided (contains all interview instructions)
            if system_prompt:
                conversation_text += f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            
            # Add conversation history
            if messages:
                conversation_text += "CONVERSATION HISTORY:\n"
                for message in messages:
                    role_msg = message["role"]
                    content = message["content"]
                    
                    if role_msg == "user":
                        conversation_text += f"Patient: {content}\n"
                    elif role_msg == "assistant":
                        conversation_text += f"Dr. O: {content}\n"
                
                # Add instruction based on role
                if role == "summary":
                    conversation_text += "\nPlease generate a comprehensive markdown summary of this occupational history interview."
            else:
                if role == "summary":
                    conversation_text += "\nPlease generate a comprehensive markdown summary."
            
            # Use custom generation config or defaults based on role
            if generation_config is None:
                if role == "summary":
                    # High consistency settings for summaries
                    generation_config = {
                        "temperature": 0.0,
                        "max_output_tokens": 8192,
                        "top_p": 1.0,
                        "top_k": 1
                    }
                else:
                    # Balanced settings for interviews
                    generation_config = {
                        "temperature": 0.6,
                        "max_output_tokens": 800,
                        "top_p": 0.8,
                        "top_k": 40
                    }
            
            # Generate response
            response = self.model.generate_content(
                conversation_text,
                generation_config=generation_config
            )
            
            return response.text.strip()
            
        except Exception as e:
            print(f"❌ Error generating response with Vertex AI: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test if the Vertex AI connection is working"""
        try:
            test_response = self.model.generate_content("Say 'Hello from Vertex AI' if you can hear me.")
            print(f"✅ Vertex AI connection test successful: {test_response.text}")
            return True
        except Exception as e:
            print(f"❌ Vertex AI connection test failed: {e}")
            return False

# Create global client instances
gemini_client = None
vertex_ai_client = None
vertex_ai_flash_client = None

def get_gemini_client() -> GeminiClient:
    """Get or create the global Gemini client instance"""
    global gemini_client
    if gemini_client is None:
        gemini_client = GeminiClient()
    return gemini_client

def get_vertex_ai_client(model_name: str = "gemini-2.5-pro") -> VertexAIClient:
    """Get or create the global Vertex AI client instance"""
    global vertex_ai_client, vertex_ai_flash_client
    
    if model_name == "gemini-2.5-flash":
        if vertex_ai_flash_client is None:
            vertex_ai_flash_client = VertexAIClient(model_name="gemini-2.5-flash")
        return vertex_ai_flash_client
    else:
        if vertex_ai_client is None:
            vertex_ai_client = VertexAIClient(model_name="gemini-2.5-pro")
        return vertex_ai_client

