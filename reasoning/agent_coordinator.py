# ================================
# reasoning/agent_coordinator.py
# ================================

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

class AgentType(Enum):
    BROWSER = "browser"
    DESKTOP = "desktop" 
    HYBRID = "hybrid"

class TaskRouter:
    """
    Intelligent task routing between Browser Use and Desktop agents.
    Determines the optimal agent for each task type.
    """
    
    def __init__(self):
        self.browser_keywords = [
            "search", "google", "website", "url", "browse", "internet", "online",
            "shop", "buy", "amazon", "ebay", "compare", "review", "price",
            "email", "gmail", "social", "facebook", "twitter", "linkedin",
            "download", "youtube", "netflix", "stream", "news", "weather",
            "translate", "maps", "directions", "research", "find information"
        ]
        
        self.desktop_keywords = [
            "file", "folder", "document", "save", "copy", "move", "delete",
            "calculator", "calculate", "math", "compute", "terminal", "command",
            "install", "settings", "configuration", "volume", "brightness",
            "screenshot", "capture", "open app", "close app", "text editor",
            "notepad", "music", "video player", "local", "system"
        ]
    
    def classify_task(self, user_command: str) -> Tuple[AgentType, float]:
        """
        Classify user command to determine optimal agent.
        
        Returns:
            (agent_type, confidence_score)
        """
        command_lower = user_command.lower()
        
        # Count keyword matches
        browser_matches = sum(1 for keyword in self.browser_keywords if keyword in command_lower)
        desktop_matches = sum(1 for keyword in self.desktop_keywords if keyword in command_lower)
        
        # Special case detection
        if any(indicator in command_lower for indicator in ["http://", "https://", "www.", ".com", ".org"]):
            return AgentType.BROWSER, 0.95
        
        if any(indicator in command_lower for indicator in ["sudo", "apt", "pip install", "cd ", "ls ", "mkdir"]):
            return AgentType.DESKTOP, 0.95
        
        # Hybrid task detection
        hybrid_indicators = ["download and save", "research and create", "find and organize", "scrape and file"]
        if any(indicator in command_lower for indicator in hybrid_indicators):
            return AgentType.HYBRID, 0.90
        
        # Score-based classification
        total_matches = browser_matches + desktop_matches
        
        if total_matches == 0:
            return AgentType.DESKTOP, 0.50  # Default to desktop for ambiguous tasks
        
        browser_score = browser_matches / total_matches
        desktop_score = desktop_matches / total_matches
        
        if browser_score > 0.6:
            return AgentType.BROWSER, browser_score
        elif desktop_score > 0.6:
            return AgentType.DESKTOP, desktop_score
        else:
            return AgentType.HYBRID, max(browser_score, desktop_score)
    
    def should_use_browser_agent(self, user_command: str) -> bool:
        """Quick check if task should use Browser Use"""
        agent_type, confidence = self.classify_task(user_command)
        return agent_type == AgentType.BROWSER and confidence > 0.7

class AgentCoordinator:
    """
    Coordinates between Browser Use and Desktop agents.
    Manages data flow and execution sequencing.
    """
    
    def __init__(self):
        self.router = TaskRouter()
        self.execution_history = []
        self.shared_data = {}
    
    async def execute_coordinated_task(
        self, 
        user_command: str,
        browser_agent=None,
        desktop_agent=None
    ) -> Dict[str, Any]:
        """
        Execute task with appropriate agent coordination.
        
        Args:
            user_command: User's task description
            browser_agent: Browser Use agent instance (optional)
            desktop_agent: Desktop automation agent instance (optional)
            
        Returns:
            Execution result with data from all involved agents
        """
        
        # Classify task
        agent_type, confidence = self.router.classify_task(user_command)
        
        print(f"[Coordinator] Task classified as: {agent_type.value} (confidence: {confidence:.2f})")
        
        if agent_type == AgentType.BROWSER:
            return await self._execute_browser_task(user_command, browser_agent)
        elif agent_type == AgentType.DESKTOP:
            return await self._execute_desktop_task(user_command, desktop_agent)
        else:  # HYBRID
            return await self._execute_hybrid_task(user_command, browser_agent, desktop_agent)
    
    async def _execute_browser_task(self, command: str, browser_agent) -> Dict[str, Any]:
        """Execute web-focused task using Browser Use"""
        
        print("[Coordinator] Executing browser task with Browser Use")
        
        if browser_agent is None:
            # Import and create Browser Use agent
            try:
                from browser_use import Agent, ChatOpenAI
                
                browser_agent = Agent(
                    task=command,
                    llm=ChatOpenAI(model="gpt-4o-mini"),  # Cost-optimized model
                )
                
                result = await browser_agent.run()
                
                return {
                    "success": True,
                    "agent_used": "browser_use", 
                    "result": result,
                    "data": self._extract_browser_data(result)
                }
                
            except Exception as e:
                print(f"[Browser Agent Error] {e}")
                return {"success": False, "error": str(e), "agent_used": "browser_use"}
        
        # Use provided browser agent
        result = await browser_agent.run()
        return {
            "success": True,
            "agent_used": "browser_use",
            "result": result,
            "data": self._extract_browser_data(result)
        }
    
    async def _execute_desktop_task(self, command: str, desktop_agent) -> Dict[str, Any]:
        """Execute desktop task using existing PyAutoGUI system"""
        
        print("[Coordinator] Executing desktop task with PyAutoGUI system")
        
        if desktop_agent is None:
            # Use your existing desktop agent
            try:
                # Import your existing agent system
                from agent.agent import DesktopAgent  # Assuming this exists
                
                desktop_agent = DesktopAgent()
                result = desktop_agent.execute_task(command)
                
                return {
                    "success": True,
                    "agent_used": "desktop_automation",
                    "result": result
                }
                
            except Exception as e:
                print(f"[Desktop Agent Error] {e}")
                return {"success": False, "error": str(e), "agent_used": "desktop_automation"}
        
        # Use provided desktop agent
        result = desktop_agent.execute_task(command)
        return {"success": True, "agent_used": "desktop_automation", "result": result}
    
    async def _execute_hybrid_task(self, command: str, browser_agent, desktop_agent) -> Dict[str, Any]:
        """Execute coordinated browser + desktop workflow"""
        
        print("[Coordinator] Executing hybrid browser + desktop workflow")
        
        # Parse hybrid command into phases
        phases = self._parse_hybrid_workflow(command)
        results = []
        
        for phase in phases:
            if phase["agent"] == "browser":
                result = await self._execute_browser_task(phase["task"], browser_agent)
            else:  # desktop
                result = await self._execute_desktop_task(phase["task"], desktop_agent)
            
            results.append(result)
            
            # Store data for next phase
            if result.get("success") and result.get("data"):
                self.shared_data.update(result["data"])
        
        return {
            "success": all(r.get("success", False) for r in results),
            "agent_used": "hybrid_coordination", 
            "results": results,
            "shared_data": self.shared_data
        }
    
    def _parse_hybrid_workflow(self, command: str) -> List[Dict[str, str]]:
        """Parse hybrid command into browser and desktop phases"""
        
        # Simple parsing for common patterns
        command_lower = command.lower()
        
        if "research" in command_lower and "save" in command_lower:
            return [
                {"agent": "browser", "task": f"Research information about: {command}"},
                {"agent": "desktop", "task": "Save research results to local file"}
            ]
        elif "download" in command_lower and "organize" in command_lower:
            return [
                {"agent": "browser", "task": f"Download content: {command}"},
                {"agent": "desktop", "task": "Organize downloaded files"}
            ]
        else:
            # Split roughly in half
            return [
                {"agent": "browser", "task": command},
                {"agent": "desktop", "task": f"Process results from: {command}"}
            ]
    
    def _extract_browser_data(self, browser_result) -> Dict[str, Any]:
        """Extract useful data from Browser Use results"""
        
        # Browser Use returns AgentHistoryList
        try:
            if hasattr(browser_result, 'extracted_content'):
                content = browser_result.extracted_content()
            elif hasattr(browser_result, 'action_results'):
                content = [str(action) for action in browser_result.action_results()]
            else:
                content = str(browser_result)
            
            return {
                "extracted_content": content,
                "urls_visited": getattr(browser_result, 'urls', lambda: [])(),
                "execution_time": getattr(browser_result, 'total_time', 0)
            }
        except:
            return {"raw_result": str(browser_result)}