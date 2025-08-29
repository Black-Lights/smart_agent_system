# ================================
# shared/history/utils.py
# ================================

import os
import json
import gzip
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from .models import HistoryEntry, SessionSummary

class HistoryUtils:
    """Utility functions for history persistence and management"""
    
    @staticmethod
    def get_history_dir() -> Path:
        """Get the directory for storing history files"""
        history_dir = Path("./history_data")
        history_dir.mkdir(exist_ok=True)
        return history_dir
    
    @staticmethod
    def get_session_filename(session_id: str, compressed: bool = False) -> str:
        """Generate filename for session history"""
        extension = ".json.gz" if compressed else ".json"
        return f"session_{session_id}{extension}"
    
    @staticmethod
    def save_session_history(
        session_id: str, 
        entries: List[HistoryEntry], 
        compress: bool = True
    ) -> bool:
        """Save session history to file"""
        
        try:
            history_dir = HistoryUtils.get_history_dir()
            filename = HistoryUtils.get_session_filename(session_id, compress)
            file_path = history_dir / filename
            
            # Convert entries to dictionaries
            data = {
                "session_id": session_id,
                "saved_at": datetime.now().isoformat(),
                "entries": [entry.to_dict() for entry in entries]
            }
            
            # Save with or without compression
            if compress:
                with gzip.open(file_path, 'wt', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Session history saved: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save session history: {e}")
            return False
    
    @staticmethod
    def load_session_history(session_id: str) -> List[HistoryEntry]:
        """Load session history from file"""
        
        try:
            history_dir = HistoryUtils.get_history_dir()
            
            # Try compressed first, then uncompressed
            for compressed in [True, False]:
                filename = HistoryUtils.get_session_filename(session_id, compressed)
                file_path = history_dir / filename
                
                if not file_path.exists():
                    continue
                
                # Load based on compression
                if compressed:
                    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                
                # Convert back to HistoryEntry objects
                entries = [HistoryEntry.from_dict(entry_data) for entry_data in data.get("entries", [])]
                
                print(f"📖 Loaded {len(entries)} history entries from {file_path}")
                return entries
            
            print(f"📂 No history file found for session: {session_id}")
            return []
            
        except Exception as e:
            print(f"❌ Failed to load session history: {e}")
            return []
    
    @staticmethod
    def cleanup_old_sessions(days_to_keep: int = 30) -> int:
        """Remove history files older than specified days"""
        
        try:
            history_dir = HistoryUtils.get_history_dir()
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            removed_count = 0
            for file_path in history_dir.glob("session_*.json*"):
                file_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_modified < cutoff_date:
                    file_path.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                print(f"🗑️  Cleaned up {removed_count} old session files")
            
            return removed_count
            
        except Exception as e:
            print(f"❌ Failed to cleanup old sessions: {e}")
            return 0
    
    @staticmethod
    def get_session_list() -> List[Dict[str, Any]]:
        """Get list of available session files with metadata"""
        
        try:
            history_dir = HistoryUtils.get_history_dir()
            sessions = []
            
            for file_path in history_dir.glob("session_*.json*"):
                # Extract session ID from filename
                session_id = file_path.stem.replace("session_", "")
                if session_id.endswith(".json"):  # Handle .json.gz case
                    session_id = session_id[:-5]
                
                # Get file stats
                stat = file_path.stat()
                
                sessions.append({
                    "session_id": session_id,
                    "file_path": str(file_path),
                    "size_bytes": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_compressed": file_path.suffix == ".gz"
                })
            
            # Sort by modification time (newest first)
            sessions.sort(key=lambda x: x["modified_at"], reverse=True)
            
            return sessions
            
        except Exception as e:
            print(f"❌ Failed to get session list: {e}")
            return []
    
    @staticmethod
    def export_session_summary(session_id: str, entries: List[HistoryEntry]) -> Dict[str, Any]:
        """Create exportable summary of session"""
        
        if not entries:
            return {"session_id": session_id, "summary": "Empty session"}
        
        # Calculate statistics
        total_commands = len(entries)
        successful = sum(1 for e in entries if e.task_status == "success")
        failed = sum(1 for e in entries if e.task_status == "failure")
        
        # Agent usage
        agent_usage = {}
        for entry in entries:
            agent_usage[entry.agent_type] = agent_usage.get(entry.agent_type, 0) + 1
        
        # Recent commands
        recent_commands = [
            f"{entry.timestamp}: {entry.user_command} ({entry.task_status})"
            for entry in entries[-10:]  # Last 10
        ]
        
        return {
            "session_id": session_id,
            "start_time": entries[0].timestamp if entries else None,
            "end_time": entries[-1].timestamp if entries else None,
            "statistics": {
                "total_commands": total_commands,
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / total_commands) * 100 if total_commands > 0 else 0
            },
            "agent_usage": agent_usage,
            "recent_commands": recent_commands,
            "generated_at": datetime.now().isoformat()
        }
    
    @staticmethod
    def format_history_for_context(entries: List[HistoryEntry], max_length: int = 800) -> str:
        """Format history entries for use as context in LLM prompts"""
        
        if not entries:
            return "No previous actions in this session."
        
        # Build context string
        context_parts = ["Previous session context:"]
        
        for i, entry in enumerate(entries[-5:], 1):  # Last 5 entries
            status_emoji = "✅" if entry.task_status == "success" else "❌"
            part = f"{i}. {status_emoji} {entry.user_command} (via {entry.agent_type})"
            
            if entry.error_message and entry.task_status == "failure":
                part += f" - Error: {entry.error_message[:50]}..."
            
            context_parts.append(part)
        
        context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(context) > max_length:
            context = context[:max_length-20] + "\n[...truncated...]"
        
        return context

# Convenience functions for common operations

def quick_save(session_id: str, entries: List[HistoryEntry]) -> bool:
    """Quick save with default settings"""
    return HistoryUtils.save_session_history(session_id, entries, compress=True)

def quick_load(session_id: str) -> List[HistoryEntry]:
    """Quick load with default settings"""
    return HistoryUtils.load_session_history(session_id)

def format_for_llm(entries: List[HistoryEntry], max_tokens: int = 200) -> str:
    """Format entries for LLM context (rough token estimation)"""
    # Rough estimation: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    return HistoryUtils.format_history_for_context(entries, max_chars)
