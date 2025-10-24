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
                
                # Add simple role marker - let system_prompt handle all instructions
                if role == "interviewer":
                    conversation_text += "\nDr. O:"
                else:  # patient role
                    conversation_text += "\nPatient:"
            else:
                # Opening message - just add role marker
                if role == "interviewer":
                    conversation_text += "\nDr. O:"
                else:  # patient role
                    conversation_text += "\nPatient:"
            
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
                    max_output_tokens=4096,  # Generous limit for detailed responses
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
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        """Initialize the Vertex AI client"""
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location
        self.model_name = "gemini-2.5-pro"
        
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
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response using Vertex AI Gemini with conversation context
        
        Args:
            messages: List of conversation messages [{"role": "user|assistant", "content": "..."}]
            system_prompt: Optional system prompt to guide the conversation
            
        Returns:
            Generated response text
        """
        try:
            # Build the full conversation context for Vertex AI
            conversation_text = ""
            
            # Add system prompt if provided
            if system_prompt:
                conversation_text += f"SYSTEM INSTRUCTIONS:\n{system_prompt}\n\n"
            
            # Add conversation history
            if messages:
                conversation_text += "CONVERSATION HISTORY:\n"
                for message in messages:
                    role = message["role"]
                    content = message["content"]
                    
                    if role == "user":
                        conversation_text += f"Patient: {content}\n"
                    elif role == "assistant":
                        conversation_text += f"Dr. O: {content}\n"
                
                # Add instruction for summary generation
                conversation_text += "\nPlease generate a comprehensive markdown summary of this occupational history interview."
            else:
                conversation_text += "\nPlease generate a comprehensive markdown summary."
            
            # Generate response with highest consistency settings for summaries
            response = self.model.generate_content(
                conversation_text,
                generation_config={
                    "temperature": 0.0,  # Lowest temperature for maximum consistency and determinism
                    "max_output_tokens": 8192,  # Much higher token limit for detailed summaries
                    "top_p": 1.0,  # Most deterministic sampling
                    "top_k": 1  # Most deterministic token selection
                }
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

def get_gemini_client() -> GeminiClient:
    """Get or create the global Gemini client instance"""
    global gemini_client
    if gemini_client is None:
        gemini_client = GeminiClient()
    return gemini_client

def get_vertex_ai_client() -> VertexAIClient:
    """Get or create the global Vertex AI client instance"""
    global vertex_ai_client
    if vertex_ai_client is None:
        vertex_ai_client = VertexAIClient()
    return vertex_ai_client


