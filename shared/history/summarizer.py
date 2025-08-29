# ================================
# shared/history/summarizer.py
# ================================

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from .models import HistoryEntry

class HistorySummarizer:
    """
    AI-powered history summarization using DeepSeek or other LLMs.
    Creates intelligent summaries of session history for context.
    """
    
    def __init__(self):
        """Initialize history summarizer"""
        
        # API configuration
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY") 
        self.use_deepseek = bool(self.deepseek_api_key)
        
        # Summarization settings
        self.max_input_entries = 50  # Max entries to send for summarization
        self.target_summary_length = 400  # Target length for summaries
        
        if not (self.deepseek_api_key or self.openai_api_key):
            print("⚠️  Warning: No API keys found for history summarization")
        
        print(f"🤖 History Summarizer initialized ({'DeepSeek' if self.use_deepseek else 'OpenAI'})")
    
    def summarize_session(
        self, 
        entries: List[HistoryEntry], 
        focus: Optional[str] = None
    ) -> str:
        """
        Create an intelligent summary of session history
        
        Args:
            entries: List of history entries to summarize
            focus: Optional focus area (e.g., "browser_tasks", "errors", "recent")
            
        Returns:
            AI-generated summary of the session
        """
        
        if not entries:
            return "No session history to summarize."
        
        # Limit entries to prevent token overflow
        limited_entries = entries[-self.max_input_entries:] if len(entries) > self.max_input_entries else entries
        
        try:
            if self.use_deepseek and self.deepseek_api_key:
                return self._summarize_with_deepseek(limited_entries, focus)
            elif self.openai_api_key:
                return self._summarize_with_openai(limited_entries, focus)
            else:
                return self._create_basic_summary(limited_entries)
                
        except Exception as e:
            print(f"❌ AI summarization failed: {e}")
            return self._create_basic_summary(limited_entries)
    
    def summarize_for_context(
        self, 
        entries: List[HistoryEntry], 
        current_command: str,
        max_tokens: int = 150
    ) -> str:
        """
        Create a context-aware summary for use in LLM prompts
        
        Args:
            entries: History entries
            current_command: Current user command for context
            max_tokens: Maximum tokens for the summary
            
        Returns:
            Focused summary relevant to current command
        """
        
        if not entries:
            return "Starting new session."
        
        # Analyze current command to focus summary
        focus = self._determine_focus(current_command, entries)
        
        try:
            prompt = self._build_context_summary_prompt(entries, current_command, focus, max_tokens)
            
            if self.use_deepseek and self.deepseek_api_key:
                return self._call_deepseek_api(prompt, max_tokens=max_tokens*4)  # Rough token->char conversion
            elif self.openai_api_key:
                return self._call_openai_api(prompt, max_tokens=max_tokens)
            else:
                return self._create_basic_context_summary(entries, current_command)
                
        except Exception as e:
            print(f"❌ Context summarization failed: {e}")
            return self._create_basic_context_summary(entries, current_command)
    
    def _summarize_with_deepseek(self, entries: List[HistoryEntry], focus: Optional[str]) -> str:
        """Create summary using DeepSeek API"""
        
        prompt = self._build_session_summary_prompt(entries, focus)
        return self._call_deepseek_api(prompt, max_tokens=500)
    
    def _summarize_with_openai(self, entries: List[HistoryEntry], focus: Optional[str]) -> str:
        """Create summary using OpenAI API"""
        
        prompt = self._build_session_summary_prompt(entries, focus)
        return self._call_openai_api(prompt, max_tokens=400)
    
    def _build_session_summary_prompt(self, entries: List[HistoryEntry], focus: Optional[str]) -> str:
        """Build prompt for session summarization"""
        
        # Create entries text
        entries_text = []
        for i, entry in enumerate(entries, 1):
            status = "✅ Success" if entry.task_status == "success" else "❌ Failed"
            entries_text.append(
                f"{i}. [{entry.timestamp}] {entry.user_command} "
                f"(Agent: {entry.agent_type}) - {status}"
            )
            
            if entry.error_message and entry.task_status == "failure":
                entries_text.append(f"   Error: {entry.error_message[:100]}...")
        
        focus_instruction = ""
        if focus:
            focus_instruction = f"\nFocus particularly on: {focus}"
        
        prompt = f"""Please create a concise summary of this user session with an AI agent system.

Session History ({len(entries)} actions):
{chr(10).join(entries_text)}

{focus_instruction}

Create a summary that:
1. Highlights the main tasks and goals the user pursued
2. Notes which agents (browser/desktop) were used most
3. Mentions any patterns or workflows
4. Briefly notes major successes and failures
5. Provides context that would help understand what the user is trying to accomplish

Keep the summary to about {self.target_summary_length} characters and write it from the perspective of providing context for the next user action.

Summary:"""
        
        return prompt
    
    def _build_context_summary_prompt(
        self, 
        entries: List[HistoryEntry], 
        current_command: str, 
        focus: str,
        max_tokens: int
    ) -> str:
        """Build prompt for context-aware summarization"""
        
        recent_entries = entries[-5:]  # Last 5 for context
        entries_text = []
        
        for entry in recent_entries:
            status = "✅" if entry.task_status == "success" else "❌"
            entries_text.append(f"{status} {entry.user_command} ({entry.agent_type})")
        
        prompt = f"""Given this recent session history, create a brief context summary for the next command.

Recent History:
{chr(10).join(entries_text)}

Next Command: {current_command}

Create a 2-3 sentence summary that provides relevant context from the history that might help with the next command. Focus on {focus}.

Keep it under {max_tokens} tokens and be concise.

Context Summary:"""
        
        return prompt
    
    def _determine_focus(self, current_command: str, entries: List[HistoryEntry]) -> str:
        """Determine what aspect of history to focus on based on current command"""
        
        command_lower = current_command.lower()
        
        # Browser-related focus
        if any(word in command_lower for word in ['search', 'browse', 'website', 'online', 'find']):
            return "browser actions and search results"
        
        # Desktop-related focus  
        if any(word in command_lower for word in ['calculator', 'file', 'app', 'system', 'desktop']):
            return "desktop actions and system interactions"
        
        # Error-related focus
        if any(word in command_lower for word in ['error', 'failed', 'problem', 'issue']):
            return "previous errors and failed attempts"
        
        # Continuation focus
        if any(word in command_lower for word in ['continue', 'next', 'also', 'then', 'additionally']):
            return "recent successful actions and workflow patterns"
        
        return "overall session progress and context"
    
    def _call_deepseek_api(self, prompt: str, max_tokens: int = 500) -> str:
        """Call DeepSeek API for summarization"""
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.deepseek_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"DeepSeek API error: {response.status_code}")
                return "Summary generation failed."
                
        except Exception as e:
            print(f"DeepSeek API call failed: {e}")
            return "Summary generation failed."
    
    def _call_openai_api(self, prompt: str, max_tokens: int = 400) -> str:
        """Call OpenAI API for summarization"""
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API call failed: {e}")
            return "Summary generation failed."
    
    def _create_basic_summary(self, entries: List[HistoryEntry]) -> str:
        """Create basic summary without AI (fallback)"""
        
        if not entries:
            return "No session activity."
        
        # Calculate basic stats
        total = len(entries)
        successful = sum(1 for e in entries if e.task_status == "success")
        failed = total - successful
        
        # Agent usage
        agent_counts = {}
        for entry in entries:
            agent_counts[entry.agent_type] = agent_counts.get(entry.agent_type, 0) + 1
        
        # Recent actions
        recent_commands = [e.user_command for e in entries[-3:]]
        
        summary_parts = [
            f"Session summary: {total} total actions ({successful} successful, {failed} failed).",
            f"Agent usage: {', '.join(f'{agent}: {count}' for agent, count in agent_counts.items())}.",
            f"Recent actions: {'; '.join(recent_commands)}."
        ]
        
        return " ".join(summary_parts)
    
    def _create_basic_context_summary(self, entries: List[HistoryEntry], current_command: str) -> str:
        """Create basic context summary without AI"""
        
        if not entries:
            return f"Starting new session. About to: {current_command}"
        
        last_entry = entries[-1]
        last_status = "succeeded" if last_entry.task_status == "success" else "failed"
        
        return (f"Last action: '{last_entry.user_command}' {last_status} via {last_entry.agent_type}. "
                f"Now attempting: {current_command}")

# Utility functions

def create_summarizer() -> HistorySummarizer:
    """Create a new history summarizer instance"""
    return HistorySummarizer()

def quick_summarize(entries: List[HistoryEntry]) -> str:
    """Quick summarization with default settings"""
    summarizer = create_summarizer()
    return summarizer.summarize_session(entries)
