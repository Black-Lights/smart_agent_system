# ================================
# browser_agent/core/browser_agent.py
# ================================

import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class BrowserAgent:
    """
    Browser Use integration agent for web automation
    Handles research, shopping, form filling, and web interactions
    """
    
    def __init__(self):
        """Initialize Browser Use agent"""
        self.agent_type = "browser"
        self.capabilities = [
            "web_research", "online_shopping", "form_filling", 
            "social_media", "data_extraction", "web_navigation"
        ]
        print("🌐 Browser Agent initialized with Browser Use")
    
    async def execute_task(self, command: str) -> Dict[str, Any]:
        """
        Execute web-based task using Browser Use
        
        Args:
            command: Natural language command for web automation
            
        Returns:
            Execution result with extracted data
        """
        
        print(f"🌐 Browser Agent executing: {command}")
        
        try:
            # Import Browser Use
            from browser_use import Agent, ChatOpenAI
            
            # Get model configuration
            model = os.getenv("BROWSER_LLM_MODEL", "gpt-4o-mini")
            
            # Create Browser Use agent
            browser_agent = Agent(
                task=command,
                llm=ChatOpenAI(model=model),
            )
            
            # Execute the task
            print("🚀 Browser Use agent starting...")
            result = await browser_agent.run()
            
            # Extract meaningful data from result
            extracted_data = self._extract_result_data(result)
            
            return {
                'success': True,
                'agent': 'browser_agent',
                'framework': 'browser_use',
                'command': command,
                'data': extracted_data,
                'raw_result': str(result)
            }
            
        except ImportError as e:
            return {
                'success': False,
                'error': f"Browser Use not installed: {e}",
                'suggestion': "Install with: pip install browser-use",
                'agent': 'browser_agent'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'agent': 'browser_agent',
                'command': command
            }
    
    def _extract_result_data(self, browser_result) -> Dict[str, Any]:
        """Extract useful information from Browser Use result"""
        
        try:
            data = {}
            
            # Extract content if available
            if hasattr(browser_result, 'extracted_content'):
                content = browser_result.extracted_content()
                data['extracted_content'] = content
            
            # Extract URLs if available
            if hasattr(browser_result, 'urls'):
                urls = browser_result.urls()
                data['urls_visited'] = urls
            
            # Extract action history if available
            if hasattr(browser_result, 'action_results'):
                actions = [str(action) for action in browser_result.action_results()]
                data['actions_performed'] = actions
            
            # Extract screenshots if available
            if hasattr(browser_result, 'screenshot_paths'):
                screenshots = browser_result.screenshot_paths()
                data['screenshots'] = screenshots
            
            return data
            
        except Exception as e:
            return {'extraction_error': str(e), 'raw_result': str(browser_result)}