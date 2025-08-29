import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class MasterAgent:
    """Master Agent with Browser Use integration and history context"""
    
    def __init__(self, history_manager=None):
        self.history_manager = history_manager
        print("Master Agent initialized with history support")
    
    async def execute_task(self, user_command: str, context: str = None) -> Dict[str, Any]:
        print(f"\nMaster Agent Processing: {user_command}")
        
        # Show context if available
        if context and context != "Starting new session.":
            print(f"📖 Using context: {context[:100]}..." if len(context) > 100 else f"📖 Using context: {context}")
        
        try:
            task_analysis = self._analyze_task(user_command, context)
            agent_type = task_analysis.get('agent_type', 'desktop')
            
            print(f"Task Analysis: {agent_type} (confidence: {task_analysis.get('confidence', 0.5):.2f})")
            
            if agent_type == 'browser':
                return await self._execute_browser_task(user_command, context)
            else:
                return await self._execute_desktop_task(user_command, context)
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'command': user_command}
    
    def _analyze_task(self, user_command: str, context: str = None) -> Dict[str, Any]:
        command_lower = user_command.lower()
        
        # Consider context when analyzing task
        if context and context != "Starting new session.":
            # If context mentions recent browser actions, slightly favor browser
            if 'browser_agent' in context and 'desktop_agent' not in context:
                browser_bias = 0.1
            elif 'desktop_agent' in context and 'browser_agent' not in context:
                browser_bias = -0.1
            else:
                browser_bias = 0.0
        else:
            browser_bias = 0.0
        
        browser_keywords = ['search', 'google', 'website', 'browse', 'internet', 'online', 
                          'shop', 'buy', 'research', 'find', 'samsung', 'earphones']
        
        browser_score = sum(1 for kw in browser_keywords if kw in command_lower)
        final_score = browser_score + browser_bias
        
        return {'agent_type': 'browser' if final_score > 0 else 'desktop', 'confidence': 0.8}
    
    async def _execute_browser_task(self, command: str, context: str = None) -> Dict[str, Any]:
        print("Routing to Browser Agent (Browser Use)")
        
        try:
            from browser_use import Agent, ChatOpenAI
            
            if not os.getenv("OPENAI_API_KEY"):
                return {
                    'success': False, 
                    'error': 'OPENAI_API_KEY not found. Please add it to your .env file.',
                    'command': command,
                    'agent_used': 'browser_agent'
                }
            
            print("Using OpenAI API with Browser Use")
            
            # Build enhanced task with context
            enhanced_task = command
            if context and context != "Starting new session.":
                enhanced_task = f"Previous context: {context}\n\nCurrent task: {command}"
                print(f"📋 Enhanced task with context")
            
            agent = Agent(
                task=enhanced_task,
                llm=ChatOpenAI(model="gpt-4o-mini")  # Cost-effective OpenAI model
            )
            
            result = await agent.run()
            
            return {
                'success': True,
                'agent_used': 'browser_use',
                'data': str(result),
                'command': command
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Browser Use error: {e}", 'command': command, 'agent_used': 'browser_agent'}
    
    async def _execute_desktop_task(self, command: str, context: str = None) -> Dict[str, Any]:
        print("Routing to Desktop Agent (PyAutoGUI)")
        
        if context and context != "Starting new session.":
            print(f"📋 Desktop agent considering context: {context[:60]}...")
        
        try:
            import pyautogui
            import time
            
            if 'calculator' in command.lower():
                pyautogui.hotkey('win')
                time.sleep(0.5)
                pyautogui.typewrite('calculator')
                time.sleep(0.5)
                pyautogui.press('enter')
                
                return {'success': True, 'agent_used': 'desktop', 'action': 'opened_calculator', 'command': command}
            else:
                return {'success': False, 'error': 'Desktop task not recognized', 'command': command, 'agent_used': 'desktop'}
                
        except Exception as e:
            return {'success': False, 'error': f"Desktop error: {e}", 'command': command, 'agent_used': 'desktop'}
