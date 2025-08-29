# ================================
# shared/history/models.py
# ================================

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

class AgentType(Enum):
    """Types of agents that can execute tasks"""
    BROWSER = "browser"
    DESKTOP = "desktop"
    HYBRID = "hybrid"
    MASTER = "master"

class TaskStatus(Enum):
    """Task execution status"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    CANCELLED = "cancelled"

@dataclass
class HistoryEntry:
    """Single interaction entry in session history"""
    
    # Core interaction data
    timestamp: str
    user_command: str
    agent_type: str
    task_status: str
    
    # Execution details
    execution_time: float = 0.0
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Context and metadata
    confidence_score: float = 0.0
    complexity_level: str = "medium"
    steps_executed: int = 0
    
    # Additional context
    os_context: Optional[str] = None
    ui_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryEntry':
        """Create from dictionary"""
        return cls(**data)
    
    def get_summary(self) -> str:
        """Get a concise summary of this entry"""
        status_emoji = "✅" if self.task_status == "success" else "❌"
        return f"{status_emoji} {self.user_command} ({self.agent_type}) - {self.task_status}"

@dataclass
class SessionSummary:
    """Summary of session history for context"""
    
    session_id: str
    start_time: str
    end_time: Optional[str]
    
    # Summary statistics
    total_commands: int
    successful_commands: int
    failed_commands: int
    
    # Agent usage
    browser_tasks: int
    desktop_tasks: int
    hybrid_tasks: int
    
    # Key highlights
    recent_actions: List[str]
    common_patterns: List[str]
    active_contexts: List[str]
    
    # Condensed narrative
    summary_text: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionSummary':
        """Create from dictionary"""
        return cls(**data)
    
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.total_commands == 0:
            return 0.0
        return (self.successful_commands / self.total_commands) * 100

@dataclass
class ContextWindow:
    """Defines what context to include for different scenarios"""
    
    # Context window sizes
    recent_entries: int = 5
    max_summary_length: int = 500
    
    # What to include
    include_errors: bool = True
    include_timing: bool = False
    include_ui_context: bool = False
    
    # Filtering
    agent_types: Optional[List[str]] = None
    min_confidence: float = 0.0
    
    def should_include(self, entry: HistoryEntry) -> bool:
        """Check if entry should be included based on filters"""
        
        # Filter by agent type
        if self.agent_types and entry.agent_type not in self.agent_types:
            return False
        
        # Filter by confidence
        if entry.confidence_score < self.min_confidence:
            return False
        
        # Filter errors if not wanted
        if not self.include_errors and entry.task_status == TaskStatus.FAILURE.value:
            return False
        
        return True

# Utility functions for working with history models

def create_history_entry(
    user_command: str,
    agent_type: str,
    result: Dict[str, Any],
    execution_time: float = 0.0
) -> HistoryEntry:
    """Create a history entry from execution result"""
    
    return HistoryEntry(
        timestamp=datetime.now().isoformat(),
        user_command=user_command,
        agent_type=agent_type,
        task_status=TaskStatus.SUCCESS.value if result.get('success') else TaskStatus.FAILURE.value,
        execution_time=execution_time,
        result_data=result,
        error_message=result.get('error'),
        confidence_score=result.get('confidence', 0.5),
        complexity_level=result.get('complexity', 'medium'),
        steps_executed=result.get('steps_executed', 1)
    )

def summarize_entries(entries: List[HistoryEntry], max_length: int = 300) -> str:
    """Create a brief summary from multiple entries"""
    
    if not entries:
        return "No previous actions in this session."
    
    recent_actions = []
    for entry in entries[-5:]:  # Last 5 actions
        action_summary = f"- {entry.user_command} ({entry.agent_type}): {entry.task_status}"
        recent_actions.append(action_summary)
    
    summary = "Recent actions:\n" + "\n".join(recent_actions)
    
    # Truncate if too long
    if len(summary) > max_length:
        summary = summary[:max_length-3] + "..."
    
    return summary
