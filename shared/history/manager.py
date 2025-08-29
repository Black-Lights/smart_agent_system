# ================================
# shared/history/manager.py
# ================================

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import HistoryEntry, SessionSummary, ContextWindow, create_history_entry
from .utils import HistoryUtils, format_for_llm
from .summarizer import HistorySummarizer

class SessionHistoryManager:
    """
    Main manager for session history and context.
    Handles logging, retrieval, persistence, and summarization.
    """
    
    def __init__(self, session_id: Optional[str] = None, auto_save: bool = True):
        """
        Initialize session history manager
        
        Args:
            session_id: Unique session identifier (generated if None)
            auto_save: Whether to automatically save to disk periodically
        """
        
        self.session_id = session_id or self._generate_session_id()
        self.auto_save = auto_save
        self.save_interval = 10  # Save every N entries
        
        # In-memory storage
        self.entries: List[HistoryEntry] = []
        self.session_start_time = datetime.now().isoformat()
        
        # Load existing session if it exists
        if session_id:
            self.entries = HistoryUtils.load_session_history(self.session_id)
        
        # Initialize summarizer
        self.summarizer = HistorySummarizer()
        
        print(f"📖 Session History Manager initialized (ID: {self.session_id})")
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"
    
    def log_interaction(
        self, 
        user_command: str, 
        result: Dict[str, Any],
        agent_type: Optional[str] = None,
        execution_time: float = 0.0
    ) -> None:
        """
        Log a user interaction and agent response
        
        Args:
            user_command: User's input command
            result: Agent execution result
            agent_type: Type of agent used (extracted from result if None)
            execution_time: Time taken for execution in seconds
        """
        
        # Extract agent type from result if not provided
        if agent_type is None:
            agent_type = result.get('agent_used', result.get('agent', 'unknown'))
        
        # Create history entry
        entry = create_history_entry(
            user_command=user_command,
            agent_type=agent_type,
            result=result,
            execution_time=execution_time
        )
        
        # Add to history
        self.entries.append(entry)
        
        # Auto-save if enabled
        if self.auto_save and len(self.entries) % self.save_interval == 0:
            self.save_to_disk()
        
        print(f"📝 Logged interaction: {user_command[:50]}... -> {agent_type} ({entry.task_status})")
    
    def get_recent_entries(self, count: int = 5) -> List[HistoryEntry]:
        """Get the most recent N entries"""
        return self.entries[-count:] if self.entries else []
    
    def get_entries_by_agent(self, agent_type: str) -> List[HistoryEntry]:
        """Get all entries for a specific agent type"""
        return [entry for entry in self.entries if entry.agent_type == agent_type]
    
    def get_successful_entries(self) -> List[HistoryEntry]:
        """Get only successful entries"""
        return [entry for entry in self.entries if entry.task_status == "success"]
    
    def get_failed_entries(self) -> List[HistoryEntry]:
        """Get only failed entries"""
        return [entry for entry in self.entries if entry.task_status == "failure"]
    
    def get_context_window(self, window: ContextWindow) -> List[HistoryEntry]:
        """Get entries based on context window configuration"""
        
        # Get recent entries first
        recent = self.get_recent_entries(window.recent_entries)
        
        # Apply filters
        filtered = [entry for entry in recent if window.should_include(entry)]
        
        return filtered
    
    def get_summary_context(self, max_length: int = 800) -> str:
        """
        Get a formatted summary of recent history for use as context
        
        Args:
            max_length: Maximum length of context string
            
        Returns:
            Formatted context string for LLM prompts
        """
        
        # Get recent entries
        recent_entries = self.get_recent_entries(5)
        
        if not recent_entries:
            return "This is the start of a new session."
        
        # Use utility function to format
        return HistoryUtils.format_history_for_context(recent_entries, max_length)
    
    def get_intelligent_summary(self) -> str:
        """
        Get an AI-generated summary of the session using DeepSeek
        
        Returns:
            Intelligent summary of session history
        """
        
        if not self.entries:
            return "No actions taken in this session yet."
        
        # Use summarizer to create intelligent summary
        return self.summarizer.summarize_session(self.entries)
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get comprehensive session statistics"""
        
        if not self.entries:
            return {
                "total_entries": 0,
                "success_rate": 0.0,
                "agent_usage": {},
                "session_duration": "0 minutes"
            }
        
        # Calculate basic stats
        total = len(self.entries)
        successful = len(self.get_successful_entries())
        failed = len(self.get_failed_entries())
        
        # Agent usage breakdown
        agent_usage = {}
        for entry in self.entries:
            agent_usage[entry.agent_type] = agent_usage.get(entry.agent_type, 0) + 1
        
        # Session duration
        if self.entries:
            start_time = datetime.fromisoformat(self.entries[0].timestamp)
            end_time = datetime.fromisoformat(self.entries[-1].timestamp)
            duration_minutes = (end_time - start_time).total_seconds() / 60
        else:
            duration_minutes = 0
        
        return {
            "session_id": self.session_id,
            "total_entries": total,
            "successful_entries": successful,
            "failed_entries": failed,
            "success_rate": (successful / total) * 100 if total > 0 else 0.0,
            "agent_usage": agent_usage,
            "session_duration_minutes": round(duration_minutes, 2),
            "average_execution_time": sum(e.execution_time for e in self.entries) / total if total > 0 else 0.0
        }
    
    def clear_history(self) -> None:
        """Clear all history entries (but keep session ID)"""
        self.entries.clear()
        print(f"🗑️  Cleared history for session {self.session_id}")
    
    def save_to_disk(self) -> bool:
        """Save current session to disk"""
        return HistoryUtils.save_session_history(self.session_id, self.entries)
    
    def export_summary(self) -> Dict[str, Any]:
        """Export comprehensive session summary"""
        return HistoryUtils.export_session_summary(self.session_id, self.entries)
    
    def search_entries(self, query: str, case_sensitive: bool = False) -> List[HistoryEntry]:
        """Search entries by command text"""
        
        if not case_sensitive:
            query = query.lower()
        
        results = []
        for entry in self.entries:
            command = entry.user_command if case_sensitive else entry.user_command.lower()
            if query in command:
                results.append(entry)
        
        return results
    
    def get_context_for_agent(self, agent_type: str, max_entries: int = 3) -> str:
        """Get context specifically relevant to a particular agent type"""
        
        # Get recent entries for this agent type
        agent_entries = [e for e in self.get_recent_entries(10) if e.agent_type == agent_type][-max_entries:]
        
        if not agent_entries:
            return f"No previous {agent_type} agent actions in this session."
        
        context_parts = [f"Recent {agent_type} agent actions:"]
        
        for i, entry in enumerate(agent_entries, 1):
            status = "✅" if entry.task_status == "success" else "❌"
            context_parts.append(f"{i}. {status} {entry.user_command}")
            
            if entry.error_message and entry.task_status == "failure":
                context_parts.append(f"   Error: {entry.error_message[:100]}...")
        
        return "\n".join(context_parts)
    
    def should_summarize(self, threshold: int = 20) -> bool:
        """Check if history should be summarized (getting too long)"""
        return len(self.entries) >= threshold
    
    def get_condensed_context(self, target_length: int = 500) -> str:
        """
        Get condensed context that fits within target length.
        Uses intelligent summarization if history is too long.
        """
        
        # If history is short, return formatted recent entries
        if len(self.entries) <= 5:
            return self.get_summary_context(target_length)
        
        # If history is long, use intelligent summarization
        if self.should_summarize():
            summary = self.get_intelligent_summary()
            
            # Truncate if still too long
            if len(summary) > target_length:
                summary = summary[:target_length-20] + "\n[...continued]"
            
            return summary
        else:
            return self.get_summary_context(target_length)
    
    def __len__(self) -> int:
        """Return number of entries in history"""
        return len(self.entries)
    
    def __str__(self) -> str:
        """String representation"""
        stats = self.get_session_statistics()
        return (f"SessionHistory(id={self.session_id}, "
                f"entries={stats['total_entries']}, "
                f"success_rate={stats['success_rate']:.1f}%)")

# Convenience functions for quick usage

def create_session_manager(session_id: Optional[str] = None) -> SessionHistoryManager:
    """Create a new session history manager"""
    return SessionHistoryManager(session_id=session_id)

def load_existing_session(session_id: str) -> SessionHistoryManager:
    """Load an existing session by ID"""
    return SessionHistoryManager(session_id=session_id)
