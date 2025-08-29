# ================================
# reasoning/coordination/task_router.py
# ================================

import os
import re
from typing import Dict, Any, Tuple
from enum import Enum

class AgentType(Enum):
    BROWSER = "browser"
    DESKTOP = "desktop"
    HYBRID = "hybrid"

class TaskRouter:
    """
    Intelligent task routing between Browser Use and Desktop agents
    Uses keyword analysis and pattern matching for classification
    """
    
    def __init__(self):
        """Initialize task router with classification rules"""
        
        # Browser task indicators
        self.browser_keywords = [
            'search', 'google', 'website', 'url', 'browse', 'internet', 'online',
            'shop', 'buy', 'amazon', 'ebay', 'compare', 'review', 'price',
            'email', 'gmail', 'social', 'facebook', 'twitter', 'linkedin',
            'download', 'youtube', 'netflix', 'stream', 'news', 'weather',
            'translate', 'maps', 'directions', 'research', 'find', 'samsung',
            'earphones', 'headphones', 'product', 'reviews', 'specifications',
            'web', 'site', 'page', 'link', 'http', 'https', 'www'
        ]
        
        # Desktop task indicators
        self.desktop_keywords = [
            'calculator', 'calculate', 'compute', 'math', 'file', 'folder',
            'document', 'save', 'copy', 'move', 'delete', 'open app',
            'close app', 'terminal', 'command', 'install', 'settings',
            'configuration', 'volume', 'brightness', 'wifi', 'network',
            'display', 'screenshot', 'capture', 'local', 'system',
            'notepad', 'text editor', 'music player', 'video player'
        ]
        
        # Hybrid task indicators
        self.hybrid_keywords = [
            'download and save', 'research and create', 'find and organize',
            'scrape and file', 'search and save', 'browse and download',
            'research and document', 'find and store', 'collect and organize'
        ]
        
        print("🎯 Task Router initialized")
    
    async def classify_task(self, user_command: str) -> Dict[str, Any]:
        """
        Classify user command to determine optimal agent routing
        
        Args:
            user_command: Natural language command from user
            
        Returns:
            Classification result with agent type and confidence
        """
        
        command_lower = user_command.lower()
        
        # Check for explicit URLs or web indicators
        if self._has_web_indicators(command_lower):
            return {
                'agent_type': 'browser',
                'confidence': 0.95,
                'reasoning': 'Contains explicit web indicators (URL, domain, etc.)',
                'classification_method': 'explicit_web'
            }
        
        # Check for explicit system commands
        if self._has_system_indicators(command_lower):
            return {
                'agent_type': 'desktop', 
                'confidence': 0.95,
                'reasoning': 'Contains explicit system commands',
                'classification_method': 'explicit_system'
            }
        
        # Check for hybrid task patterns
        hybrid_score = sum(1 for pattern in self.hybrid_keywords if pattern in command_lower)
        if hybrid_score > 0:
            return {
                'agent_type': 'hybrid',
                'confidence': 0.90,
                'reasoning': f'Contains {hybrid_score} hybrid task indicators',
                'classification_method': 'hybrid_pattern'
            }
        
        # Keyword-based scoring
        browser_score = sum(1 for keyword in self.browser_keywords if keyword in command_lower)
        desktop_score = sum(1 for keyword in self.desktop_keywords if keyword in command_lower)
        
        # Calculate confidence and determine agent
        total_score = browser_score + desktop_score
        
        if total_score == 0:
            # Default to desktop for ambiguous commands
            return {
                'agent_type': 'desktop',
                'confidence': 0.50,
                'reasoning': 'No clear indicators found, defaulting to desktop',
                'classification_method': 'default'
            }
        
        if browser_score > desktop_score:
            confidence = browser_score / total_score
            return {
                'agent_type': 'browser',
                'confidence': confidence,
                'reasoning': f'Browser keywords: {browser_score}, Desktop keywords: {desktop_score}',
                'classification_method': 'keyword_scoring',
                'browser_keywords_found': browser_score,
                'desktop_keywords_found': desktop_score
            }
        else:
            confidence = desktop_score / total_score
            return {
                'agent_type': 'desktop',
                'confidence': confidence,
                'reasoning': f'Desktop keywords: {desktop_score}, Browser keywords: {browser_score}',
                'classification_method': 'keyword_scoring',
                'browser_keywords_found': browser_score,
                'desktop_keywords_found': desktop_score
            }
    
    def _has_web_indicators(self, command: str) -> bool:
        """Check for explicit web indicators"""
        web_patterns = [
            r'https?://',  # URLs
            r'www\.',      # www domains
            r'\.com\b', r'\.org\b', r'\.net\b',  # Common TLDs
            r'google\.', r'amazon\.', r'youtube\.',  # Popular sites
        ]
        
        return any(re.search(pattern, command) for pattern in web_patterns)
    
    def _has_system_indicators(self, command: str) -> bool:
        """Check for explicit system command indicators"""
        system_patterns = [
            r'\bsudo\b', r'\bapt\b', r'\bpip install\b',
            r'\bcd\s+', r'\bls\b', r'\bmkdir\b',
            r'\bctrl\+', r'\balt\+', r'\bwin\+'
        ]
        
        return any(re.search(pattern, command) for pattern in system_patterns)