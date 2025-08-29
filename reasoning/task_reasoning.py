# ================================
# reasoning/task_reasoning.py
# ================================

import os
import json
import platform
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class TaskReasoner:
    """
    Intelligent task analysis and high-level planning.
    Determines whether tasks need Browser Use or Desktop automation.
    """
    
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") 
        self.use_deepseek = bool(os.getenv("DEEPSEEK_API_KEY"))
        
        if self.use_deepseek:
            self.base_url = "https://api.deepseek.com/v1/chat/completions"
            self.model = "deepseek-chat"
            print("[Task Reasoner] Using DeepSeek API (cost-optimized)")
        else:
            self.base_url = "https://api.openai.com/v1/chat/completions"
            self.model = "gpt-4o"
            print("[Task Reasoner] Using OpenAI GPT-4o API")
    
    def analyze_task(self, user_command: str, os_context: str) -> Dict[str, Any]:
        """
        Analyze user command and determine execution strategy.
        
        Returns:
            {
                "agent_type": "browser" | "desktop" | "hybrid",
                "complexity": "simple" | "medium" | "complex", 
                "estimated_steps": 3-15,
                "required_context": "browser" | "calculator" | "file_manager" | etc,
                "strategy": "High-level execution strategy",
                "reasoning": "Why this classification was chosen"
            }
        """
        
        prompt = f"""Analyze this user command and determine the optimal execution strategy.

USER COMMAND: {user_command}
OS CONTEXT: {os_context}

Classify this task based on these criteria:

AGENT TYPES:
- browser: Web research, online shopping, social media, web forms, cloud services
- desktop: Local apps, file management, system settings, terminal commands, local calculations
- hybrid: Requires both web and desktop operations (download from web + organize locally, etc.)

COMPLEXITY LEVELS:
- simple: 1-3 steps, single application
- medium: 4-8 steps, may need app switching  
- complex: 9+ steps, multiple applications, data processing

CONTEXT REQUIREMENTS:
- browser: Firefox, Chrome, any web browser
- calculator: Calculator app, mathematical operations
- file_manager: Nautilus, file operations, folder navigation
- terminal: Command line operations, system commands
- text_editor: Document creation, text editing
- media_player: Video/audio playback
- system_settings: System configuration, preferences
- desktop: General desktop environment

Return ONLY valid JSON:
{{
  "agent_type": "browser|desktop|hybrid",
  "complexity": "simple|medium|complex",
  "estimated_steps": <number>,
  "required_context": "<context_name>",
  "strategy": "<brief execution strategy>",
  "reasoning": "<why this classification>"
}}"""

        try:
            response = self._call_api([
                {"role": "system", "content": "You are a task classification specialist for desktop automation."},
                {"role": "user", "content": prompt}
            ])
            
            # Parse JSON response
            result = json.loads(response)
            result["success"] = True
            return result
            
        except Exception as e:
            print(f"[Task Reasoner Error] {e}")
            return {
                "agent_type": "desktop", 
                "complexity": "simple",
                "estimated_steps": 3,
                "required_context": "desktop", 
                "strategy": "Fallback to desktop automation",
                "reasoning": f"Error in analysis: {str(e)}",
                "success": False
            }
    
    def get_os_context(self) -> str:
        """Get detailed OS context for better task planning"""
        system = platform.system()
        
        if system == "Linux":
            try:
                # Get Linux distribution
                with open("/etc/os-release", "r") as f:
                    os_info = f.read()
                    if "Ubuntu" in os_info:
                        distro = "Ubuntu Linux"
                    elif "Fedora" in os_info:
                        distro = "Fedora Linux"  
                    elif "Debian" in os_info:
                        distro = "Debian Linux"
                    else:
                        distro = "Linux"
                        
                # Get desktop environment
                desktop = os.environ.get("XDG_CURRENT_DESKTOP", "Unknown")
                
                return f"{distro} with {desktop} desktop environment. Use Linux-specific commands."
                
            except:
                return "Linux system. Use standard Linux commands."
                
        elif system == "Darwin":
            return "macOS system. Use macOS-specific commands."
        elif system == "Windows":  
            return "Windows system. Use Windows-specific commands."
        else:
            return "Unknown OS. Use portable commands."
    
    def _call_api(self, messages: List[Dict[str, str]], max_tokens: int = 800) -> str:
        """Call the configured API (DeepSeek or OpenAI)"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens
        }
        
        response = requests.post(self.base_url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"].strip()
