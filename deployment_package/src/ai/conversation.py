"""
Conversation Management System
Handles conversation state, prompts, and interview logic
"""

from typing import List, Dict, Optional
from .llm_client import get_gemini_client, get_vertex_ai_client
import os
import json
import re
from datetime import datetime

class ConversationManager:
    """Manages the occupational history interview conversation"""
    
    def __init__(self):
        self.llm_client = get_vertex_ai_client("gemini-2.5-flash")  # For interviews (Gemini 2.5 Flash via Vertex AI)
        self.summary_client = get_vertex_ai_client("gemini-2.5-pro") # For summaries (Gemini 2.5 Pro)
        self.interview_prompt = self._load_interview_prompt()
        self.summary_prompt = self._load_summary_prompt()
        
        # Occupation-based chunking
        self.current_occupation = None
        self.occupation_chunks = {}
        self.conversation_history = []
    
    def _load_interview_prompt(self) -> str:
        """Load the main interview system prompt - prioritize the advanced v3.3 prompt"""
        # Get the absolute path to handle different working directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Prioritize the advanced Dr. O v3.3 system prompt
        advanced_prompt_path = os.path.join(project_root, "multi_agent_prompt", "system_prompt_v2.md")
        if os.path.exists(advanced_prompt_path):
            try:
                with open(advanced_prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Enhance the prompt with production-specific conversation awareness
                    production_enhancement = """

# PRODUCTION CONVERSATION MANAGEMENT
**IMPORTANT FOR REAL PATIENTS:** You are interviewing real patients with potentially complex occupational histories. Be thorough and patient. Complete the interview naturally when you have gathered comprehensive information about all significant occupations and exposures.

**Monitor conversation flow:** If the interview becomes very long, consider whether you have sufficient information for a comprehensive occupational health assessment. Signal completion with ---INTERVIEW_COMPLETE--- when you have covered all major exposure risks thoroughly.
"""
                    return content + production_enhancement
            except FileNotFoundError:
                pass
        
        # Fallback to old prompt if advanced prompt not available
        prompt_path = os.path.join(project_root, "src", "prompts", "interview_prompt.md")
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Interview prompt not found at {prompt_path}")
    
    def _load_summary_prompt(self) -> str:
        """Load the patient-facing summary generation system prompt"""
        # Get the absolute path to handle different working directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Use the simple patient-facing prompt
        prompt_path = os.path.join(project_root, "src", "prompts", "summary_prompt.md")
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Summary prompt not found at {prompt_path}")
    
    def _load_doctor_summary_prompt(self) -> str:
        """Load the doctor-facing detailed analysis prompt"""
        # Get the absolute path to handle different working directories
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # Use the advanced discovery mode prompt for doctors
        advanced_prompt_path = os.path.join(project_root, "multi_agent_prompt", "summary_prompt_v2_discovery.md")
        if os.path.exists(advanced_prompt_path):
            try:
                with open(advanced_prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                pass
        
        # Fallback to simple prompt if advanced not available
        prompt_path = os.path.join(project_root, "src", "prompts", "summary_prompt.md")
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Summary prompt not found at {prompt_path}")
    
    def _detect_occupation_transition(self, message_content: str) -> Optional[str]:
        """
        Detect when Dr. O transitions to a new occupation
        Returns the new occupation name if detected, None otherwise
        """
        # Common transition phrases
        transition_patterns = [
            r"Now, let's talk about the job you had (?:right )?before",
            r"Let's move to your (?:previous|earlier) job",
            r"Now, let's discuss your time",
            r"Let's move on to the job you had",
            r"Now, let's move on to",
            r"Let's talk about your (?:previous|earlier) work"
        ]
        
        for pattern in transition_patterns:
            if re.search(pattern, message_content, re.IGNORECASE):
                # Try to extract occupation name from the message
                # Look for job titles in the patient's response
                return self._extract_occupation_from_context()
        
        return None
    
    def _extract_occupation_from_context(self) -> Optional[str]:
        """
        Extract occupation name from recent conversation context
        """
        # Look at the last few messages to find occupation mentions
        recent_messages = self.conversation_history[-6:]  # Last 6 messages
        
        for message in reversed(recent_messages):
            if message["role"] == "user":  # Patient response
                content = message["content"].lower()
                
                # Common occupation keywords
                occupation_keywords = [
                    "welder", "welding", "construction", "miner", "mining", 
                    "mechanic", "farming", "farmer", "carpenter", "electrician",
                    "plumber", "painter", "machinist", "operator", "supervisor",
                    "foreman", "contractor", "renovation", "demolition"
                ]
                
                for keyword in occupation_keywords:
                    if keyword in content:
                        # Try to get more context
                        words = content.split()
                        for i, word in enumerate(words):
                            if keyword in word:
                                # Get surrounding words for context
                                start = max(0, i-2)
                                end = min(len(words), i+3)
                                context = " ".join(words[start:end])
                                return context.strip()
        
        return None
    
    def _chunk_conversation_by_occupation(self, message_content: str):
        """
        Chunk conversation by occupation transitions
        """
        # Check if this is a transition to a new occupation
        new_occupation = self._detect_occupation_transition(message_content)
        
        if new_occupation and new_occupation != self.current_occupation:
            # Save current occupation chunk
            if self.current_occupation:
                self.occupation_chunks[self.current_occupation] = {
                    "messages": self.conversation_history.copy(),
                    "start_time": datetime.now().isoformat(),
                    "summary": None
                }
                print(f"📋 Chunked conversation for occupation: {self.current_occupation}")
            
            # Start new occupation
            self.current_occupation = new_occupation
            print(f"🔄 Transitioning to new occupation: {new_occupation}")
    
    def start_interview(self) -> Dict[str, str]:
        """Start a new interview conversation"""
        # Reset conversation state
        self.current_occupation = "initial"
        self.occupation_chunks = {}
        self.conversation_history = []
        
        # Generate the opening message from Dr. O
        opening_messages = []
        
        response = self.llm_client.generate_response(
            messages=opening_messages,
            system_prompt=self.interview_prompt
        )
        
        result = {
            "role": "assistant",
            "content": response
        }
        
        # Add to conversation history
        self.conversation_history.append(result)
        
        return result
    
    def continue_interview(self, conversation_history: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Continue the interview conversation
        
        Args:
            conversation_history: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Next response from Dr. O
        """
        # Update internal conversation history
        self.conversation_history = conversation_history.copy()
        
        # Safety is handled by the LLM system prompt - no backend filtering needed
        
        response = self.llm_client.generate_response(
            messages=conversation_history,
            system_prompt=self.interview_prompt
        )
        
        result = {
            "role": "assistant", 
            "content": response
        }
        
        # Check for occupation transitions
        self._chunk_conversation_by_occupation(response)
        
        return result
    
    def generate_occupation_summary(self, occupation_name: str) -> str:
        """
        Generate summary for a specific occupation chunk
        
        Args:
            occupation_name: Name of the occupation to summarize
            
        Returns:
            Markdown-formatted summary for that occupation
        """
        if occupation_name not in self.occupation_chunks:
            return f"## {occupation_name}\nNo conversation data available for this occupation."
        
        chunk_data = self.occupation_chunks[occupation_name]
        messages = chunk_data["messages"]
        
        # Convert conversation to text for summary generation
        conversation_text = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                conversation_text += f"Patient: {content}\n"
            elif role == "assistant" and content != "---INTERVIEW_COMPLETE---":
                conversation_text += f"Dr. O: {content}\n"
        
        # Generate summary using Vertex AI
        summary_messages = [
            {"role": "user", "content": f"Please summarize this conversation about the occupation '{occupation_name}':\n\n{conversation_text}"}
        ]
        
        try:
            summary = self.summary_client.generate_response(
                messages=summary_messages,
                system_prompt=self.summary_prompt,
                role="summary"
            )
            
            # Store the summary
            self.occupation_chunks[occupation_name]["summary"] = summary
            
            return summary
            
        except Exception as e:
            print(f"❌ Error generating summary for {occupation_name}: {e}")
            return f"## {occupation_name}\nError generating summary: {str(e)}"
    
    def generate_comprehensive_summary(self) -> str:
        """
        Generate a comprehensive summary of all occupations
        
        Returns:
            Complete markdown summary with all occupations
        """
        # Ensure current occupation is saved
        if self.current_occupation and self.current_occupation not in self.occupation_chunks:
            self.occupation_chunks[self.current_occupation] = {
                "messages": self.conversation_history.copy(),
                "start_time": datetime.now().isoformat(),
                "summary": None
            }
        
        # Generate summaries for each occupation
        comprehensive_summary = "# OCCUPATIONAL HISTORY SUMMARY REPORT\n\n"
        comprehensive_summary += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        comprehensive_summary += f"**Total Occupations:** {len(self.occupation_chunks)}\n\n"
        
        for occupation_name in self.occupation_chunks.keys():
            if occupation_name != "initial":
                summary = self.generate_occupation_summary(occupation_name)
                comprehensive_summary += f"{summary}\n\n"
        
        return comprehensive_summary
    
    def generate_summary(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate a patient-facing markdown summary of the complete interview
        
        Args:
            conversation_history: Complete conversation
            
        Returns:
            Markdown-formatted summary text for patients
        """
        # Convert conversation to a single text for summary generation
        conversation_text = ""
        for message in conversation_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                conversation_text += f"Patient: {content}\n"
            elif role == "assistant" and content != "---INTERVIEW_COMPLETE---":
                conversation_text += f"Dr. O: {content}\n"
        
        # Generate summary using the patient-facing summary prompt
        summary_messages = [
            {"role": "user", "content": f"Please summarize this interview:\n\n{conversation_text}"}
        ]
        
        summary = self.summary_client.generate_response(
            messages=summary_messages,
            system_prompt=self.summary_prompt,
            role="summary"
        )
        
        return summary
    
    def generate_doctor_summary(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate a doctor-facing detailed analysis of the complete interview
        
        Args:
            conversation_history: Complete conversation
            
        Returns:
            Markdown-formatted detailed analysis for doctors
        """
        # Convert conversation to a single text for summary generation
        conversation_text = ""
        for message in conversation_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                conversation_text += f"Patient: {content}\n"
            elif role == "assistant" and content != "---INTERVIEW_COMPLETE---":
                conversation_text += f"Dr. O: {content}\n"
        
        # Load the doctor-specific prompt
        doctor_prompt = self._load_doctor_summary_prompt()
        
        # Generate summary using the doctor-facing prompt
        summary_messages = [
            {"role": "user", "content": f"Please analyze this interview:\n\n{conversation_text}"}
        ]
        
        summary = self.summary_client.generate_response(
            messages=summary_messages,
            system_prompt=doctor_prompt,
            role="summary"
        )
        
        # 🔍 DEBUG: Print raw LLM output before any processing
        print("="*80)
        print("🔍 RAW LLM OUTPUT (Doctor Summary) - START")
        print("="*80)
        print(summary)
        print("="*80)
        print("🔍 RAW LLM OUTPUT (Doctor Summary) - END")
        print(f"📏 Raw output length: {len(summary)} characters")
        print("="*80)
        
        return summary
    
    def is_interview_complete(self, message_content: str) -> bool:
        """Check if the interview completion signal was sent"""
        return message_content.strip() == "---INTERVIEW_COMPLETE---"
    
    
    def save_occupation_chunks(self, filename: str = "occupation_chunks.json"):
        """
        Save occupation chunks to JSON file for analysis
        
        Args:
            filename: Name of the JSON file to save
        """
        # Convert to serializable format
        serializable_chunks = {}
        for occupation_name, chunk_data in self.occupation_chunks.items():
            serializable_chunks[occupation_name] = {
                "start_time": chunk_data["start_time"],
                "message_count": len(chunk_data["messages"]),
                "summary": chunk_data["summary"],
                "messages": chunk_data["messages"]
            }
        
        with open(filename, 'w') as f:
            json.dump(serializable_chunks, f, indent=2)
        
        print(f"💾 Occupation chunks saved to {filename}")
    
    def get_occupation_stats(self) -> Dict:
        """
        Get statistics about the conversation chunks
        
        Returns:
            Dictionary with occupation statistics
        """
        stats = {
            "total_occupations": len(self.occupation_chunks),
            "current_occupation": self.current_occupation,
            "occupations": {}
        }
        
        for occupation_name, chunk_data in self.occupation_chunks.items():
            stats["occupations"][occupation_name] = {
                "message_count": len(chunk_data["messages"]),
                "has_summary": chunk_data["summary"] is not None,
                "start_time": chunk_data["start_time"]
            }
        
        return stats
