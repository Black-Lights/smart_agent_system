# ================================
# shared/history/__init__.py
# ================================

"""
History Management Module for Smart Agent System

This module provides comprehensive session history tracking, intelligent summarization,
and context management for multi-agent conversations and task execution.

Key Components:
- SessionHistoryManager: Main interface for history management
- HistorySummarizer: AI-powered history summarization using DeepSeek/OpenAI
- HistoryEntry: Data model for individual interactions
- SessionSummary: Data model for session summaries
- HistoryUtils: Utility functions for persistence and formatting

Usage:
    from shared.history import SessionHistoryManager
    
    # Create new session
    history = SessionHistoryManager()
    
    # Log interactions
    history.log_interaction("search for python tutorials", result_dict)
    
    # Get context for next command
    context = history.get_summary_context()
"""

# Core classes
from .manager import SessionHistoryManager, create_session_manager, load_existing_session
from .summarizer import HistorySummarizer, create_summarizer, quick_summarize
from .models import (
    HistoryEntry, 
    SessionSummary, 
    ContextWindow, 
    AgentType, 
    TaskStatus,
    create_history_entry,
    summarize_entries
)
from .utils import (
    HistoryUtils,
    quick_save,
    quick_load,
    format_for_llm
)

# Version info
__version__ = "1.0.0"
__author__ = "Smart Agent System"

# Main exports - these are the primary interfaces users should use
__all__ = [
    # Main manager class
    "SessionHistoryManager",
    
    # Convenience functions
    "create_session_manager",
    "load_existing_session",
    
    # Summarization
    "HistorySummarizer", 
    "create_summarizer",
    "quick_summarize",
    
    # Data models
    "HistoryEntry",
    "SessionSummary", 
    "ContextWindow",
    "AgentType",
    "TaskStatus",
    
    # Utility functions
    "HistoryUtils",
    "create_history_entry",
    "summarize_entries",
    "quick_save",
    "quick_load",
    "format_for_llm"
]

# Convenience functions for common use cases

def start_new_session(auto_save: bool = True) -> SessionHistoryManager:
    """
    Start a new session with history tracking
    
    Args:
        auto_save: Whether to automatically save to disk periodically
        
    Returns:
        New SessionHistoryManager instance
    """
    return SessionHistoryManager(auto_save=auto_save)

def resume_session(session_id: str) -> SessionHistoryManager:
    """
    Resume an existing session by ID
    
    Args:
        session_id: ID of session to resume
        
    Returns:
        SessionHistoryManager with loaded history
    """
    return SessionHistoryManager(session_id=session_id)

def get_available_sessions():
    """Get list of available session files"""
    return HistoryUtils.get_session_list()

def cleanup_old_sessions(days: int = 30):
    """Remove session files older than specified days"""
    return HistoryUtils.cleanup_old_sessions(days)

# Add convenience functions to exports
__all__.extend([
    "start_new_session",
    "resume_session", 
    "get_available_sessions",
    "cleanup_old_sessions"
])

# Module-level configuration
DEFAULT_CONTEXT_LENGTH = 800
DEFAULT_SUMMARY_LENGTH = 400
DEFAULT_RECENT_ENTRIES = 5

def configure_defaults(context_length: int = 800, summary_length: int = 400, recent_entries: int = 5):
    """Configure default settings for the history module"""
    global DEFAULT_CONTEXT_LENGTH, DEFAULT_SUMMARY_LENGTH, DEFAULT_RECENT_ENTRIES
    DEFAULT_CONTEXT_LENGTH = context_length
    DEFAULT_SUMMARY_LENGTH = summary_length  
    DEFAULT_RECENT_ENTRIES = recent_entries

# Example usage documentation
EXAMPLE_USAGE = """
# Basic Usage Example:

from shared.history import SessionHistoryManager

# Start new session
history = SessionHistoryManager()

# Log user interaction
result = {'success': True, 'agent_used': 'browser_agent', 'data': 'Found tutorials'}
history.log_interaction("find Python tutorials", result)

# Get context for next command  
context = history.get_summary_context()
print(context)  # "Recent actions: 1. ✅ find Python tutorials (browser_agent) - success"

# Get intelligent summary using AI
summary = history.get_intelligent_summary()
print(summary)  # AI-generated summary of session

# Save session to disk
history.save_to_disk()

# Get session statistics
stats = history.get_session_statistics()
print(f"Success rate: {stats['success_rate']:.1f}%")
"""

if __name__ == "__main__":
    print(__doc__)
    print(EXAMPLE_USAGE)
